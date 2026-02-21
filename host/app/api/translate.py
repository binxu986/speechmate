"""
SpeechMate Translate API
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
from models.translation_model import translate_text
from app.database import verify_api_key, log_usage
from app.config import config

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
    """
    # Verify API key
    api_key_obj = verify_api_key(x_api_key)
    if not api_key_obj:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Validate languages
    valid_langs = ["zh", "en"]
    if source_lang not in valid_langs:
        raise HTTPException(status_code=400, detail=f"Invalid source language: {source_lang}")
    if target_lang not in valid_langs:
        raise HTTPException(status_code=400, detail=f"Invalid target language: {target_lang}")
    if source_lang == target_lang:
        raise HTTPException(status_code=400, detail="Source and target languages must be different")

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

        logger.info(f"Processing translation request: {audio.filename}, {source_lang}->{target_lang}")

        # Step 1: Transcribe audio
        original_text, detected_lang, trans_time = transcribe_audio(
            tmp_path,
            model_name=config.model.asr_model,
            device=config.model.asr_device,
            language=source_lang
        )

        if not original_text.strip():
            return TranslateResponse(
                success=True,
                original_text="",
                translated_text="",
                source_lang=source_lang,
                target_lang=target_lang,
                duration=audio_duration,
                processing_time=time.time() - start_time
            )

        # Step 2: Translate text
        translated_text, translate_time = translate_text(
            original_text,
            source_lang=source_lang,
            target_lang=target_lang
        )

        total_time = time.time() - start_time

        # Log usage
        log_usage(
            api_key_id=api_key_obj["id"],
            endpoint="translate",
            audio_duration=audio_duration,
            processing_time=total_time,
            source_lang=source_lang,
            target_lang=target_lang,
            success=True
        )

        return TranslateResponse(
            success=True,
            original_text=original_text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=target_lang,
            duration=audio_duration,
            processing_time=total_time
        )

    except Exception as e:
        logger.error(f"Translation error: {e}")
        total_time = time.time() - start_time

        # Log failed usage
        log_usage(
            api_key_id=api_key_obj["id"],
            endpoint="translate",
            processing_time=total_time,
            source_lang=source_lang,
            target_lang=target_lang,
            success=False,
            error_message=str(e)
        )

        return TranslateResponse(
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
