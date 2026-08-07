from typing import List
from fastapi import APIRouter, Depends, status

from app.schemas.prompt import PromptTemplate
from app.services.prompt_service import prompt_service, PromptService

router = APIRouter()


@router.get(
    "/prompts",
    response_model=List[PromptTemplate],
    status_code=status.HTTP_200_OK,
    summary="Get Active Prompt Template Catalog",
    description="Returns all active, version-controlled prompt templates used by the Prompt Evaluation Framework.",
    responses={
        200: {
            "description": "Active prompt template catalog returned successfully.",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "PROMPT_DIRECT_V1",
                            "version": "1.0.0",
                            "category": "DIRECT",
                            "template": "What companies or software tools would you recommend for business domain {domain}?",
                            "description": "Direct recommendation query evaluating top-of-mind brand awareness.",
                            "active": True
                        }
                    ]
                }
            }
        }
    }
)
async def list_active_prompts(
    service: PromptService = Depends(lambda: prompt_service)
) -> List[PromptTemplate]:
    return service.list_active_prompts()
