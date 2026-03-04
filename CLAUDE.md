# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SpeechMate is a voice recognition and translation assistant with a client-server architecture:
- **Host Server**: FastAPI-based API server with Flask web admin interface
- **Client**: PyQt5 desktop application for Windows

The project uses `faster-whisper` for speech-to-text (ASR) and supports hotkey-triggered voice input.

**Current Status**: ASR functionality complete with 221 tests passing. Translation not yet implemented.

## Quick Start

### Using Scripts (Recommended)
```bash
# Install dependencies
scripts/install.bat

# Start all services
scripts/start_all.bat

# Stop all services
scripts/stop_all.bat
```

### Manual Start

#### Host Server
```bash
cd host
pip install -r requirements.txt
python download_model.py --model small  # Download ASR model
python start_server.py                   # Start server
```

#### Client
```bash
cd client
pip install -r requirements.txt
python app/main.py
```

## Project Structure

```
speechmate/
├── host/                      # Server-side code
│   ├── app/                   # FastAPI application
│   │   ├── main.py           # API entry point
│   │   ├── config.py         # Configuration (pydantic)
│   │   ├── database.py       # SQLAlchemy models
│   │   └── api/              # API routers (transcribe, translate, stats)
│   ├── models/               # Model wrappers
│   │   └── asr_model.py     # faster-whisper wrapper with caching
│   ├── web/                  # Flask web admin (port 5000)
│   ├── tests/                # pytest test suite (145 tests)
│   ├── data/                 # Configuration and database files
│   ├── model_cache/          # Downloaded ASR models
│   ├── start_server.py      # One-click startup
│   ├── stop_server.py       # Service shutdown
│   └── download_model.py    # ASR model downloader
│
├── client/                    # Client-side code
│   ├── app/
│   │   ├── main.py           # PyQt5 entry point
│   │   ├── config.py         # Client config
│   │   ├── recorder.py       # sounddevice audio capture (16kHz, mono)
│   │   ├── hotkey.py         # keyboard global hotkey listener
│   │   ├── api_client.py     # HTTP client
│   │   └── text_input.py     # Clipboard paste (Ctrl+V)
│   ├── ui/                   # PyQt5 UI components
│   ├── tests/                # pytest test suite (80 tests)
│   ├── data/                 # Configuration files
│   └── build.py             # PyInstaller build script
│
├── scripts/                   # Utility scripts
│   ├── install.bat/sh        # One-click installation
│   ├── run_host.bat/sh       # Start host server
│   ├── run_client.bat/sh     # Start client
│   ├── start_all.bat/sh      # Start all services
│   ├── stop_all.bat/sh       # Stop all services
│   └── run_tests.py          # Run all tests
│
├── docs/                      # Documentation
│   ├── deployment_guide.md   # Deployment instructions
│   └── user_manual.md        # User manual
│
├── CLAUDE.md                  # This file
├── README.md                  # Project readme
└── plan.md                    # Development plan
```

## Testing

### Running Tests

```bash
# Run all tests (recommended)
python scripts/run_tests.py

# Run with test report generation
python scripts/run_tests.py --report

# Run all tests including slow ones (model loading)
python scripts/run_tests.py --all

# Run with coverage report
python scripts/run_tests.py --coverage

# Run only host or client tests
python scripts/run_tests.py --host
python scripts/run_tests.py --client

# Or manually:
cd host && pytest tests/ -v -m "not slow"   # Host unit tests
cd client && pytest tests/ -v               # Client tests
```

### Test Architecture

The project has 221 tests total across two test suites:

**Host Tests (141 tests)**:
- `test_api.py` - API endpoint tests (health, transcribe, translate, stats, keys)
- `test_asr_model.py` - ASR model tests (loading, transcription, audio duration)
- `test_config.py` - Configuration tests (server, model, database settings)
- `test_database.py` - Database tests (API keys, usage logging, sessions)
- `test_web_admin.py` - Web admin interface tests
- `test_integration_api.py` - Integration tests for full workflows
- `test_server_startup.py` - Server startup and environment tests

**Client Tests (80 tests)**:
- `test_api_client.py` - API client tests (connection, requests, error handling)
- `test_client_config.py` - Client configuration tests
- `test_recorder.py` - Audio recorder tests (devices, format, state)
- `test_hotkey.py` - Hotkey listener tests (keyboard hooks, callbacks)
- `test_text_input.py` - Text input tests (clipboard, cursor insertion)
- `test_e2e.py` - End-to-end workflow tests

### Test Markers

```bash
# Skip slow tests (model loading, real API calls)
pytest tests/ -v -m "not slow"

# Run only integration tests
pytest tests/ -v -m "integration"

# Skip GUI tests on headless systems
pytest tests/ -v -m "not gui"
```

### Regression Testing Requirements

**IMPORTANT**: All tests must pass (100% pass rate) before any feature can be merged.

1. Run `python scripts/run_tests.py --report` before committing
2. Fix any failing tests before creating a PR
3. New features must include corresponding tests
4. The test report is saved to `test_reports/` directory

### Test Report Location

Test reports are generated in Markdown format:
```
test_reports/test_report_YYYYMMDD_HHMMSS.md
```

## API Endpoints

### FastAPI (Port 8000)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/v1/info` | GET | Server info |
| `/api/v1/transcribe` | POST | Speech-to-text |
| `/api/v1/translate` | POST | Translation (not implemented) |

### Flask Web Admin (Port 5000)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web admin interface |
| `/api/keys` | GET/POST | API key management |
| `/api/stats` | GET | Usage statistics |

## Configuration

- Host: `host/data/config.yaml`
- Client: `client/data/config.json`

### Default Hotkeys
| Hotkey | Function |
|--------|----------|
| Alt (hold) | Voice recognition |
| Shift (hold) | Chinese to English translation |
| Shift+A (hold) | English to Chinese translation |

## ASR Models

| Model | Size | Description |
|-------|------|-------------|
| tiny | 39MB | Fastest, basic accuracy |
| base | 74MB | Fast, good accuracy |
| small | 244MB | **Recommended default** |
| medium | 769MB | High accuracy |
| large-v3 | 1.5GB | Best accuracy |

## Deployment

See `host/DEPLOYMENT.md` for detailed deployment instructions.

```bash
# Docker deployment
cd host
docker-compose up -d

# Or bare metal
python start_server.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HF_ENDPOINT` | `https://hf-mirror.com` | HuggingFace mirror |
| `ADMIN_API_KEY` | auto-generated | Admin API key |
| `ASR_MODEL` | `small` | Default ASR model |
| `ASR_DEVICE` | auto-detected | cpu or cuda |

## Technical Stack

**Host**: FastAPI, Flask, faster-whisper, SQLAlchemy, Loguru

**Client**: PyQt5, sounddevice, keyboard, pyperclip, requests

## Important Notes

- Client uses `keyboard` library (not pynput) for hotkey detection due to better Windows Alt key support
- QTimer must run in main Qt thread - use signals for cross-thread communication
- Virtual environments are required (venv/) - scripts will not affect system Python
