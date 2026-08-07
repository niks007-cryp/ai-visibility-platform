"""create provider_results table

Revision ID: 2026_08_07_0003
Revises: 2026_08_07_0002
Create Date: 2026-08-07 23:55:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2026_08_07_0003'
down_revision: Union[str, None] = '2026_08_07_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'provider_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_name', sa.String(length=64), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('raw_response', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['analysis_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_provider_results_id'), 'provider_results', ['id'], unique=False)
    op.create_index(op.f('ix_provider_results_job_id'), 'provider_results', ['job_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_provider_results_job_id'), table_name='provider_results')
    op.drop_index(op.f('ix_provider_results_id'), table_name='provider_results')
    op.drop_table('provider_results')
