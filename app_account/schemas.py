from typing import Optional
from pydantic import BaseModel, EmailStr, constr, Field


class User(BaseModel):
    username: str


class UserCreate(User):
    password: constr(min_length=3, max_length=8)
    email: EmailStr
    is_staff: Optional[bool] = None
