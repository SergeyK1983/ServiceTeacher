import jwt
from uuid import uuid4, UUID
from typing import Any
from datetime import datetime, timezone, timedelta
from enum import Enum
from copy import deepcopy

from fastapi.encoders import jsonable_encoder
from fastapi.security import APIKeyHeader
from passlib.context import CryptContext
from fastapi import Request, Depends

from app_account.crud import UserCRUD
from app_account.excepions import AuthExceptions
from app_account.models import User
from core.config import settings


class TypeToken(Enum):
    ACCESS = APIKeyHeader(name="Authorization")
    REFRESH = APIKeyHeader(name="Refresh_token")

    @classmethod
    def all_names(cls) -> list:
        return cls._member_names_


class Authentication:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    payload_token: dict = dict()

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """
        Хеширование пароля пользователя
        Args:
            password: user password
        Returns:
            hashed password
        """
        return cls.pwd_context.hash(password)

    @classmethod
    def verify_password(cls, input_password: str, hashed_password: str) -> bool:
        """
        Проверка пароля при вводе пароля пользователем
        Args:
            input_password: input password
            hashed_password: hash in database
        Returns:
            True if good
        """
        return cls.pwd_context.verify(input_password, hashed_password)

    @classmethod
    def _create_token(
            cls,
            data: dict,
            current_time: datetime | None,
            ttl: timedelta | None,
            type_t: str = TypeToken.ACCESS.name
    ) -> str:
        """
        Создание JWT токена. По умолчанию создается access токен. По умолчанию время жизни токена указано в
        переменных окружения.
        Args:
            data: data for Payload
            current_time: Current time
            type_t: Access or Refresh of token type
            ttl: timedelta - время жизни токена
        Returns:
            str: jwt token
        """
        if not current_time:
            current_time = datetime.now(tz=timezone.utc)

        if type_t not in TypeToken.all_names():
            AuthExceptions.exc_type_token_error()

        if type_t == TypeToken.ACCESS.name:
            time_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            time_delta = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_HOURS)

        nbf: datetime = data.get("not_before") if data.get("not_before") else current_time
        user_device: str = data.get("user_device") if data.get("user_device") else "no_device"

        to_encode: dict[str, Any] = {
            "sub": str(data.get("user_id").id) + "=" + user_device,  # субъект, которому выдан токен
            "iss": settings.APPLICATION,  # издатель токена
            "exp": nbf + ttl if ttl else nbf + time_delta,  # время, когда токен станет невалидным
            "type": type_t,
            "jti": jsonable_encoder(uuid4()),  # уникальный идентификатор токена
            "iat": current_time,  # время, в которое был выдан токен
            "nbf": nbf,  # время, с которого токен должен считаться действительным
        }
        cls.payload_token = deepcopy(to_encode)
        encode_jwt: str = jwt.encode(payload=to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return "JWT " + encode_jwt

    @classmethod
    def create_access_token(cls, data: dict, current_time: datetime = None, ttl: timedelta = None) -> str:
        return cls._create_token(data=data, current_time=current_time, ttl=ttl)

    @classmethod
    def create_refresh_token(cls, data: dict, current_time: datetime = None, ttl: timedelta = None) -> str:
        return cls._create_token(data=data, current_time=current_time, ttl=ttl, type_t=TypeToken.REFRESH.name)

    @staticmethod
    def __get_payload(token: str) -> dict:
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
        Returns:
            dict: payload
        """
        payload: dict = Authentication.__get_payload(token)
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
        Returns:
            dict: payload
        """
        payload: dict = Authentication.__get_payload(token)
        if payload.get("type") != TypeToken.REFRESH.name:
            AuthExceptions.exc_invalid_token_type()

        return payload


class IsAuthenticate:
    def __init__(self, request: Request, authorization_header: str, refresh: bool = False):
        self.request = request
        self.request.state.user = None
        self.authorization_header = authorization_header
        self.refresh = refresh

    def _check_headers(self) -> None:
        AuthExceptions.exc_authorization_header_not_exist(self.authorization_header)
        AuthExceptions.exc_jwt_not_exist(self.authorization_header)
        return

    def _authenticate(self) -> None:
        """
        Устанавливает пользователя в Request.state или вызывает ошибку: HTTP_403_FORBIDDEN
        Returns:
            None
        """
        clear_token: str = self.authorization_header.replace("JWT ", "")
        payload: dict = Authentication.verify_access_token(clear_token) if not self.refresh else \
            Authentication.verify_refresh_token(clear_token)

        jti = UUID(payload["jti"])
        user: User | None = UserCRUD.get_user_by_jti_token(uuid_jti=jti, refresh=self.refresh)
        AuthExceptions.exc_user_not_exist(user)
        self.request.state.user = user
        return None

    def is_authenticate(self) -> bool:
        """
        Вернет True или вызовет HTTP ошибку.
        """
        self._check_headers()
        self._authenticate()
        return True


def is_authenticate(request: Request, header: str = Depends(TypeToken.ACCESS.value)) -> bool:
    """
    Использовать для апи, в которых нужна аутентификация. Вернет True или вызовет ошибку аутентификации.
    Args:
        request: Request
        header: token in the header (access_token)
    Returns:
        True if token is valid else raises exception
    """
    return IsAuthenticate(request, header).is_authenticate()


def refresh_tokens(request: Request, header: str = Depends(TypeToken.REFRESH.value)) -> bool:
    """
    Предназначено для обновления токенов. В заголовке использовать имя 'Refresh_token'. Соответственно должен быть
    получен refresh токен.
    """
    return IsAuthenticate(request, header, refresh=True).is_authenticate()
