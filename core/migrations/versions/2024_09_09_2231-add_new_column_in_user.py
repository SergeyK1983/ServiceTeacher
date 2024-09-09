"""add new column in user

Revision ID: 193381dfcd84
Revises: 173560e60ed1
Create Date: 2024-09-09 22:31:08.012854

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "193381dfcd84"
down_revision: Union[str, None] = "173560e60ed1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Дата создания",
        ),
        sa.Column(
            "updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Дата изменения",
        ),
        sa.Column(
            "username",
            sa.String(length=100),
            nullable=False,
            comment="ник пользователя",
        ),
        sa.Column("password", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=True, comment="Имя пользователя",),
        sa.Column("last_name", sa.String(length=100), nullable=True, comment="Фамилия пользователя",),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, comment="супер пользователь",),
        sa.Column("is_active", sa.Boolean(), nullable=False, comment="Активен"),
        sa.Column("is_staff", sa.Boolean(), nullable=False, comment="супер пользователь",),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_index(op.f("ix_user_email"), "user", ["email"], unique=True)
    op.create_index(op.f("ix_user_username"), "user", ["username"], unique=True)
    op.drop_table("users")


def downgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column(
            "username",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=False,
            comment="Имя пользователя",
        ),
        sa.Column(
            "password",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.VARCHAR(length=100),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "is_staff",
            sa.BOOLEAN(),
            autoincrement=False,
            nullable=False,
            comment="супер пользователь",
        ),
        sa.PrimaryKeyConstraint("id", name="users_pkey"),
    )
    op.drop_index(op.f("ix_user_username"), table_name="user")
    op.drop_index(op.f("ix_user_email"), table_name="user")
    op.drop_table("user")
