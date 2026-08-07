"""create extracted_evidence table

Revision ID: 2026_08_07_0004
Revises: 2026_08_07_0003
Create Date: 2026-08-07 23:59:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2026_08_07_0004'
down_revision: Union[str, None] = '2026_08_07_0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'extracted_evidence',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider_result_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_domain', sa.String(length=255), nullable=False),
        sa.Column('mentioned', sa.Boolean(), nullable=False),
        sa.Column('raw_citations', sa.JSON(), nullable=False),
        sa.Column('matched_snippets', sa.JSON(), nullable=False),
        sa.Column('extracted_brand_mentions', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['job_id'], ['analysis_jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['provider_result_id'], ['provider_results.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_extracted_evidence_id'), 'extracted_evidence', ['id'], unique=False)
    op.create_index(op.f('ix_extracted_evidence_job_id'), 'extracted_evidence', ['job_id'], unique=False)
    op.create_index(op.f('ix_extracted_evidence_target_domain'), 'extracted_evidence', ['target_domain'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_extracted_evidence_target_domain'), table_name='extracted_evidence')
    op.drop_index(op.f('ix_extracted_evidence_job_id'), table_name='extracted_evidence')
    op.drop_index(op.f('ix_extracted_evidence_id'), table_name='extracted_evidence')
    op.drop_table('extracted_evidence')
