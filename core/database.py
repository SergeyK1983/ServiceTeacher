from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from core.config import settings


DATABASE_URL = settings.postgresql_url

engine = create_engine(DATABASE_URL, echo=True)  # echo=True для отладки

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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


class Base(DeclarativeBase):
    pass
