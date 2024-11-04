import jwt
from typing import Optional
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

from app_account.excepions import AuthExceptions
from core.config import settings


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

