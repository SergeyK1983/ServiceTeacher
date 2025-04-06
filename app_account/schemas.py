from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

from app_account.constants import DEFAULT_USER_DEVICE


class UserSchema(BaseModel):
    username: str = Field(max_length=125, description="Имя пользователя в системе")
    email: EmailStr = Field(max_length=80, description="Электронная почта пользователя")


class UserRegisterSchema(UserSchema):
    password: str = Field(min_length=3, max_length=8, description="Пароль")


class UserIdSchema(UserSchema):
    id: UUID = Field(description="Идентификатор")

    model_config = ConfigDict(
        from_attributes=True,
    )


class FullUserSchema(UserIdSchema):
    first_name: str | None = Field(max_length=125, description="Имя пользователя")
    last_name: str | None = Field(max_length=125, description="Фамилия пользователя")
    created: datetime = Field(description="Дата регистрации")
    updated: datetime = Field(description="Дата изменения")

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserPayloadSchema(BaseModel):
    device_id: str | None = Field(
        default=None, min_length=1, max_length=100, title="Устройство", description="Устройство пользователя"
    )
    not_before: datetime | None = Field(default=None, title="nbf", description="Начало действия токена")

    model_config = ConfigDict(
        from_attributes=True,
    )

    @classmethod
    @field_validator("not_before", mode="before")
    def ensure_timezone(cls, value: datetime) -> datetime:
        if value:
            current_time = datetime.now(tz=timezone.utc)
            if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
                raise ValueError("not_before must include a timezone")
            if value < current_time:
                raise ValueError("not_before must be later than the current date")
        return value


class AuthUserSchema(UserPayloadSchema):
    username: str = Field(description="Имя пользователя")
    password: str = Field(description="Пароль")


class AllUsers(BaseModel):
    users: list[UserSchema] = Field(description="Пользователи системы")

    model_config = ConfigDict(
        from_attributes=True,
    )


class JWTToken(BaseModel):
    jti: UUID = Field(description="Идентификатор токена")
    is_active: bool = Field(default=False, description="Активен")
    expired_time: datetime = Field(alias="exp", description="Окончание доступа")
    device_id: str = Field(default=DEFAULT_USER_DEVICE, description="Устройство пользователя")
    user_id: UserIdSchema = Field(description="id пользователя")


class AcTokenSchema(JWTToken):

    model_config = ConfigDict(
        from_attributes=True,
    )


class ReTokenSchema(JWTToken):

    model_config = ConfigDict(
        from_attributes=True,
    )

