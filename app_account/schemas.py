from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, constr, Field


class User(BaseModel):
    username: str
    email: EmailStr


class FullUser(User):
    first_name: str
    last_name: str
    created: datetime
    updated: datetime

    class Config:
        from_attributes = True


class UserRegister(User):
    password: constr(min_length=3, max_length=8)

