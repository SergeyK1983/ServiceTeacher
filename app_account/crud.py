from sqlalchemy.orm import Session

from .models import User
from .schemas import UserCreate


class UserCrud:

    @staticmethod
    def create_user(db: Session, user: UserCreate):
        user_c = User(**user.dict())
        db.add(user_c)
        db.commit()
        db.refresh(user_c)
        return user_c


