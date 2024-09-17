from sqlalchemy import select
from typing import Optional

from app_account.models import User
from core.database import SessionLocal


def get_session():
    return SessionLocal()


class UserCommon:

    @staticmethod
    def get_user_or_none(user_email: str) -> Optional[User]:
        """
        Возвращает экземпляр пользователя по его email либо None.
        Args:
            user_email: email of user
        Returns: User or None
        """
        session = get_session()
        query_ = select(User).where(User.email == user_email)
        with session as ses:
            resp = ses.execute(query_)
            instance: Optional[User] = resp.scalar_one_or_none()

        return instance
