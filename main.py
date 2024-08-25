from fastapi import FastAPI

from app_service.models.database import Base, engine, SessionLocal

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

