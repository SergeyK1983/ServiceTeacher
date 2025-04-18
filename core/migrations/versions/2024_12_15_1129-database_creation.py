"""database creation

Revision ID: e76e3b422877
Revises: 
Create Date: 2024-12-15 11:29:43.537352

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e76e3b422877"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "proba",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=True),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="Дата создания"),
        sa.Column("updated", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, comment="Дата изменения"),
        sa.Column("username", sa.String(length=100), nullable=False, comment="ник пользователя"),
        sa.Column("password", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=True, comment="Имя пользователя"),
        sa.Column("last_name", sa.String(length=100), nullable=True, comment="Фамилия пользователя"),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, comment="Суперпользователь"),
        sa.Column("is_active", sa.Boolean(), nullable=False, comment="Активен"),
        sa.Column("is_staff", sa.Boolean(), nullable=False, comment="Персонал"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)
    op.create_table(
        "assigned_jwt_access_token",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("jti", sa.UUID(), nullable=False, comment="Идентификатор токена"),
        sa.Column("is_active", sa.Boolean(), nullable=False, comment="Активен"),
        sa.Column("expired_time", sa.DateTime(timezone=True), nullable=False, comment="Окончание доступа"),
        sa.Column("device_id", sa.String(length=100), nullable=False, comment="Устройство пользователя"),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("jti"),
    )
    op.create_index(op.f("ix_assigned_jwt_access_token_jti"), "assigned_jwt_access_token", ["jti"], unique=True)
    op.create_table(
        "assigned_jwt_refresh_token",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("jti", sa.UUID(), nullable=False, comment="Идентификатор токена"),
        sa.Column("is_active", sa.Boolean(), nullable=False, comment="Активен"),
        sa.Column("expired_time", sa.DateTime(timezone=True), nullable=False, comment="Окончание доступа"),
        sa.Column("device_id", sa.String(length=100), nullable=False, comment="Устройство пользователя"),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("jti"),
    )
    op.create_index(op.f("ix_assigned_jwt_refresh_token_jti"), "assigned_jwt_refresh_token", ["jti"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_assigned_jwt_refresh_token_jti"), table_name="assigned_jwt_refresh_token")
    op.drop_table("assigned_jwt_refresh_token")
    op.drop_index(op.f("ix_assigned_jwt_access_token_jti"), table_name="assigned_jwt_access_token")
    op.drop_table("assigned_jwt_access_token")
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
    op.drop_table("proba")
    # ### end Alembic commands ###
