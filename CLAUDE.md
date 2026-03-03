# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SpeechMate is a voice recognition and translation assistant with a client-server architecture:
- **Host Server**: FastAPI-based API server with Flask web admin interface
- **Client**: PyQt5 desktop application for Windows

The project uses `faster-whisper` for speech-to-text (ASR) and supports hotkey-triggered voice input.

**Current Status**: ASR functionality complete with 225 tests passing. Translation not yet implemented.

## Quick Start

### Host Server
```bash
cd host
pip install -r requirements.txt
python download_model.py --model small  # Download ASR model
python start_server.py                   # Start server
```

### Client
```bash
cd client
pip install -r requirements.txt
python app/main.py
```

## Architecture

```
host/
├── app/                    # FastAPI application
│   ├── main.py            # API entry point
│   ├── config.py          # Configuration (pydantic)
│   ├── database.py        # SQLAlchemy models
│   └── api/               # API routers (transcribe, translate, stats)
├── models/                 # Model wrappers
│   └── asr_model.py       # faster-whisper wrapper with caching
├── web/                    # Flask web admin (port 5000)
├── tests/                  # pytest test suite (145 tests)
├── start_server.py        # One-click startup
├── stop_server.py         # Service shutdown
└── download_model.py      # ASR model downloader

client/
├── app/
│   ├── main.py            # PyQt5 entry point
│   ├── config.py          # Client config
│   ├── recorder.py        # sounddevice audio capture (16kHz, mono)
│   ├── hotkey.py          # pynput global hotkey listener
│   ├── api_client.py      # HTTP client
│   └── text_input.py      # Clipboard paste (Ctrl+V)
├── ui/                     # PyQt5 UI components
├── tests/                  # pytest test suite (80 tests)
└── build.py               # PyInstaller build script
```

## Testing

```bash
# Host tests (145 tests)
cd host
pytest tests/ -v                    # All tests
pytest tests/ -v -m "not slow"      # Skip slow tests (model loading)

# Client tests (80 tests)
cd client
pytest tests/ -v
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

**Client**: PyQt5, sounddevice, pynput, pyperclip, requests
