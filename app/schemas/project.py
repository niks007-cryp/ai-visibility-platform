import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ProjectCreate(BaseModel):
    name: str
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        val = v.strip().lower()
        if "." not in val:
            raise ValueError("URL must contain a valid domain name.")
        return v


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None


class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    domain: str
    url: str = Field(default="")
    owner_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def populate_url_from_domain(cls, data: any) -> any:
        if hasattr(data, "domain") and getattr(data, "domain"):
            domain_val = getattr(data, "domain")
            if not getattr(data, "url", None):
                setattr(data, "url", f"https://{domain_val}")
        elif isinstance(data, dict) and "domain" in data:
            if "url" not in data or not data["url"]:
                data["url"] = f"https://{data['domain']}"
        return data

    model_config = ConfigDict(from_attributes=True)
