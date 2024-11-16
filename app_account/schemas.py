from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    username: str = Field(default=..., max_length=125, description="Имя пользователя в системе")
    email: EmailStr = Field(default=..., max_length=80, description="Электронная почта пользователя")


class UserId(User):
    id: UUID = Field(default=..., description="Идентификатор")

    class Config:
        from_attributes = True


class FullUser(UserId):
    first_name: str | None = Field(default=..., max_length=125, description="Имя пользователя")
    last_name: str | None = Field(default=..., max_length=125, description="Фамилия пользователя")
    created: datetime = Field(default=..., description="Дата регистрации")
    updated: datetime = Field(default=..., description="Дата изменения")

    class Config:
        from_attributes = True


class UserRegister(User):
    password: str = Field(min_length=3, max_length=8, description="Пароль")


class AuthUser(BaseModel):
    username: str = Field(description="Имя пользователя")
    password: str = Field(description="Пароль")


class AllUsers(BaseModel):
    users: list[User] = Field(description="Пользователи системы")

    class Config:
        from_attributes = True
