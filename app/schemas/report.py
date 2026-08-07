import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.analysis_job import AnalysisJobStatus


class JobReportResponse(BaseModel):
    """Unified MVP Report payload assembled from existing domain entities for frontend rendering."""
    job_id: uuid.UUID
    project_id: uuid.UUID
    project_name: str
    target_domain: str
    job_status: AnalysisJobStatus
    provider_name: str
    prompt: str
    raw_response: str
    mentioned: bool
    raw_citations: List[str]
    matched_snippets: List[str]
    extracted_brand_mentions: List[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
