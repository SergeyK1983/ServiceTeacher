from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from core.database import get_db
from .auth import Authentication
from .common import UserCommon
from .crud import UserCrud
from .excepions import UserExceptions
from .schemas import UserRegister, User
from .swagger_schema import AccountSWSchema

router = APIRouter(tags=["account"])


@router.post("/register", status_code=status.HTTP_201_CREATED, **AccountSWSchema.register_user)  # response_model=User,
def register_user(user: UserRegister, db: Session = Depends(get_db)) -> dict:
    """
    Регистрация пользователя в системе. Если пользователь уже существует, то будет поднято исключение.
    Args:
        user: schema UserRegister
        db: session
    Returns: schema User
    """
    user_instance = UserCommon.get_user_or_none(user.email)
    UserExceptions.exc_user_already_exists(user_instance)

    user.password = Authentication.get_password_hash(user.password)
    instance = UserCrud.register_user(db, user)
    return {"massage": "Вы успешно зарегистрированы!"}


@router.post("/login")
def login_user():
    pass


@router.post("/logout")
def logout_user():
    pass

