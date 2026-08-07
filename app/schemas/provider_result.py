import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ProviderResultCreate(BaseModel):
    """Schema for creating a ProviderResult."""
    job_id: uuid.UUID
    provider_name: str
    prompt: str
    raw_response: str
    prompt_id: Optional[str] = None
    prompt_version: Optional[str] = None
    prompt_category: Optional[str] = None


class ProviderResultResponse(BaseModel):
    """Schema for returning ProviderResult details."""
    id: uuid.UUID
    job_id: uuid.UUID
    provider_name: str
    prompt: str
    raw_response: str
    prompt_id: Optional[str] = None
    prompt_version: Optional[str] = None
    prompt_category: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
