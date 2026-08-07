import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.analysis_job import AnalysisJobStatus


class AnalysisJobCreate(BaseModel):
    """Schema for triggering a new Analysis Job."""
    pass


class AnalysisJobStatusUpdate(BaseModel):
    """Schema for updating job status via state machine transition."""
    status: AnalysisJobStatus
    error_message: Optional[str] = Field(None, description="Optional error details if status is Failed")


class AnalysisJobResponse(BaseModel):
    """Schema for Analysis Job API responses."""
    id: uuid.UUID
    project_id: uuid.UUID
    status: AnalysisJobStatus
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
