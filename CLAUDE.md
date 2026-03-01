# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SpeechMate is a voice recognition and translation assistant with a client-server architecture:
- **Host Server**: FastAPI-based API server with Flask web admin interface
- **Client**: PyQt5 desktop application for Windows

The project uses `faster-whisper` for speech-to-text (ASR) and supports hotkey-triggered voice input.

## Common Commands

### Host Server

```bash
# Install dependencies
cd host
pip install -r requirements.txt

# Run server (starts both API and Web admin)
python start_server.py

# Stop server
python stop_server.py

# Run tests
python test_server.py

# Run with pytest
pytest tests/ -v

# Run specific test
pytest tests/test_asr_model.py -v
```

### Client

```bash
# Install dependencies
cd client
pip install -r requirements.txt

# Run client
python app/main.py

# Build executable
python build.py --all
```

## Architecture

### Host Server Structure

```
host/
├── app/                    # FastAPI application
│   ├── main.py            # API entry point, lifespan management
│   ├── config.py          # Configuration (pydantic), GPU auto-detection
│   ├── database.py        # SQLAlchemy models (APIKey, UsageLog)
│   └── api/               # API routers
│       ├── transcribe.py  # /api/v1/transcribe endpoint
│       ├── translate.py   # /api/v1/translate endpoint (not implemented)
│       └── stats.py       # Statistics endpoint
├── models/                 # Model wrappers
│   └── asr_model.py       # faster-whisper wrapper with caching
├── web/                    # Flask web admin (port 5000)
│   ├── app.py             # API key management, model config
│   └── templates/index.html
└── tests/                  # pytest test suite
```

### Client Structure

```
client/
├── app/
│   ├── main.py            # PyQt5 entry point
│   ├── config.py          # Client config (base_url, api_key, hotkeys)
│   ├── recorder.py        # sounddevice audio capture
│   ├── hotkey.py          # pynput global hotkey listener
│   ├── api_client.py      # HTTP client for Host API
│   └── text_input.py      # Clipboard paste simulation
└── ui/
    ├── main_window.py     # Settings dialog
    ├── tray_icon.py       # System tray with menu
    └── recording_indicator.py  # Floating recording status
```

### Key Design Patterns

1. **Model Caching**: `host/models/asr_model.py` uses global `_model` cache to avoid reloading Whisper models between requests

2. **Hotkey Actions**: Client uses enum-based action system (`HotkeyAction.TRANSCRIBE`, etc.) with callback registration

3. **API Key Auth**: All API endpoints require `X-API-Key` header, verified against SQLite database

4. **GPU Auto-Detection**: `host/app/config.py` auto-detects CUDA availability on startup

## Configuration

- Host: `host/data/config.yaml` (auto-created)
- Client: `client/data/config.json` (auto-created)

## Default Ports

- API Server: 8000
- Web Admin: 5000

## Default Hotkeys

- `Alt` (hold): Voice transcription
- `Shift` (hold): Chinese to English translation
- `Shift+A` (hold): English to Chinese translation

## Translation Feature Status

Translation functionality is **not yet implemented**. The `/api/v1/translate` endpoint returns an error message. See `host/app/api/translate.py`.

## Testing

Tests use pytest with markers:
- `@pytest.mark.slow` - Tests that require model loading (skip with `-m "not slow"`)

Test fixtures are in `host/tests/conftest.py`. Sample audio files should be placed in `host/tests/fixtures/`.