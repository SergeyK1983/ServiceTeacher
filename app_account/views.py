from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from .auth import Authentication
from .common import UserCommon
from .crud import UserCrud
from .schemas import UserRegister, User

router = APIRouter(tags=["account"])


@router.post("/add_user", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user: UserRegister, db: Session = Depends(get_db)):
    user_inst = UserCommon.get_user_or_none(user.email)
    if user_inst:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь уже существует'
        )

    user.password = Authentication.get_password_hash(user.password)
    instance = UserCrud.register_user(db, user)
    return instance
