from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from .auth import Authentication
from .common import UserCommon
from .crud import UserCrud
from .excepions import UserExceptions
from .schemas import UserRegister, User
from .swagger_schema import AccountSWSchema

router = APIRouter(tags=["account"])


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED, **AccountSWSchema.register_user)
def register_user(user: UserRegister, db: Session = Depends(get_db)) -> User:
    """
    Регистрация пользователя в системе. Если пользователь уже существует, то будет поднято исключение.
    Args:
        user: schema UserRegister
        db: session
    Returns: schema User
    """
    user_inst = UserCommon.get_user_or_none(user.email)
    UserExceptions.exc_user_already_exists(user_inst)

    user.password = Authentication.get_password_hash(user.password)
    instance = UserCrud.register_user(db, user)
    return instance
