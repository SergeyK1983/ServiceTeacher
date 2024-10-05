from fastapi import HTTPException, status

from app_account.models import User


class AccountBaseException(Exception):
    pass


class UserExceptions(AccountBaseException):

    @classmethod
    def exc_user_already_exists(cls, user: User | None):
        """
        Поднимает исключение, если передан экземпляр пользователя.\n
        raise HTTPException, status.HTTP_409_CONFLICT
        Args:
            user: instance User
        """
        if user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь уже существует")

    @classmethod
    def exc_user_unauthorized(cls, user: User | None):
        """
        Поднимает исключение, если не передан экземпляр пользователя.\n
        raise HTTPException, status.HTTP_401_UNAUTHORIZED
        Args:
            user: instance User or None
        """
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверное имя пользователя или пароль')
