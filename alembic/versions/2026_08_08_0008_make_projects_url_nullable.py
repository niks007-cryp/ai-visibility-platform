"""make projects url nullable

Revision ID: 2026_08_08_0008
Revises: 2026_08_08_0007
Create Date: 2026-08-08 08:48:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '2026_08_08_0008'
down_revision: Union[str, None] = '2026_08_08_0007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('projects', 'url', existing_type=sa.String(length=2048), nullable=True)


def downgrade() -> None:
    op.alter_column('projects', 'url', existing_type=sa.String(length=2048), nullable=False)
