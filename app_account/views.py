from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from .auth import Authentication
from .crud import UserCrud
from .schemas import UserRegister, User

router = APIRouter(tags=["account"])


@router.post("/add_user", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    user.password = Authentication.get_password_hash(user.password)
    instance = UserCrud.register_user(db, user)
    return instance
