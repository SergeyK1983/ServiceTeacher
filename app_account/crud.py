from sqlalchemy.orm import Session

from core.database import SessionLocal
from .models import User, AssignedJWTAccessToken, AssignedJWTRefreshToken
from .schemas import UserRegister, JWTAccessToken, JWTRefreshToken


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


class TokenCRUD:

    @staticmethod
    def save_token(data: dict, flag: bool) -> None:
        session = SessionLocal()
        if flag:
            valid_data = JWTAccessToken.validate(data)
            instance = AssignedJWTAccessToken(**valid_data.model_dump())
        else:
            valid_data = JWTRefreshToken.validate(data)
            instance = AssignedJWTRefreshToken(**valid_data.model_dump())

        session.add(instance)
        session.commit()
        session.refresh(instance)
        session.close()
        return

