from sqlalchemy.orm import Session

from .models import ProbaTable
from .schemas import ProbaCreate


def create_proba(db: Session, proba: ProbaCreate):
    db_proba = ProbaTable(
        name=proba.name
    )
    db.add(db_proba)
    db.commit()
    db.refresh(db_proba)
    return db_proba


def get_probas(db: Session):
    return db.query(ProbaTable).all()
