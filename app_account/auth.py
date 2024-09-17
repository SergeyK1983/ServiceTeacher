import jwt
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

from core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


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
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encode_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
        return encode_jwt

