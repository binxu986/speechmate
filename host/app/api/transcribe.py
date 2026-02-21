"""
SpeechMate Transcribe API
"""
import time
import tempfile
import os
from fastapi import APIRouter, UploadFile, File, Header, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel

from loguru import logger
from models.asr_model import transcribe_audio, get_audio_duration
from app.database import verify_api_key, log_usage
from app.config import config

router = APIRouter()


class TranscribeResponse(BaseModel):
    """Transcribe API response"""
    success: bool
    text: str = ""
    language: str = ""
    duration: float = 0.0
    processing_time: float = 0.0
    error: str = ""


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    audio: UploadFile = File(..., description="Audio file (wav/mp3/m4a)"),
    language: Optional[str] = Form(None, description="Language code (zh/en)"),
    x_api_key: str = Header(..., alias="X-API-Key", description="API Key")
):
    """
    Transcribe audio to text

    - **audio**: Audio file to transcribe
    - **language**: Optional language code (zh for Chinese, en for English)
    - **X-API-Key**: Your API key
    """
    # Verify API key
    api_key_obj = verify_api_key(x_api_key)
    if not api_key_obj:
        raise HTTPException(status_code=401, detail="Invalid API key")

    start_time = time.time()
    tmp_path = None

    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(audio.filename)[1] or ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            content = await audio.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Get audio duration
        audio_duration = get_audio_duration(tmp_path)

        logger.info(f"Processing transcription request: {audio.filename}, duration: {audio_duration:.2f}s")

        # Run transcription
        text, detected_lang, processing_time = transcribe_audio(
            tmp_path,
            model_name=config.model.asr_model,
            device=config.model.asr_device,
            language=language
        )

        total_time = time.time() - start_time

        # Log usage
        log_usage(
            api_key_id=api_key_obj["id"],
            endpoint="transcribe",
            audio_duration=audio_duration,
            processing_time=total_time,
            source_lang=detected_lang,
            success=True
        )

        return TranscribeResponse(
            success=True,
            text=text,
            language=detected_lang,
            duration=audio_duration,
            processing_time=total_time
        )

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        total_time = time.time() - start_time

        # Log failed usage
        log_usage(
            api_key_id=api_key_obj["id"],
            endpoint="transcribe",
            processing_time=total_time,
            success=False,
            error_message=str(e)
        )

        return TranscribeResponse(
            success=False,
            error=str(e)
        )

    finally:
        # Clean up temporary file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass
