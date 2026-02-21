"""
SpeechMate API Routes
"""
from fastapi import APIRouter
from app.api.transcribe import router as transcribe_router
from app.api.translate import router as translate_router
from app.api.stats import router as stats_router

api_router = APIRouter()

api_router.include_router(transcribe_router, prefix="/api/v1", tags=["transcribe"])
api_router.include_router(translate_router, prefix="/api/v1", tags=["translate"])
api_router.include_router(stats_router, prefix="/api/v1", tags=["stats"])
