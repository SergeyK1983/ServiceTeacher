from uuid import UUID

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from core.database import get_db
from .auth import Authentication
from .common import UserCommon, UserCommonBase
from .crud import UserCrud
from .excepions import UserExceptions
from .schemas import UserRegister, AuthUser, FullUser
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
def login_user(response: Response, user: AuthUser):
    check = UserCommon.authenticate_user(username=user.username, password=user.password)
    UserExceptions.exc_user_unauthorized(check)
    access_token = Authentication.create_access_token({"sub": str(check.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "refresh_token": None}


@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {"massage": "Пользователь успешно вышел из системы"}


@router.get("/all_users", status_code=status.HTTP_200_OK)
def read_all_users(db: Session = Depends(get_db)):
    ucb = UserCommonBase(db)
    users = ucb.show_all_users()
    return users


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK, response_model=FullUser)
def read_all_users(user_id: UUID, db: Session = Depends(get_db)):
    ucb = UserCommonBase(db)
    user = ucb.show_full_user(user_id)
    return user
