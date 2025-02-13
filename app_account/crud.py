from contextlib import contextmanager

from sqlalchemy.orm import Session

from core.database import SessionLocal
from .models import User
from .schemas import UserRegister


class BaseCRUD:

    @classmethod
    @contextmanager
    def _get_session_db(cls):
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()


class UserCrud:

    @staticmethod
    def register_user(db: Session, user: UserRegister) -> User:
        """
        Регистрация (создание) пользователя
        Args:
            db: session
            user: schema UserRegister
        Returns:
            instance User
        """
        instance = User(**user.model_dump())
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance


class TokenCRUD(BaseCRUD):

    @classmethod
    def update_token(cls, stmt) -> None:
        with cls._get_session_db() as db:
            db.execute(stmt)
            db.commit()
        return None

    @classmethod
    def insert_token(cls, stmt) -> None:
        with cls._get_session_db() as db:
            db.execute(stmt)
            db.commit()
        return None

