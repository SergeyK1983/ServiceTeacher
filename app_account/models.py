import uuid

from sqlalchemy import String, UUID, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), unique=True, primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(100), nullable=False, comment="Имя пользователя")
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    is_staff: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False, comment="супер пользователь")


