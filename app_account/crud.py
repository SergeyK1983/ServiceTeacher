from sqlalchemy.orm import Session

from .models import User
from .schemas import UserRegister


class UserCrud:

    @staticmethod
    def register_user(db: Session, user: UserRegister) -> User:
        """
        Регистрация (создание) пользователя
        """
        instance = User(**user.dict())
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance


