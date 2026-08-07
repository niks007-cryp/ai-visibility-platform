from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, projects, analysis_jobs, evidence, report, recommendations, prompts, evaluation, worker

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(analysis_jobs.router, tags=["Analysis Jobs"])
api_router.include_router(evidence.router, tags=["Extracted Evidence"])
api_router.include_router(report.router, tags=["MVP Report"])
api_router.include_router(recommendations.router, tags=["Recommendations"])
api_router.include_router(prompts.router, tags=["Prompt Framework"])
api_router.include_router(evaluation.router, tags=["Evaluation Framework"])
api_router.include_router(worker.router, tags=["Worker Infrastructure"])
