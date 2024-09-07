from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.database import get_db
from .crud import UserCrud
from .schemas import UserCreate, User

router = APIRouter(tags=["account"])


@router.post("/add_user", response_model=User, status_code=status.HTTP_201_CREATED)
def add_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = UserCrud.create_user(db, user)
    return new_user
