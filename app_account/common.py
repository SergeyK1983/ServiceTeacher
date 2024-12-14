from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional

from core.database import SessionLocal
from .models import User
from .auth import Authentication
from .schemas import FullUser, UserId


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


class UserCommonBase:

    def __init__(self, db: Session):
        self.session: Session = db

    def show_all_users(self):
        session = get_session()
        query_ = select(User)
        with session as ses:
            resp = ses.execute(query_)
            result = resp.scalars().all()
            users = [FullUser.model_validate(row, from_attributes=True) for row in result]
        return users

    def show_full_user(self, user_id: UUID):
        resp = self.session.execute(select(User).where(User.id == user_id))
        result = resp.scalars().all()
        user = FullUser.model_validate(result[0])
        return user

    def get_user_by_id(self, user_id: UUID):
        resp = self.session.execute(select(User).where(User.id == user_id))
        result = resp.first()
        user = UserId.model_validate(result[0], from_attributes=True)
        return user

