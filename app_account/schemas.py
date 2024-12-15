from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class User(BaseModel):
    username: str = Field(default=..., max_length=125, description="Имя пользователя в системе")
    email: EmailStr = Field(default=..., max_length=80, description="Электронная почта пользователя")


class UserId(User):
    id: UUID = Field(default=..., description="Идентификатор")

    model_config = ConfigDict(
        from_attributes=True,
    )


class FullUser(UserId):
    first_name: str | None = Field(default=..., max_length=125, description="Имя пользователя")
    last_name: str | None = Field(default=..., max_length=125, description="Фамилия пользователя")
    created: datetime = Field(default=..., description="Дата регистрации")
    updated: datetime = Field(default=..., description="Дата изменения")

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserRegister(User):
    password: str = Field(min_length=3, max_length=8, description="Пароль")


class AuthUser(BaseModel):
    username: str = Field(description="Имя пользователя")
    password: str = Field(description="Пароль")
    device_id: str | None = Field(
        default=None, min_length=1, max_length=100, title="Устройство", description="Устройство пользователя"
    )
    not_before: datetime | None = Field(default=None, description="Начало действия токена")

    @classmethod
    @field_validator('not_before', mode="before")
    def ensure_timezone(cls, value: datetime) -> datetime:
        if value:
            current_time = datetime.now(tz=timezone.utc)
            if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
                raise ValueError("not_before must include a timezone")
            if value < current_time:
                raise ValueError("not_before must be later than the current date")
        return value


class AllUsers(BaseModel):
    users: list[User] = Field(description="Пользователи системы")

    model_config = ConfigDict(
        from_attributes=True,
    )


class JWTToken(BaseModel):
    jti: UUID = Field(description="Идентификатор токена")
    is_active: bool = Field(default=False, description="Активен")
    expired_time: datetime = Field(description="Окончание доступа")
    device_id: str = Field(default="Не указано", description="Устройство пользователя")
    user_id: UserId = Field(description="id пользователя")


class JWTAccessToken(JWTToken):

    model_config = ConfigDict(
        from_attributes=True,
    )


class JWTRefreshToken(JWTToken):

    model_config = ConfigDict(
        from_attributes=True,
    )

