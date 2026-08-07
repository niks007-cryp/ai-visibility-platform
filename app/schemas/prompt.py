from enum import Enum
from pydantic import BaseModel, ConfigDict


class PromptCategory(str, Enum):
    DIRECT = "DIRECT"
    COMPARISON = "COMPARISON"
    USE_CASE = "USE_CASE"
    BUYING = "BUYING"


class PromptTemplate(BaseModel):
    """Version-controlled prompt template definition."""
    id: str
    version: str
    category: PromptCategory
    template: str
    description: str
    active: bool = True

    model_config = ConfigDict(from_attributes=True)
