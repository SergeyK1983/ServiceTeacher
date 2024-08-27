from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app_service.crud import create_proba
from app_service.models.database import Base, engine, SessionLocal
from app_service.schemas import ProbaCreate

Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    """
    Независимый сеанс/соединение с базой данных (SessionLocal) для каждого запроса, использовать
    один и тот же сеанс для всех запросов, а затем закрыть его после завершения запроса.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/proba/")
def post_proba(proba: ProbaCreate, db: Session = Depends(get_db)):
    db_proba = create_proba(db, proba)

    return db_proba
