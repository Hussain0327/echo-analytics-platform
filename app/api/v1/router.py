from fastapi import APIRouter
from app.api.v1 import health, ingestion, metrics

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(ingestion.router, prefix="/ingestion", tags=["ingestion"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
