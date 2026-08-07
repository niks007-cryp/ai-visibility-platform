import uuid
from datetime import datetime, timezone
from typing import List
from sqlalchemy import String, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base


class ExtractedEvidence(Base):
    """SQLAlchemy ORM Model representing factual evidence extracted from raw provider text."""
    __tablename__ = "extracted_evidence"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    provider_result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("provider_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    target_domain: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    mentioned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    raw_citations: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    matched_snippets: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    extracted_brand_mentions: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    job = relationship("AnalysisJob", backref="extracted_evidence")
    provider_result = relationship("ProviderResult", backref="extracted_evidence")
