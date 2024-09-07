"""add tables user proba

Revision ID: 173560e60ed1
Revises: 
Create Date: 2024-09-07 11:23:33.642880

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "173560e60ed1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "proba",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=True),
        sa.Column("description", sa.String(length=300), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "username",
            sa.String(length=100),
            nullable=False,
            comment="Имя пользователя",
        ),
        sa.Column("password", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column(
            "is_staff",
            sa.Boolean(),
            nullable=False,
            comment="супер пользователь",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("proba")
