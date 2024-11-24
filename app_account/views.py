from typing import Annotated, List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session

from core.database import get_db
from .auth import Authentication, is_authenticate
from .common import UserCommon, UserCommonBase
from .crud import UserCrud
from .excepions import UserExceptions
from .models import User
from .schemas import UserRegister, AuthUser, FullUser, UserId, User as UserSch
from .swagger_schema import AccountSWSchema as Swag

router = APIRouter(tags=["account"])


@router.post("/register", status_code=status.HTTP_201_CREATED, **Swag.register_user)
def register_user(user: UserRegister, db: Session = Depends(get_db)) -> dict:
    """
    Регистрация пользователя в системе. Если пользователь уже существует, то будет поднято исключение.
    Args:
        user: schema UserRegister
        db: session
    Returns: msg and schema User
    """
    user_instance = UserCommon.get_user_or_none(user.email)
    UserExceptions.exc_user_already_exists(user_instance)

    user.password = Authentication.get_password_hash(user.password)
    instance: User = UserCrud.register_user(db, user)
    user_sch = UserSch.model_validate(instance, from_attributes=True)
    return {"msg": "Вы зарегистрированы!", "user": user_sch}


@router.post("/login", response_model=UserId, status_code=status.HTTP_200_OK)
def login_user(response: Response, user: AuthUser):
    """
    Аутентификация. Устанавливает заголовки "access_token" и "refresh_token" в ответе. Если пользователь не пройдет
    проверку будет вызвано исключение: HTTPException, status.HTTP_401_UNAUTHORIZED.
    Args:
        response: Response
        user: schema AuthUser
    Returns: schema UserId and sets the headers "access_token" and "refresh_token"
    """
    check_user: User | None = UserCommon.authenticate_user(username=user.username, password=user.password)
    UserExceptions.exc_user_unauthorized(check_user)

    access_token: str = Authentication.create_access_token({"sub": str(check_user.id)})
    response.headers["access_token"] = "JWT " + access_token
    response.headers["refresh_token"] = ""
    return check_user


@router.post("/logout")
def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {"massage": "Пользователь успешно вышел из системы"}


@router.get(
    "/all_users",
    dependencies=[Depends(is_authenticate), ],
    status_code=status.HTTP_200_OK,
    response_model=List[FullUser]
)
def read_all_users(db: Session = Depends(get_db)) -> List[dict]:
    users = UserCommonBase(db).show_all_users()
    return users


@router.get(
    "/user/{user_id}",
    dependencies=[Depends(is_authenticate), ],
    status_code=status.HTTP_200_OK,
    response_model=FullUser
)
def read_full_user(user_id: UUID, db: Session = Depends(get_db)):
    user = UserCommonBase(db).show_full_user(user_id)
    return user
