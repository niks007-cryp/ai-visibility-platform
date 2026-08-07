import uuid
from enum import Enum
from pydantic import BaseModel, ConfigDict


class PriorityLevel(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class EffortLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ImpactLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Recommendation(BaseModel):
    """Deterministic, rule-based remediation action item."""
    id: uuid.UUID
    title: str
    description: str
    category: str
    priority: PriorityLevel
    effort: EffortLevel
    expected_impact: ImpactLevel
    trigger: str
    evidence_reference: str
    verification_method: str

    model_config = ConfigDict(from_attributes=True)
