import os
import io
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional
import signal
import sys

HOST_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HOST_DIR))

from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Template

import config as config_module
from src.asr_engine import ASREngine
from src.translate_engine import TranslationEngine
from src.key_manager import KeyManager

load_config = config_module.load_config
save_config = config_module.save_config

app = FastAPI(title="SpeechMate API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

app_config = load_config()
key_manager = KeyManager(app_config)

asr_engine = None
translate_engine = None

def get_asr_engine():
    global asr_engine
    if asr_engine is None:
        asr_engine = ASREngine(app_config["asr_model"], app_config["device"])
    return asr_engine

def get_translate_engine():
    global translate_engine
    if translate_engine is None:
        translate_engine = TranslationEngine(app_config["translate_model"], app_config["device"])
    return translate_engine


def graceful_shutdown(signum, frame):
    print("\nShutting down...")
    if asr_engine:
        asr_engine.unload_model()
    if translate_engine:
        translate_engine.unload_model()
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)


@app.get("/", response_class=HTMLResponse)
async def index():
    template_path = TEMPLATES_DIR / "index.html"
    if not template_path.exists():
        return HTMLResponse(content="<h1>Template not found</h1>", status_code=500)
    
    with open(template_path, encoding='utf-8') as f:
        template = Template(f.read())
    
    stats = key_manager.get_stats()
    total_calls = sum(stats.get("daily", {}).values())
    
    models_info = {
        "asr": {
            "current": app_config["asr_model"],
            "available": [
                {"name": "base", "size": "140MB", "accuracy": "Medium", "speed": "Fast"},
                {"name": "small", "size": "290MB", "accuracy": "Medium-High", "speed": "Fast"},
                {"name": "medium", "size": "1.5GB", "accuracy": "High", "speed": "Medium"},
                {"name": "large-v3", "size": "3.1GB", "accuracy": "Highest", "speed": "Medium"}
            ]
        },
        "translate": {
            "current": app_config["translate_model"],
            "available": [
                {"name": "m2m100-418M", "size": "1.6GB", "speed": "Medium"},
                {"name": "m2m100-1.2B", "size": "2.5GB", "speed": "Slow"}
            ]
        },
        "device": app_config["device"]
    }
    
    return template.render(
        base_url=f"http://{app_config['host']}:{app_config['port']}",
        keys=key_manager.get_all_keys(),
        stats=stats,
        total_calls=total_calls,
        models=models_info
    )


@app.post("/api/v1/asr")
async def asr(
    audio: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key is required")
    
    if not key_manager.validate_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    key_manager.record_usage(x_api_key, "asr")
    
    audio_data = await audio.read()
    
    if len(audio_data) == 0:
        raise HTTPException(status_code=400, detail="Empty audio file")
    
    try:
        result = get_asr_engine().transcribe_audio_data(audio_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ASR processing failed: {str(e)}")


@app.post("/api/v1/translate")
async def translate(
    text: str = Form(...),
    src_lang: str = Form("zh"),
    tgt_lang: str = Form("en"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key is required")
    
    if not key_manager.validate_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    key_manager.record_usage(x_api_key, "translate")
    
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    
    try:
        result = get_translate_engine().translate(text, src_lang, tgt_lang)
        return {"success": True, "data": {"text": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.get("/api/v1/models")
async def get_models():
    return {
        "asr": {
            "current": app_config["asr_model"],
            "available": [
                {"name": "base", "size": "140MB", "accuracy": "Medium", "speed": "Fast"},
                {"name": "small", "size": "290MB", "accuracy": "Medium-High", "speed": "Fast"},
                {"name": "medium", "size": "1.5GB", "accuracy": "High", "speed": "Medium"},
                {"name": "large-v3", "size": "3.1GB", "accuracy": "Highest", "speed": "Medium"}
            ]
        },
        "translate": {
            "current": app_config["translate_model"],
            "available": [
                {"name": "m2m100-418M", "size": "1.6GB", "speed": "Medium"},
                {"name": "m2m100-1.2B", "size": "2.5GB", "speed": "Slow"}
            ]
        },
        "device": app_config["device"]
    }


@app.post("/api/v1/models/switch")
async def switch_model(
    model_type: str = Form(...),
    model_name: str = Form(...),
    device: Optional[str] = Form(None)
):
    global asr_engine, translate_engine
    
    try:
        if model_type == "asr":
            if asr_engine:
                asr_engine.unload_model()
            asr_engine = ASREngine(model_name, device or app_config["device"])
            app_config["asr_model"] = model_name
        elif model_type == "translate":
            if translate_engine:
                translate_engine.unload_model()
            translate_engine = TranslationEngine(model_name, device or app_config["device"])
            app_config["translate_model"] = model_name
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")
        
        if device:
            app_config["device"] = device
        
        save_config(app_config)
        return {"success": True, "message": f"Switched to {model_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model switch failed: {str(e)}")


@app.get("/api/v1/stats")
async def get_stats(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    if x_api_key:
        if not key_manager.validate_key(x_api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")
        return key_manager.get_stats(x_api_key)
    return key_manager.get_stats()


@app.get("/api/v1/keys")
async def get_keys():
    return key_manager.get_all_keys()


@app.post("/api/v1/keys")
async def create_key(name: str = Form("default")):
    key = key_manager.generate_key(name)
    return {"success": True, "key": key}


@app.delete("/api/v1/keys/{key}")
async def delete_key(key: str):
    key_manager.delete_key(key)
    return {"success": True}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    print(f"""
============================================
   SpeechMate API Server
============================================
   Server: http://{app_config['host']}:{app_config['port']}
   Web UI: http://{app_config['host']}:{app_config['port']}/
   Press Ctrl+C to stop
============================================
    """)
    uvicorn.run(app, host=app_config["host"], port=app_config["port"], log_level="info")
