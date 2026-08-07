"""add prompt metadata to provider_results

Revision ID: 2026_08_07_0005
Revises: 2026_08_07_0004
Create Date: 2026-08-07 23:56:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2026_08_07_0005'
down_revision: Union[str, None] = '2026_08_07_0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('provider_results', sa.Column('prompt_id', sa.String(length=64), nullable=True))
    op.add_column('provider_results', sa.Column('prompt_version', sa.String(length=32), nullable=True))
    op.add_column('provider_results', sa.Column('prompt_category', sa.String(length=32), nullable=True))


def downgrade() -> None:
    op.drop_column('provider_results', 'prompt_category')
    op.drop_column('provider_results', 'prompt_version')
    op.drop_column('provider_results', 'prompt_id')
