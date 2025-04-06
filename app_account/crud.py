from contextlib import contextmanager
from typing import Optional
from uuid import UUID

from sqlalchemy import update, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, contains_eager

from core.database import SessionLocal
from .models import User, AssignedJWTAccessToken, AssignedJWTRefreshToken
from .schemas import UserRegisterSchema, AcTokenSchema, ReTokenSchema


class BaseCRUD:

    @classmethod
    @contextmanager
    def _get_session_db(cls):
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()


class UserCRUD(BaseCRUD):

    @staticmethod
    def register_user(db: Session, user: UserRegisterSchema) -> User:
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

    @staticmethod
    def del_user(db: Session, user: User) -> None:
        """
        Удаление пользователя
        Args:
            db: Session from get_db()
            user: instance User model
        """
        db.delete(user)
        db.commit()
        return

    @classmethod
    def get_user_by_jti_token(cls, uuid_jti: UUID, refresh: bool = False) -> Optional[User]:
        """
        Вернет пользователя по идентификатору токена сохраненного в БД, либо ничего.
        Args:
            uuid_jti: token jti from payload
            refresh: refresh or not
        Returns:
            Instance of User or None
        """
        if refresh:
            stmt = (
                select(User).
                join(
                    User.refresh_tokens
                ).
                where(
                    AssignedJWTRefreshToken.jti == uuid_jti,
                    AssignedJWTRefreshToken.is_active == True
                ).
                options(
                    contains_eager(
                        User.refresh_tokens
                    )
                )
            )
        else:
            stmt = (
                select(User).
                join(
                    User.access_tokens
                ).
                where(
                    AssignedJWTAccessToken.jti == uuid_jti,
                    AssignedJWTAccessToken.is_active == True
                ).
                options(
                    contains_eager(
                        User.access_tokens
                    )
                )
            )

        with cls._get_session_db() as db:
            user: User | None = db.execute(stmt).unique().scalar_one_or_none()

        return user


class TokenCRUD(BaseCRUD):

    @classmethod
    def _update_insert_session_db(cls, stmt) -> None:
        with cls._get_session_db() as db:
            db.execute(stmt)
            db.commit()
        return None

    @classmethod
    def deactivate_token(
            cls,
            token_model: AssignedJWTAccessToken | AssignedJWTRefreshToken,
            user_verified: User,
            user_device: str
    ) -> None:
        """
        Обновляет (деактивирует) имеющиеся токены соответствующей модели конкретного пользователя с привязкой к
        устройству пользователя. Значения колонки is_active устанавливаются в False.
        Args:
            token_model: модель токена
            user_verified: Экземпляр пользователя верифицированный
            user_device: str: Устройство пользователя
        Returns:
            None
        """
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
            data: AcTokenSchema | ReTokenSchema
    ) -> None:
        """
        Вставка одной записи в соответствующую таблицу модели токена. Данные для вставки принимаются от соответствующей
        pydentic модели.
        Args:
            token_model: модель токена
            data: данные для наполнения
        Returns:
            None
        """
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

