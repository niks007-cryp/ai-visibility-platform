import uuid
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel, ConfigDict


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ContradictionDetail(BaseModel):
    """Details of a contradiction where brand mention status conflicted across prompts."""
    mentioned_prompt_id: str
    mentioned_prompt_category: str
    omitted_prompt_id: str
    omitted_prompt_category: str
    description: str


class EvaluationSummary(BaseModel):
    """Telemetry DTO measuring multi-prompt execution consistency and confidence level."""
    job_id: uuid.UUID
    total_prompts: int
    successful_executions: int
    mentioned_count: int
    mention_rate: float
    provider_count: int
    prompt_categories_tested: List[str]
    consistency_percentage: float
    confidence_level: ConfidenceLevel
    contradictions: List[ContradictionDetail]
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)
