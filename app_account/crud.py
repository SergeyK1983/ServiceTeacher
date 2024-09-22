from sqlalchemy.orm import Session

from .models import User
from .schemas import UserRegister


class UserCrud:

    @staticmethod
    def register_user(db: Session, user: UserRegister) -> User:
        """
        Регистрация (создание) пользователя
        Args:
            db: session
            user: schema UserRegister
        Returns: instance User
        """
        instance = User(**user.dict())
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance


