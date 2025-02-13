"""token_default_device

Revision ID: a787a188bb93
Revises: e76e3b422877
Create Date: 2025-02-12 19:46:04.499408

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a787a188bb93"
down_revision: Union[str, None] = "e76e3b422877"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "assigned_jwt_access_token",
        "device_id",
        existing_type=sa.VARCHAR(length=100),
        server_default=sa.text("'Не указано'"),
        existing_comment="Устройство пользователя",
        existing_nullable=False,
    )
    op.alter_column(
        "assigned_jwt_refresh_token",
        "device_id",
        existing_type=sa.VARCHAR(length=100),
        server_default=sa.text("'Не указано'"),
        existing_comment="Устройство пользователя",
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "assigned_jwt_refresh_token",
        "device_id",
        existing_type=sa.VARCHAR(length=100),
        server_default=None,
        existing_comment="Устройство пользователя",
        existing_nullable=False,
    )
    op.alter_column(
        "assigned_jwt_access_token",
        "device_id",
        existing_type=sa.VARCHAR(length=100),
        server_default=None,
        existing_comment="Устройство пользователя",
        existing_nullable=False,
    )
    # ### end Alembic commands ###
