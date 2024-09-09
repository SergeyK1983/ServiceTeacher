import uuid
from datetime import datetime
from sqlalchemy import String, UUID, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class User(Base):
    """
    Пользователь.
    """
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), comment="Дата создания"
    )
    updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Дата изменения"
    )
    username: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, index=True, comment="ник пользователя"
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=True, comment="Имя пользователя")
    last_name: Mapped[str] = mapped_column(String(100), nullable=True, comment="Фамилия пользователя")
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="супер пользователь")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="Активен")
    is_staff: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="супер пользователь")

    def __repr__(self):
        return f"{self.id}-{self.username}"

