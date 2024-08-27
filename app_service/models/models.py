from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app_service.models.database import Base


class ProbaTable(Base):
    """
    Пробная таблица
    """
    __tablename__ = "proba"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=True)
