import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel, ConfigDict


class ExtractedEvidenceCreate(BaseModel):
    """Schema for creating an ExtractedEvidence record."""
    job_id: uuid.UUID
    provider_result_id: uuid.UUID
    target_domain: str
    mentioned: bool
    raw_citations: List[str]
    matched_snippets: List[str]
    extracted_brand_mentions: List[str]


class ExtractedEvidenceResponse(BaseModel):
    """Schema for returning ExtractedEvidence details."""
    id: uuid.UUID
    job_id: uuid.UUID
    provider_result_id: uuid.UUID
    target_domain: str
    mentioned: bool
    raw_citations: List[str]
    matched_snippets: List[str]
    extracted_brand_mentions: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
