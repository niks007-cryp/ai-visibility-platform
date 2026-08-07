"""add performance indexes

Revision ID: 2026_08_08_0007
Revises: 2026_08_08_0006
Create Date: 2026-08-08 00:21:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '2026_08_08_0007'
down_revision: Union[str, None] = '2026_08_08_0006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index('ix_projects_owner_created', 'projects', ['owner_id', 'created_at'], unique=False)
    op.create_index('ix_analysis_jobs_project_status', 'analysis_jobs', ['project_id', 'status'], unique=False)
    op.create_index('ix_extracted_evidence_job_created', 'extracted_evidence', ['job_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_extracted_evidence_job_created', table_name='extracted_evidence')
    op.drop_index('ix_analysis_jobs_project_status', table_name='analysis_jobs')
    op.drop_index('ix_projects_owner_created', table_name='projects')
