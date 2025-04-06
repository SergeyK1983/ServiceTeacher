from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional, Any

from core.database import SessionLocal
from .constants import DEFAULT_USER_DEVICE
from .crud import TokenCRUD
from .excepions import AuthExceptions
from .models import User, AssignedJWTAccessToken, AssignedJWTRefreshToken
from .auth import Authentication, TypeToken
from .schemas import FullUserSchema, UserIdSchema, AuthUserSchema, AcTokenSchema, ReTokenSchema


def get_session():
    return SessionLocal()


class UserCommon:

    @classmethod
    def get_user_or_none(cls, user_email: str) -> Optional[User]:
        """
        Возвращает экземпляр пользователя по его email либо None.
        Args:
            user_email: email of user
        Returns:
            User or None
        """
        query_ = select(User).where(User.email == user_email)
        user: User = cls._session_to_receive_user(query_)
        return user

    @classmethod
    def get_user_by_id_or_none(cls, user_id: UUID) -> Optional[User]:
        """
        Возвращает экземпляр пользователя по его id либо None.
        Args:
            user_id: id of the user
        Returns:
            User or None
        """
        query_ = select(User).where(User.id == user_id)
        user: User = cls._session_to_receive_user(query_)
        return user

    @classmethod
    def authenticate_user(cls, username: str, password: str) -> Optional[User]:
        """
        Получает пользователя по переданному username. Если пользователь существует и переданный пароль совпадает,
        то возвращает экземпляр пользователя.
        Args:
            username: input username
            password: input password
        Returns:
            instance User model or None
        """
        query_ = select(User).where(User.username == username)
        user: User = cls._session_to_receive_user(query_)
        if not user or Authentication.verify_password(input_password=password, hashed_password=user.password) is False:
            return None
        return user

    @staticmethod
    def _session_to_receive_user(query_) -> Optional[User]:
        """
        Возвращает экземпляр пользователя либо None.
        Args:
            query_: select from sqlalchemy
        Returns:
            instance User model
        """
        session = get_session()
        with session as ses:
            resp = ses.execute(query_)
            instance: Optional[User] = resp.scalar_one_or_none()

        return instance


class TokenCommon:

    def __init__(
            self,
            user_verified: User,
            user: AuthUserSchema,
            current_time: datetime | None = None,
            ttl: timedelta | None = None  # время жизни токена, если нужно отличное от значения в переменной окружения
    ):
        self.user_verified: User = user_verified
        self.user_schema: AuthUserSchema = user
        self.current_time: datetime | None = current_time
        self.ttl: timedelta | None = ttl

    def _get_token_model(self, token_type: str) -> AssignedJWTAccessToken | AssignedJWTRefreshToken:
        """
        Предоставляет модель токена в зависимости от типа (Access или Refresh), либо вызовет ошибку TypeError.
        Args:
            token_type: str: тип токена
        Returns:
            AssignedJWTAccessToken | AssignedJWTRefreshToken
        """
        token_model = None
        if token_type == TypeToken.ACCESS.name:
            token_model = AssignedJWTAccessToken
        elif token_type == TypeToken.REFRESH.name:
            token_model = AssignedJWTRefreshToken
        return token_model if token_model is not None else AuthExceptions.exc_type_token_error()

    def _deactivate_current_user_tokens(self, payload_token: dict) -> None:
        token_model: AssignedJWTAccessToken | AssignedJWTRefreshToken = self._get_token_model(
            token_type=payload_token["type"]
        )
        user_device: str = self.user_schema.device_id if self.user_schema.device_id else DEFAULT_USER_DEVICE

        TokenCRUD.deactivate_token(token_model, self.user_verified, user_device)
        return

    def _insert_user_token(self, payload_token: dict) -> None:
        token_model = self._get_token_model(token_type=payload_token["type"])
        payload_token.update({"user_id": self.user_verified})

        if self.user_schema.device_id:
            payload_token.update({"device_id": self.user_schema.device_id})

        validator = AcTokenSchema if isinstance(token_model, AssignedJWTAccessToken) else ReTokenSchema
        valid_data = validator.model_validate(payload_token)
        valid_data.is_active = True

        TokenCRUD.insert_token(token_model=token_model, data=valid_data)
        return

    def _deactivate_and_insert(self) -> None:
        payload_token: dict[str, Any] = Authentication.payload_token
        self._deactivate_current_user_tokens(payload_token)
        self._insert_user_token(payload_token)
        return

    def _prepare_data(self) -> dict:
        data = {
            "user_id": self.user_verified,
            "user_device": self.user_schema.device_id,
            "not_before": self.user_schema.not_before,
        }
        return data

    def get_access_token(self) -> str:
        payload_data: dict = self._prepare_data()
        access_token: str = Authentication.create_access_token(
            data=payload_data, current_time=self.current_time, ttl=self.ttl
        )
        self._deactivate_and_insert()
        return access_token

    def get_refresh_token(self) -> str:
        payload_data: dict = self._prepare_data()
        refresh_token: str = Authentication.create_refresh_token(
            data=payload_data, current_time=self.current_time, ttl=self.ttl
        )
        self._deactivate_and_insert()
        return refresh_token

    def get_tokens(self) -> tuple[str, str]:
        access: str = self.get_access_token()
        refresh: str = self.get_refresh_token()
        return access, refresh


class UserCommonBase:

    def __init__(self, db: Session):
        self.session: Session = db  # ожидается сессия от database.py

    def show_all_users(self):
        session = get_session()
        query_ = select(User)
        with session as ses:
            resp = ses.execute(query_)
            result = resp.scalars().all()
            users = [FullUserSchema.model_validate(row, from_attributes=True) for row in result]
        return users

    def show_full_user(self, user_id: UUID):
        resp = self.session.execute(select(User).where(User.id == user_id))
        result = resp.scalars().all()
        user = FullUserSchema.model_validate(result[0])
        return user

    def get_user_by_id(self, user_id: UUID):
        resp = self.session.execute(select(User).where(User.id == user_id))
        result = resp.first()
        user = UserIdSchema.model_validate(result[0], from_attributes=True)
        return user

