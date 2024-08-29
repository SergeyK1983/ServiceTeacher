from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from .crud import create_proba
from .models.database import get_db
from .schemas import ProbaCreate


router = APIRouter()

swagger_post_proba = {
    "tags": ["prob"],
    "summary": "Create a proba",
    "response_description": "The created proba",
    # "deprecated": True  # Пометка, что операция пути устаревшая
}


@router.post("/proba", response_model=ProbaCreate, status_code=status.HTTP_201_CREATED, **swagger_post_proba)
def post_proba(proba: ProbaCreate, db: Session = Depends(get_db)):
    """
    Create the proba instance.
    """
    db_proba = create_proba(db, proba)

    return db_proba



