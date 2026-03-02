# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SpeechMate is a voice recognition and translation assistant with a client-server architecture:
- **Host Server**: FastAPI-based API server with Flask web admin interface
- **Client**: PyQt5 desktop application for Windows

The project uses `faster-whisper` for speech-to-text (ASR) and supports hotkey-triggered voice input.

**Current Status**: Project is in development/debugging phase. Translation functionality is not yet implemented.

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

# Skip slow tests (model loading)
pytest tests/ -v -m "not slow"
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
│       ├── translate.py   # /api/v1/translate endpoint (NOT IMPLEMENTED)
│       └── stats.py       # Statistics endpoint
├── models/                 # Model wrappers (MISSING - needs creation)
│   └── asr_model.py       # faster-whisper wrapper with caching
├── web/                    # Flask web admin (port 5000)
│   ├── app.py             # API key management, model config
│   └── templates/index.html
├── tests/                  # pytest test suite
│   ├── conftest.py        # Test fixtures
│   ├── test_asr_model.py  # ASR model tests
│   ├── test_config.py     # Config tests
│   └── test_database.py   # Database tests
├── start_server.py        # One-click startup script
├── stop_server.py         # Service shutdown script
└── test_server.py         # Server test script
```

### Client Structure

```
client/
├── app/
│   ├── main.py            # PyQt5 entry point
│   ├── config.py          # Client config (base_url, api_key, hotkeys)
│   ├── recorder.py        # sounddevice audio capture (16kHz, mono)
│   ├── hotkey.py          # pynput global hotkey listener
│   ├── api_client.py      # HTTP client for Host API
│   └── text_input.py      # Clipboard paste simulation (Ctrl+V)
├── ui/
│   ├── main_window.py     # Settings dialog
│   ├── tray_icon.py       # System tray with menu
│   └── recording_indicator.py  # Floating recording status
├── utils/
│   └── logger.py          # Loguru logging setup
└── build.py               # PyInstaller build script
```

### Key Design Patterns

1. **Model Caching**: `host/models/asr_model.py` should use global `_model` cache to avoid reloading Whisper models between requests

2. **Hotkey Actions**: Client uses enum-based action system (`HotkeyAction.TRANSCRIBE`, etc.) with callback registration

3. **API Key Auth**: All API endpoints require `X-API-Key` header, verified against SQLite database

4. **GPU Auto-Detection**: `host/app/config.py` auto-detects CUDA availability on startup

5. **Lifespan Management**: FastAPI uses `@asynccontextmanager` lifespan for startup/shutdown events

## API Endpoints

### FastAPI (Port 8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/info` | GET | Server info and model config |
| `/api/v1/transcribe` | POST | Speech-to-text (requires X-API-Key) |
| `/api/v1/translate` | POST | Translation (NOT IMPLEMENTED) |
| `/api/v1/config/model` | POST | Update model configuration |

### Flask Web Admin (Port 5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web admin interface |
| `/api/keys` | GET/POST | List/Create API keys |
| `/api/keys/<id>` | DELETE | Delete API key |
| `/api/keys/<id>/toggle` | POST | Enable/disable API key |
| `/api/stats` | GET | Usage statistics |
| `/api/config/model` | POST | Update model config |

## Configuration

- Host: `host/data/config.yaml` (auto-created)
- Client: `client/data/config.json` (auto-created)

### Host Config Structure

```yaml
server:
  api_host: "0.0.0.0"
  api_port: 8000
  web_host: "0.0.0.0"
  web_port: 5000
  debug: false

model:
  asr_model: "small"        # tiny, base, small, medium, large-v3
  asr_device: "cpu"         # cpu or cuda (auto-detected)
  asr_compute_type: "int8"  # float16 (GPU), int8 (CPU)
  translation_model_zh_en: "Helsinki-NLP/opus-mt-zh-en"
  translation_model_en_zh: "Helsinki-NLP/opus-mt-en-zh"
```

### Client Config Structure

```json
{
  "base_url": "http://localhost:8000",
  "api_key": "",
  "hotkeys": {
    "transcribe": "alt",
    "translate_zh_to_en": "shift",
    "translate_en_to_zh": "shift+a"
  },
  "auto_start": false,
  "minimize_to_tray": true,
  "show_recording_indicator": true,
  "language": "auto"
}
```

## Default Ports

- API Server: 8000
- Web Admin: 5000

## Default Hotkeys

| Hotkey | Action |
|--------|--------|
| `Alt` (hold) | Voice transcription |
| `Shift` (hold) | Chinese to English translation |
| `Shift+A` (hold) | English to Chinese translation |

## Supported ASR Models

| Model | Size | Speed | Accuracy | Description |
|-------|------|-------|----------|-------------|
| tiny | 39MB | Fastest | Basic | Quick response scenarios |
| base | 74MB | Fast | Good | Balance of speed/accuracy |
| small | 244MB | Medium | Good | Recommended default |
| medium | 769MB | Slow | Very Good | High accuracy |
| large-v3 | 1.5GB | Slowest | Best | Highest accuracy |

## Translation Feature Status

Translation functionality is **NOT YET IMPLEMENTED**. The `/api/v1/translate` endpoint returns an error message. See `host/app/api/translate.py`.

## Known Issues

1. **Missing `models` directory**: The `host/models/asr_model.py` file is referenced but the directory doesn't exist. This needs to be created with:
   - `get_asr_model()` - Load/cache Whisper model
   - `transcribe_audio()` - Transcribe audio file
   - `get_audio_duration()` - Get audio length
   - `unload_model()` - Clear model cache
   - `get_model_info()` - Get current model status

2. **Project in debugging phase**: README indicates ongoing debugging

## Testing

Tests use pytest with markers:
- `@pytest.mark.slow` - Tests that require model loading (skip with `-m "not slow"`)

Test fixtures are in `host/tests/conftest.py`. Sample audio files should be placed in `host/tests/fixtures/`.

## Technical Stack

### Host
- FastAPI - API framework
- Flask - Web admin interface
- faster-whisper - Speech recognition
- Helsinki-NLP/opus-mt - Translation (planned)
- SQLAlchemy - Database ORM
- Loguru - Logging

### Client
- PyQt5 - GUI framework
- sounddevice - Audio recording
- pynput - Global hotkey listener
- pyperclip - Clipboard operations
- keyboard - Keyboard simulation
- requests - HTTP client

## Environment Variables

- `HF_ENDPOINT` - HuggingFace mirror URL (defaults to https://hf-mirror.com for China users)
- `ADMIN_API_KEY` - Override auto-generated admin API key
- `JWT_SECRET` - Override auto-generated JWT secret
