"""
SpeechMate Host Server - FastAPI Main Entry
"""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import config, ASR_MODELS, get_base_url, get_local_ip, save_config
from app.database import init_db
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("SpeechMate Host Server starting...")

    # Initialize database
    init_db()
    logger.info("Database initialized")

    # Print server info
    logger.info(f"API Server: http://{get_local_ip()}:{config.server.api_port}")
    logger.info(f"Admin API Key: {config.admin_api_key}")

    yield

    # Shutdown
    logger.info("SpeechMate Host Server shutting down...")


# Create FastAPI app
app = FastAPI(
    title="SpeechMate API",
    description="Speech Recognition and Translation API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc)}
    )


# Include API routes
app.include_router(api_router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "speechmate-api"}


# Server info endpoint
@app.get("/api/v1/info")
async def server_info():
    """Get server information"""
    return {
        "success": True,
        "base_url": get_base_url(),
        "current_model": {
            "asr": config.model.asr_model,
            "device": config.model.asr_device,
            "compute_type": config.model.asr_compute_type
        },
        "available_models": ASR_MODELS,
        "admin_api_key": config.admin_api_key
    }


# Model configuration endpoint
@app.post("/api/v1/config/model")
async def update_model_config(
    asr_model: str = None,
    asr_device: str = None,
    asr_compute_type: str = None
):
    """Update model configuration"""
    from models.asr_model import unload_model

    if asr_model and asr_model in ASR_MODELS:
        config.model.asr_model = asr_model
        unload_model()  # Unload current model

    if asr_device in ["cpu", "cuda"]:
        config.model.asr_device = asr_device

    if asr_compute_type in ["float16", "int8", "int8_float16"]:
        config.model.asr_compute_type = asr_compute_type

    save_config()

    return {
        "success": True,
        "config": {
            "asr_model": config.model.asr_model,
            "asr_device": config.model.asr_device,
            "asr_compute_type": config.model.asr_compute_type
        }
    }


def run_server():
    """Run the API server"""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=config.server.api_host,
        port=config.server.api_port,
        reload=config.server.debug
    )


if __name__ == "__main__":
    run_server()
