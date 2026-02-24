# AGENTS.md - SpeechMate Development Guide

This file provides guidelines for AI agents working on the SpeechMate project.

---

## Project Overview

SpeechMate is a voice recognition and translation assistant with two main components:

| Component | Description |
|-----------|-------------|
| **Host** (`host/`) | FastAPI server with Whisper ASR and translation models |
| **Client** (`client/`) | PyQt5 Windows desktop application |

### Core Features
- **Voice Recognition**: Press hotkey to record, release to transcribe and auto-type
- **Voice Translation**: Record and translate directly to target language
- **Multi-language**: Chinese/English recognition and translation

### Architecture
```
┌──────────────────────┐         ┌──────────────────────┐
│   Client (Windows)   │  HTTP   │    Host Server        │
│   - PyQt5 GUI       │◄───────►│    - FastAPI          │
│   - System Tray     │  REST   │    - Whisper ASR      │
│   - Recording LED   │   API   │    - Translation      │
└──────────────────────┘         └──────────────────────┘
```

---

## Build & Run Commands

### Host Server
```bash
cd host

# First time: create venv and install deps
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Start server (recommended)
python start_server.py

# Or manually:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
python -m web.app  # Web admin on port 5000
```

### Client Application
```bash
cd client
pip install -r requirements.txt
python app/main.py
```

### Running Tests
The project uses custom test scripts (not pytest):

```bash
# Test Host server components
python host/test_server.py

# Test Client components
python client/test_client.py

# Integration tests (requires running server)
python integration_test.py
```

**Run a single test function**:
```bash
# Example: run only import tests
python -c "
import sys; sys.path.insert(0, 'host')
from host.test_server import test_imports
test_imports()
"
```

### Building Client EXE
```bash
cd client
pip install pyinstaller
python build.py --all
# Output: dist/SpeechMate.exe
```

---

## Code Style Guidelines

### General Conventions
- Python 3.9+
- Use **type hints** for all function parameters and return values
- Use **docstrings** for all modules, classes, and public functions
- Use **loguru** for logging (not print for production code)
- Use **Pydantic** for configuration/data validation
- Use **SQLAlchemy** ORM for database operations

### Import Organization
Order imports strictly:
1. Standard library (`os`, `sys`, `json`, etc.)
2. Third-party packages (`fastapi`, `torch`, `pydantic`, etc.)
3. Local.`, `models.`, `ui application imports (`app.`)

```python
import os
import sys
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, Request
from pydantic import BaseModel
from loguru import logger

from app.config import config
from app.database import init_db
from models.asr_model import get_asr_model
```

### Naming Conventions
- **Functions/variables**: `snake_case` (e.g., `get_api_key`, `config_path`)
- **Classes**: `PascalCase` (e.g., `APIKey`, `ClientConfig`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_AUDIO_LENGTH`)
- **Private methods**: prefix with `_` (e.g., `_init_ui`)

### File Headers
Every Python file should start with a module docstring:
```python
"""
Module Name - Brief Description

Longer description if needed.
"""
import ...
```

### Type Hints
Always use type hints:
```python
# Good
def process_audio(audio_path: str, language: Optional[str] = None) -> dict:
    ...

# Bad
def process_audio(audio_path, language=None):
    ...
```

### Error Handling
- Use specific exception types
- Log errors with appropriate level
- Return meaningful error messages

```python
try:
    result = model.transcribe(audio)
except Exception as e:
    logger.error(f"Transcription failed: {e}")
    return {"success": False, "error": str(e)}
```

### Database Sessions
Always use context managers:
```python
@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

### Configuration
- Use Pydantic models for config classes
- Store config in `data/` directory
- Use YAML for host config, JSON for client config

### API Design
- Use FastAPI for REST endpoints
- Return consistent JSON response format:
  ```python
  {"success": True, "data": {...}}
  {"success": False, "error": "message"}
  ```
- Use HTTP status codes appropriately (200, 400, 401, 500)

### Async/Await
- Use async/await for FastAPI endpoints
- Use `run_in_executor` for blocking operations (model inference)

### GUI Code (Client)
- Use PyQt5 conventions
- Use `_init_` prefix for setup methods
- Keep UI logic separate from business logic
- Use signals/slots for event handling

---

## Technology Stack

### Host Server
| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| Web Admin | Flask + Jinja2 |
| ASR Model | faster-whisper |
| Translation | Helsinki-NLP/opus-mt |
| Database | SQLite |
| Model Inference | PyTorch + CUDA (optional) |

### Client
| Component | Technology |
|-----------|------------|
| GUI Framework | PyQt5 |
| Audio Recording | sounddevice |
| Hotkey Listener | pynput |
| HTTP Client | requests |
| Packager | PyInstaller |

---

## API Endpoints

### POST /api/v1/transcribe
- Headers: `X-API-Key: <api_key>`
- Body: `audio` (wav/mp3), `language` (zh/en)
- Response: `{"text": "...", "language": "...", "duration": 2.5}`

### POST /api/v1/translate
- Headers: `X-API-Key: <api_key>`
- Body: `audio`, `source_lang`, `target_lang`
- Response: `{"original_text": "...", "translated_text": "...", "source_lang": "zh", "target_lang": "en"}`

### GET /api/v1/stats
- Headers: `X-API-Key: <admin_api_key>`
- Response: API usage statistics

---

## Supported Models

### ASR (Whisper)
| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 39MB | Fastest | Basic |
| base | 74MB | Fast | Good |
| small | 244MB | Medium | Great (default) |
| medium | 769MB | Slow | Very Good |
| large-v3 | 1.5GB | Slowest | Best |

### Translation
- `Helsinki-NLP/opus-mt-zh-en` (Chinese → English)
- `Helsinki-NLP/opus-mt-en-zh` (English → Chinese)

---

## Default Hotkeys

| Hotkey | Action |
|--------|--------|
| Alt (hold) | Voice Recognition |
| Shift (hold) | Chinese → English |
| Shift+A (hold) | English → Chinese |

---

## Environment Variables

```bash
# Host
ADMIN_API_KEY=your_admin_key
JWT_SECRET=your_jwt_secret
HF_ENDPOINT=https://hf-mirror.com  # China mirror

# Client (uses config.json)
```

---

## Testing Guidelines

When adding new features:
1. Add test functions to appropriate test file (`host/test_server.py` or `client/test_client.py`)
2. Follow naming: `test_<component>_<feature>`
3. Use try/except and return `True`/`False`
4. Print results with `[OK]` or `[FAIL]` prefix
5. Include descriptive error messages

---

## Directory Structure

```
speechmate/
├── host/                    # Server side
│   ├── app/
│   │   ├── main.py         # FastAPI entry
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # SQLite operations
│   │   └── api/           # Route handlers
│   ├── models/             # AI models
│   ├── web/               # Flask admin
│   ├── start_server.py    # One-click start
│   └── stop_server.py    # Stop script
├── client/                 # Windows client
│   ├── app/               # Business logic
│   ├── ui/                # PyQt5 UI
│   ├── build.py          # PyInstaller script
│   └── requirements.txt
├── docs/                   # Documentation
└── AGENTS.md             # This file
```

## Key Files

| File | Purpose |
|------|---------|
| `host/app/main.py` | FastAPI entry point |
| `host/app/config.py` | Host configuration |
| `host/app/database.py` | SQLite operations |
| `host/app/api/` | API route handlers |
| `host/models/asr_model.py` | Whisper model management |
| `host/models/translation_model.py` | Translation model |
| `client/app/main.py` | PyQt5 app entry |
| `client/app/config.py` | Client configuration |
| `client/app/recorder.py` | Audio recording |
| `client/app/hotkey.py` | Hotkey listener |
| `client/ui/main_window.py` | Main window UI |

## Ports

- `8000`: Host API server
- `5000`: Web admin interface
