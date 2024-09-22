from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    username: str = Field(default=..., max_length=125, description="Имя пользователя в системе")
    email: EmailStr = Field(default=..., max_length=80, description="Электронная почта пользователя")


class FullUser(User):
    first_name: str = Field(default=..., max_length=125, description="Имя пользователя")
    last_name: str = Field(default=..., max_length=125, description="Фамилия пользователя")
    created: datetime = Field(default=..., description="Дата регистрации")
    updated: datetime = Field(default=..., description="Дата изменения")

    class Config:
        orm_mode = True


class UserRegister(User):
    password: str = Field(min_length=3, max_length=8, description="Пароль")

