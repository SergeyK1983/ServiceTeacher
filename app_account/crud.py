from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .models import User
from .schemas import UserCreate


class UserCrud:

    @staticmethod
    def get_password_hash(password) -> str:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        instance = User(**user.dict())
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance


