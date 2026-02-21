"""
SpeechMate Stats API
"""
from fastapi import APIRouter, Header, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from loguru import logger
from app.database import get_stats, get_all_api_keys, create_api_key, delete_api_key, toggle_api_key
from app.config import config

router = APIRouter()


class APIKeyInfo(BaseModel):
    """API Key information"""
    id: int
    key: str
    name: str
    is_active: bool
    created_at: Optional[str] = None
    last_used_at: Optional[str] = None


class DailyStats(BaseModel):
    """Daily statistics"""
    date: str
    transcribe: int = 0
    translate: int = 0


class APIKeyStats(BaseModel):
    """API Key statistics"""
    id: int
    key: str
    name: str
    is_active: bool
    daily_stats: List[DailyStats] = []
    total_transcribe: int = 0
    total_translate: int = 0


class StatsResponse(BaseModel):
    """Stats API response"""
    success: bool
    api_keys: List[APIKeyStats] = []
    error: str = ""


@router.get("/stats", response_model=StatsResponse)
async def get_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    x_api_key: str = Header(..., alias="X-API-Key", description="Admin API Key")
):
    """
    Get usage statistics for all API keys

    - **days**: Number of days to include in statistics (1-365)
    - **X-API-Key**: Admin API key
    """
    # Verify admin API key
    if x_api_key != config.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin API key")

    try:
        # Get all API keys
        keys = get_all_api_keys()

        # Get stats for all keys
        all_stats = get_stats(days=days)

        result = []
        for key_info in keys:
            key_id = key_info["id"]
            stats_data = all_stats.get(key_id, {})

            # Build daily stats
            daily_stats = []
            for date, counts in stats_data.get("daily", {}).items():
                daily_stats.append(DailyStats(
                    date=date,
                    transcribe=counts.get("transcribe", 0),
                    translate=counts.get("translate", 0)
                ))

            # Sort by date
            daily_stats.sort(key=lambda x: x.date, reverse=True)

            result.append(APIKeyStats(
                id=key_id,
                key=key_info["key"],
                name=key_info["name"],
                is_active=key_info["is_active"],
                daily_stats=daily_stats,
                total_transcribe=stats_data.get("total_transcribe", 0),
                total_translate=stats_data.get("total_translate", 0)
            ))

        return StatsResponse(success=True, api_keys=result)

    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return StatsResponse(success=False, error=str(e))


@router.get("/api-keys")
async def list_api_keys(
    x_api_key: str = Header(..., alias="X-API-Key", description="Admin API Key")
):
    """List all API keys"""
    if x_api_key != config.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin API key")

    keys = get_all_api_keys()
    return {"success": True, "api_keys": keys}


@router.post("/api-keys")
async def new_api_key(
    name: str,
    x_api_key: str = Header(..., alias="X-API-Key", description="Admin API Key")
):
    """Create a new API key"""
    if x_api_key != config.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin API key")

    try:
        new_key = create_api_key(name)
        return {"success": True, "key": new_key, "name": name}
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        return {"success": False, "error": str(e)}


@router.delete("/api-keys/{key_id}")
async def remove_api_key(
    key_id: int,
    x_api_key: str = Header(..., alias="X-API-Key", description="Admin API Key")
):
    """Delete an API key"""
    if x_api_key != config.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin API key")

    try:
        success = delete_api_key(key_id)
        return {"success": success}
    except Exception as e:
        logger.error(f"Failed to delete API key: {e}")
        return {"success": False, "error": str(e)}


@router.patch("/api-keys/{key_id}/toggle")
async def toggle_key(
    key_id: int,
    x_api_key: str = Header(..., alias="X-API-Key", description="Admin API Key")
):
    """Toggle API key active status"""
    if x_api_key != config.admin_api_key:
        raise HTTPException(status_code=401, detail="Invalid admin API key")

    try:
        is_active = toggle_api_key(key_id)
        return {"success": True, "is_active": is_active}
    except Exception as e:
        logger.error(f"Failed to toggle API key: {e}")
        return {"success": False, "error": str(e)}
