from sqlalchemy import create_engine, URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from core.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME


DATABASE_URL = URL.create(
    "postgresql+psycopg2",
    username=f"{DB_USER}",
    password=f"{DB_PASS}",
    host=f"{DB_HOST}",
    port=f"{DB_PORT}",
    database=f"{DB_NAME}",
)

engine = create_engine(DATABASE_URL, echo=True)

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
