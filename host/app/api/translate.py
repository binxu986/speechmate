"""
SpeechMate Translate API

NOTE: Translation functionality is not yet implemented.
This endpoint will return an error indicating the feature is coming soon.
"""
import time
from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Form
from typing import Optional
from pydantic import BaseModel

from loguru import logger
from app.database import verify_api_key

router = APIRouter()


class TranslateResponse(BaseModel):
    """Translate API response"""
    success: bool
    original_text: str = ""
    translated_text: str = ""
    source_lang: str = ""
    target_lang: str = ""
    duration: float = 0.0
    processing_time: float = 0.0
    error: str = ""


@router.post("/translate", response_model=TranslateResponse)
async def translate_audio(
    audio: UploadFile = File(..., description="Audio file (wav/mp3/m4a)"),
    source_lang: str = Form("zh", description="Source language (zh/en)"),
    target_lang: str = Form("en", description="Target language (zh/en)"),
    x_api_key: str = Header(..., alias="X-API-Key", description="API Key")
):
    """
    Translate audio to target language

    - **audio**: Audio file to translate
    - **source_lang**: Source language code (zh for Chinese, en for English)
    - **target_lang**: Target language code (zh for Chinese, en for English)
    - **X-API-Key**: Your API key

    Examples:
    - Chinese to English: source_lang=zh, target_lang=en
    - English to Chinese: source_lang=en, target_lang=zh

    NOTE: This feature is not yet implemented.
    """
    # Verify API key
    api_key_obj = verify_api_key(x_api_key)
    if not api_key_obj:
        raise HTTPException(status_code=401, detail="Invalid API key")

    logger.warning(f"Translation request received but feature not implemented: {source_lang}->{target_lang}")

    # Return error indicating feature is not implemented
    return TranslateResponse(
        success=False,
        error="Translation feature is not yet implemented. This feature will be added in a future update. Please use the /transcribe endpoint for speech-to-text only."
    )