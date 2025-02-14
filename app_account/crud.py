from contextlib import contextmanager

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from core.database import SessionLocal
from .models import User, AssignedJWTAccessToken, AssignedJWTRefreshToken
from .schemas import UserRegister, JWTAccessToken, JWTRefreshToken


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
    def _update_insert_session_db(cls, stmt) -> None:
        with cls._get_session_db() as db:
            db.execute(stmt)
            db.commit()
        return None

    @classmethod
    def update_token(
            cls,
            token_model: AssignedJWTAccessToken | AssignedJWTRefreshToken,
            user_verified: User,
            user_device: str
    ) -> None:
        stmt = (
            update(
                token_model
            ).
            where(
                token_model.user_id == user_verified.id,
                token_model.device_id == user_device,
                token_model.is_active
            ).
            values(
                is_active=False
            )
        )
        cls._update_insert_session_db(stmt)
        return

    @classmethod
    def insert_token(
            cls,
            token_model: AssignedJWTAccessToken | AssignedJWTRefreshToken,
            data: JWTAccessToken | JWTRefreshToken
    ) -> None:
        stmt = (
            insert(
                token_model
            ).
            values(
                jti=data.jti,
                is_active=data.is_active,
                expired_time=data.expired_time,
                device_id=data.device_id,
                user_id=data.user_id.id
            )
        )
        cls._update_insert_session_db(stmt)
        return

