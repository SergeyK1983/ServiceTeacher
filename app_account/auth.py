import jwt
from uuid import UUID
from typing import Optional
from datetime import datetime, timezone, timedelta

from fastapi.security import APIKeyHeader
from passlib.context import CryptContext
from sqlalchemy import select
from fastapi import Request, Depends

from app_account.excepions import AuthExceptions
from app_account.models import User
from core.config import settings
from core.database import SessionLocal


header_scheme = APIKeyHeader(name="Authorization")


class Authentication:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """
        Хеширование пароля пользователя
        Args:
            password: user password
        Returns: hashed password
        """
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, input_password: str, hashed_password: str) -> bool:
        """
        Проверка пароля при вводе пароля пользователем
        Args:
            input_password: input password
            hashed_password: hash in database
        Returns: True if good
        """
        return cls.pwd_context.verify(input_password, hashed_password)

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        """
        Создание JWT токена.
        Args:
            data:
        Returns: jwt token
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
        return encode_jwt

    @classmethod
    def verify_access_token(cls, token: str) -> Optional[dict]:
        payload = dict()
        try:
            payload: dict = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            AuthExceptions.exc_jwt_decode_error()

        return payload


class BaseAuthenticate:

    @staticmethod
    def _session_to_receive_user(query_) -> Optional[User]:
        """
        Возвращает экземпляр пользователя либо None.
        Args:
            query_: select from sqlalchemy
        Returns: instance User model
        """
        session = SessionLocal()
        with session as ses:
            resp = ses.execute(query_)
            instance: Optional[User] = resp.scalar_one_or_none()

        return instance

    def _get_user_by_id_or_none(self, user_id: UUID) -> Optional[User]:
        """
        Возвращает экземпляр пользователя по его id либо None.
        Args:
            user_id: id of the user
        Returns: User or None
        """
        query_ = select(User).where(User.id == user_id)
        user: User = self._session_to_receive_user(query_)
        return user


class IsAuthenticate(BaseAuthenticate):
    def __init__(self, request: Request, authorization_header: str):
        self.request = request
        self.authorization_header = authorization_header

    def _check_headers(self) -> None:
        AuthExceptions.exc_authorization_header_not_exist(self.authorization_header)
        AuthExceptions.exc_jwt_not_exist(self.authorization_header)
        return

    def _authenticate(self) -> None:
        clear_token = self.authorization_header.replace('JWT ', '')
        payload: dict = Authentication.verify_access_token(clear_token)

        user: User | None = self._get_user_by_id_or_none(user_id=payload["sub"])
        AuthExceptions.exc_user_not_exist(user)
        self.request.state.user = user
        return

    def is_authenticate(self) -> bool:
        self._check_headers()
        self._authenticate()
        return True


def is_authenticate(request: Request, header: str = Depends(header_scheme)) -> bool:
    is_auth = IsAuthenticate(request, header).is_authenticate()
    return is_auth

