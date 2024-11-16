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


class AuthExceptions(AccountBaseException):
    @classmethod
    def exc_jwt_decode_error(cls):
        """
        Поднимает исключение 'Ошибка аутентификации'.\n
        raise HTTPException, status.HTTP_403_FORBIDDEN
        """
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Ошибка аутентификации')

    @classmethod
    def exc_authorization_header_not_exist(cls, authorization_header: str | None):
        """
        Поднимает исключение, если отсутствует заголовок authorization.\n
        raise HTTPException, status.HTTP_401_UNAUTHORIZED
        Args:
            authorization_header: Authorization in headers
        """
        if authorization_header is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')

    @classmethod
    def exc_jwt_not_exist(cls, authorization_header: str):
        """
        Поднимает исключение, если в заголовке "authorization" отсутствует JWT префикс.\n
        raise HTTPException, status.HTTP_401_UNAUTHORIZED
        Args:
            authorization_header: Authorization in headers
        """
        if 'JWT ' not in authorization_header:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')

    @classmethod
    def exc_user_not_exist(cls, user: User | None):
        """
        Поднимает исключение, если не передан экземпляр пользователя.\n
        raise HTTPException, status.HTTP_403_FORBIDDEN
        Args:
            user: instance User or None
        """
        if not user:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Ошибка аутентификации')
