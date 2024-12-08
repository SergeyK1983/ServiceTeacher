import jwt
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime, timezone, timedelta
from enum import Enum

from fastapi.encoders import jsonable_encoder
from fastapi.security import APIKeyHeader
from passlib.context import CryptContext
from sqlalchemy import select
from fastapi import Request, Depends

from app_account.excepions import AuthExceptions
from app_account.models import User
from core.config import settings
from core.database import SessionLocal


class TypeToken(Enum):
    ACCESS = APIKeyHeader(name="Authorization")
    REFRESH = APIKeyHeader(name="Refresh_token")

    @classmethod
    def all_names(cls) -> list:
        return cls._member_names_


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
    def create_token(cls, data: dict, type_t: str = TypeToken.ACCESS.name, ttl: timedelta = None) -> str:
        """
        Создание JWT токена. По умолчанию создается access токен. По умолчанию время жизни токена указано в
        переменных окружения.
        Args:
            data: Payload
            type_t: access or refresh token
            ttl: timedelta - время жизни токена
        Returns: jwt token
        """
        current_time = datetime.now(tz=timezone.utc)
        to_encode = data.copy()
        if type_t not in TypeToken.all_names():
            AuthExceptions.exc_type_token_error()

        if type_t == TypeToken.ACCESS.name:
            time_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            time_delta = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)

        if to_encode.get("nbf"):
            exp = to_encode['nbf'] + ttl if ttl else to_encode['nbf'] + time_delta
        else:
            exp = current_time + ttl if ttl else current_time + time_delta

        to_encode.update({
            "iss": "service-teacher",  # издатель токена
            "exp": exp,  # время, когда токен станет невалидным
            "type": type_t,
            "jti": jsonable_encoder(uuid4()),  # уникальный идентификатор токена
            "iat": current_time,  # время, в которое был выдан токен
            "nbf": data['nbf'] if data.get('nbf') else current_time  # время, с которого токен должен считаться действительным
        })
        encode_jwt: str = jwt.encode(payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return "JWT " + encode_jwt

    @classmethod
    def create_access_token(cls, data: dict, ttl: timedelta = None) -> str:
        return cls.create_token(data=data, ttl=ttl)

    @classmethod
    def create_refresh_token(cls, data: dict, ttl: timedelta = None) -> str:
        return cls.create_token(data=data, type_t=TypeToken.REFRESH.name, ttl=ttl)

    @staticmethod
    def __get_payload(token: str) -> dict | None:
        payload = dict()
        try:
            payload: dict = jwt.decode(jwt=token, key=settings.SECRET_KEY, algorithms=settings.ALGORITHM)
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            AuthExceptions.exc_jwt_decode_error()
        return payload

    @classmethod
    def verify_access_token(cls, token: str) -> dict:
        """
        Проверяет действительность access токена. Возвращает полезную нагрузку токена в виде словаря либо вызывает
        ошибку аутентификации.
        Args:
            token: str: token without JWT
        Returns: dict: payload
        """
        payload: dict | None = Authentication.__get_payload(token)
        if payload.get("type") != TypeToken.ACCESS.name:
            AuthExceptions.exc_invalid_token_type()

        return payload

    @classmethod
    def verify_refresh_token(cls, token: str) -> dict:
        """
        Проверяет действительность refresh токена. Возвращает полезную нагрузку токена в виде словаря либо вызывает
        ошибку аутентификации.
        Args:
            token: str: token without JWT
        Returns: dict: payload
        """
        payload: dict | None = Authentication.__get_payload(token)
        if payload.get("type") != TypeToken.REFRESH.name:
            AuthExceptions.exc_invalid_token_type()

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


def is_authenticate(request: Request, header: str = Depends(TypeToken.ACCESS.value)) -> bool:
    """
    Использовать для апи, для которых нужна аутентификация. Вернет True или вызовет ошибку аутентификации.
    Args:
        request:
        header:
    Returns:
    """
    is_auth = IsAuthenticate(request, header).is_authenticate()
    return is_auth


def refresh_tokens(header: str = Depends(TypeToken.REFRESH.value)) -> str:
    """
    Предназначено для обновления токенов. В заголовке использовать имя 'Refresh_token'. Соответственно должен быть
    получен refresh токен.
    """
    return header
