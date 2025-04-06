from datetime import datetime, timezone
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status, Response, Request
from sqlalchemy.orm import Session

from core.database import get_db
from .auth import Authentication, is_authenticate, refresh_tokens
from .common import UserCommon, UserCommonBase, TokenCommon
from .crud import UserCRUD
from .excepions import UserExceptions
from .models import User
from .schemas import UserRegisterSchema, AuthUserSchema, FullUserSchema, UserIdSchema, UserSchema, \
    UserPayloadSchema
from .swagger_schema import AccountSWSchema as Swag

router = APIRouter(tags=["account"])


@router.post(path="/register", status_code=status.HTTP_201_CREATED, **Swag.register_user)
def register_user(user: UserRegisterSchema, db: Session = Depends(get_db)) -> dict:
    """
    Регистрация пользователя в системе. Если пользователь уже существует, то будет поднято исключение.
    Args:
        user: schema UserRegister
        db: session
    Returns:
        msg and schema User
    """
    user_instance = UserCommon.get_user_or_none(user.email)
    UserExceptions.exc_user_already_exists(user_instance)

    user.password = Authentication.get_password_hash(user.password)
    instance: User = UserCRUD.register_user(db, user)
    user_sch = UserSchema.model_validate(instance, from_attributes=True)
    return {"msg": "Вы зарегистрированы!", "user": user_sch}


@router.post(path="/login", response_model=UserIdSchema, status_code=status.HTTP_200_OK)
def login_user(response: Response, user: AuthUserSchema) -> User:
    """
    Аутентификация. Устанавливает заголовки "access_token" и "refresh_token" в ответе. Если пользователь не пройдет
    проверку будет вызвано исключение: HTTPException, status.HTTP_401_UNAUTHORIZED.
    Args:
        response: Response
        user: schema AuthUser (from post body)
    Returns:
        schema UserIdSchema and sets the headers "access_token" and "refresh_token"
    """
    user_verified: User | None = UserCommon.authenticate_user(username=user.username, password=user.password)
    UserExceptions.exc_user_unauthorized(user_verified)

    current_time = datetime.now(tz=timezone.utc)
    token_common = TokenCommon(user_verified=user_verified, user=user, current_time=current_time)
    access, refresh = token_common.get_tokens()

    response.headers["access_token"]: str = access
    response.headers["refresh_token"]: str = refresh
    return user_verified


@router.post(path="/update-tokens", dependencies=[Depends(refresh_tokens)])
def refresh_token(request: Request, response: Response) -> dict:
    user_verified: User = request.state.user
    ref_tokens: list = user_verified.refresh_tokens
    current_time = datetime.now(tz=timezone.utc)
    user_schema = UserPayloadSchema(device_id=ref_tokens[0].device_id, not_before=None)
    token_common = TokenCommon(user_verified=user_verified, user=user_schema, current_time=current_time)

    access, refresh = token_common.get_tokens()
    response.headers["access_token"]: str = access
    response.headers["refresh_token"]: str = refresh
    return {"msg": "Токены обновлены"}


@router.post(path="/update-access-token")
def refresh_token(response: Response, user: User = Depends(refresh_tokens)) -> dict:
    response.headers["access_token"]: str = Authentication.create_access_token({"sub": str(user.id)})
    return {"msg": "Токен доступа обновлен"}


@router.post(path="/logout")
def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    return {"massage": "Пользователь успешно вышел из системы"}


@router.delete(path="/delete_user", status_code=status.HTTP_200_OK)
def read_all_users(user: UserSchema, db: Session = Depends(get_db)) -> dict:
    user_instance = UserCommon.get_user_or_none(user.email)
    if not user_instance:
        return {"massage": "Пользователь не найден."}
    UserCRUD.del_user(db, user_instance)
    return {"massage": "Пользователь успешно удалён."}


@router.get(
    path="/all_users",
    dependencies=[Depends(is_authenticate), ],
    status_code=status.HTTP_200_OK,
    response_model=List[FullUserSchema]
)
def read_all_users(db: Session = Depends(get_db)) -> List[dict]:
    users = UserCommonBase(db).show_all_users()
    return users


@router.get(
    path="/user/{user_id}",
    dependencies=[Depends(is_authenticate), ],
    status_code=status.HTTP_200_OK,
    response_model=FullUserSchema
)
def read_full_user(user_id: UUID, db: Session = Depends(get_db)):
    user = UserCommonBase(db).show_full_user(user_id)
    return user
