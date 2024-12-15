import uuid
from datetime import datetime

from sqlalchemy import BigInteger, String, UUID, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="Суперпользователь")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, comment="Активен")
    is_staff: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="Персонал")

    access_tokens: Mapped[list["AssignedJWTAccessToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )  # lazy="joined",
    refresh_tokens: Mapped[list["AssignedJWTRefreshToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"{self.id}-{self.username}"


class AssignedJWTAccessToken(Base):
    """
    Назначенный токен доступа
    """
    __tablename__ = "assigned_jwt_access_token"

    id: Mapped[BigInteger] = mapped_column(BigInteger, unique=True, primary_key=True, autoincrement=True)
    jti: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True, index=True, comment="Идентификатор токена"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="Активен")
    expired_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="Окончание доступа")
    device_id: Mapped[str] = mapped_column(String(100), default="Не указано", comment="Устройство пользователя")

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship(back_populates="access_tokens")

    def __repr__(self):
        return f"{self.id}-{self.is_active}-{self.expired_time}"


class AssignedJWTRefreshToken(Base):
    """
    Назначенный токен обновления
    """
    __tablename__ = "assigned_jwt_refresh_token"

    id: Mapped[BigInteger] = mapped_column(BigInteger, unique=True, primary_key=True, autoincrement=True)
    jti: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True, index=True, comment="Идентификатор токена"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, comment="Активен")
    expired_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="Окончание доступа")
    device_id: Mapped[str] = mapped_column(String(100), default="Не указано", comment="Устройство пользователя")

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped[User] = relationship(back_populates="refresh_tokens")

    def __repr__(self):
        return f"{self.id}-{self.is_active}-{self.expired_time}"

