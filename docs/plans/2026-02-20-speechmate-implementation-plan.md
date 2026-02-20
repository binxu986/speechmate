# SpeechMate Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建完整的语音识别和翻译助手，包括Host服务端和Windows客户端

**Architecture:** 
- Host端: FastAPI + Faster Whisper + m2m100，提供REST API和Web管理界面
- Client端: Electron + React + Tailwind，实现全局快捷键录音和翻译

**Tech Stack:** 
- Host: Python, FastAPI, Faster Whisper, m2m100, SQLite
- Client: Electron 28, React 18, Tailwind CSS, shadcn/ui, TypeScript

---

## Part 1: Host端实现

### Task 1: 项目结构和依赖配置

**Files:**
- Create: `host/config.py`
- Create: `host/requirements.txt`
- Create: `host/src/__init__.py`
- Create: `host/deploy.sh`
- Create: `host/stop_server.sh`

**Step 1: 创建项目目录结构**

```bash
mkdir -p host/src host/models host/templates
```

**Step 2: 创建 config.py**

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config.json"
MODELS_DIR = BASE_DIR / "models"

DEFAULT_CONFIG = {
    "host": "0.0.0.0",
    "port": 3456,
    "asr_model": "base",
    "translate_model": "m2m100-418M",
    "device": "cpu",
    "api_keys": [],
    "stats": {}
}

def load_config():
    import json
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()

def save_config(config):
    import json
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
```

**Step 3: 创建 requirements.txt**

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
faster-whisper==1.0.3
transformers==4.36.2
torch==2.1.2
torchaudio==2.1.2
sentencepiece==0.1.99
protobuf==4.25.2
pydantic==2.5.3
python-multipart==0.0.6
jinja2==3.1.3
psutil==5.9.8
```

**Step 4: 创建 deploy.sh**

```bash
#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "=== Creating Python virtual environment ==="
python3 -m venv venv
source venv/bin/activate

echo "=== Installing dependencies ==="
pip install -r requirements.txt

echo "=== Installing system dependencies ==="
# Ubuntu
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y ffmpeg
# Windows
elif command -v choco &> /dev/null; then
    choco install ffmpeg -y
fi

echo "=== Downloading default models ==="
python3 -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"

echo "=== Starting server ==="
python3 -m src.api_server
```

**Step 5: 创建 stop_server.sh**

```bash
#!/bin/bash

echo "=== Stopping SpeechMate services ==="

# Kill Python processes related to this project
pkill -f "python.*src.api_server" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

# Kill by port
if command -v fuser &> /dev/null; then
    fuser -k 3456/tcp 2>/dev/null || true
elif command -v netstat &> /dev/null; then
    # Windows
    netstat -ano | findstr :3456 | findstr LISTENING | for /f "tokens=5" %%a in ('more') do taskkill /F /PID %%a
fi

echo "=== All services stopped ==="
```

**Step 6: Commit**

```bash
git add host/
git commit -m "feat(host): add project structure and deploy scripts"
```

---

### Task 2: 语音识别引擎 (ASR Engine)

**Files:**
- Create: `host/src/asr_engine.py`
- Create: `tests/host/test_asr_engine.py`

**Step 1: 创建测试文件**

```python
import pytest
from host.src.asr_engine import ASREngine

def test_asr_engine_init():
    engine = ASREngine(model_name="base", device="cpu")
    assert engine.model_name == "base"
    assert engine.device == "cpu"

def test_asr_engine_transcribe():
    engine = ASREngine(model_name="base", device="cpu")
    # Test with sample audio file path
    result = engine.transcribe("tests/fixtures/sample.wav")
    assert isinstance(result, dict)
    assert "text" in result
```

**Step 2: 创建 ASR Engine 实现**

```python
import numpy as np
from typing import Optional, Dict
from faster_whisper import WhisperModel
import torch

class ASREngine:
    def __init__(self, model_name: str = "base", device: str = "cpu", compute_type: str = "int8"):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type if device == "cpu" else "float16"
        self.model = None
        
    def load_model(self):
        if self.model is None:
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type
            )
        return self.model
    
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, any]:
        model = self.load_model()
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True
        )
        text = " ".join([seg.text for seg in segments])
        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability
        }
    
    def transcribe_audio_data(self, audio_data: bytes, sample_rate: int = 16000) -> Dict[str, any]:
        import io
        import soundfile as sf
        
        # Convert bytes to audio array
        audio_buffer = io.BytesIO(audio_data)
        audio_array, sr = sf.read(audio_buffer)
        
        # Resample if needed
        if sr != 16000:
            import librosa
            audio_array = librosa.resample(audio_array, orig_sr=sr, target_sr=16000)
        
        model = self.load_model()
        segments, info = model.transcribe(
            audio_array,
            language=None,
            beam_size=5
        )
        text = "".join([seg.text for seg in segments])
        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability
        }
    
    def unload_model(self):
        if self.model:
            del self.model
            self.model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
```

**Step 3: 运行测试**

```bash
cd host && pytest ../tests/host/test_asr_engine.py -v
```

---

### Task 3: 翻译引擎 (Translation Engine)

**Files:**
- Create: `host/src/translate_engine.py`
- Create: `tests/host/test_translate_engine.py`

**Step 1: 创建测试文件**

```python
def test_translation_zh_en():
    engine = TranslationEngine(model_name="m2m100-418M", device="cpu")
    result = engine.translate("你好世界", src_lang="zh", tgt_lang="en")
    assert isinstance(result, str)
    assert len(result) > 0

def test_translation_en_zh():
    engine = TranslationEngine(model_name="m2m100-418M", device="cpu")
    result = engine.translate("Hello world", src_lang="en", tgt_lang="zh")
    assert isinstance(result, str)
```

**Step 2: 实现翻译引擎**

```python
import torch
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from typing import Dict

class TranslationEngine:
    def __init__(self, model_name: str = "m2m100-418M", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        if self.model is None:
            self.tokenizer = M2M100Tokenizer.from_pretrained(self.model_name)
            self.model = M2M100ForConditionalGeneration.from_pretrained(self.model_name)
            self.model = self.model.to(self.device)
            self.model.eval()
        return self.model
    
    def translate(self, text: str, src_lang: str = "zh", tgt_lang: str = "en") -> str:
        model = self.load_model()
        
        # Set source language
        self.tokenizer.src_lang = src_lang
        encoded = self.tokenizer(text, return_tensors="pt").to(self.device)
        
        # Generate translation
        generated_tokens = model.generate(
            **encoded,
            forced_bos_token_id=self.tokenizer.get_lang_id(tgt_lang)
        )
        
        result = self.tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True
        )[0]
        return result
    
    def translate_audio_to_text(self, audio_path: str, src_lang: str = "zh", tgt_lang: str = "en") -> str:
        # First transcribe, then translate
        from .asr_engine import ASREngine
        asr = ASREngine()
        asr_result = asr.transcribe(audio_path, language=src_lang)
        text = asr_result["text"]
        return self.translate(text, src_lang, tgt_lang)
```

---

### Task 4: API Key 管理

**Files:**
- Create: `host/src/key_manager.py`

**Step 1: 实现 Key Manager**

```python
import uuid
import hashlib
from typing import List, Dict, Optional
from datetime import datetime

class KeyManager:
    def __init__(self, config: Dict):
        self.config = config
        self.keys = config.get("api_keys", [])
        
    def generate_key(self, name: str = "default") -> str:
        key = f"sk-{uuid.uuid4().hex}{uuid.uuid4().hex[:8]}"
        key_info = {
            "key": key,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "usage": {"daily": {}, "weekly": {}, "monthly": {}}
        }
        self.keys.append(key_info)
        self._save()
        return key
    
    def validate_key(self, key: str) -> bool:
        return any(k["key"] == key for k in self.keys)
    
    def delete_key(self, key: str) -> bool:
        self.keys = [k for k in self.keys if k["key"] != key]
        self._save()
        return True
    
    def get_all_keys(self) -> List[Dict]:
        return [{"key": k["key"], "name": k["name"], "created_at": k["created_at"]} for k in self.keys]
    
    def record_usage(self, key: str, endpoint: str):
        today = datetime.now().strftime("%Y-%m-%d")
        for k in self.keys:
            if k["key"] == key:
                if endpoint not in k["usage"]["daily"]:
                    k["usage"]["daily"][endpoint] = 0
                k["usage"]["daily"][endpoint] += 1
                self._save()
                break
    
    def get_stats(self, key: Optional[str] = None) -> Dict:
        if key:
            for k in self.keys:
                if k["key"] == key:
                    return k["usage"]
            return {}
        
        total = {"daily": {}, "weekly": {}, "monthly": {}}
        for k in self.keys:
            for period in total:
                for endpoint, count in k["usage"].get(period, {}).items():
                    total[period][endpoint] = total[period].get(endpoint, 0) + count
        return total
    
    def _save(self):
        self.config["api_keys"] = self.keys
        from .config import save_config
        save_config(self.config)
```

---

### Task 5: FastAPI 主服务

**Files:**
- Create: `host/src/api_server.py`
- Create: `host/templates/index.html`

**Step 1: 创建 API Server**

```python
import os
import io
import base64
from pathlib import Path
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Header, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Template

from .config import load_config, save_config
from .asr_engine import ASREngine
from .translate_engine import TranslationEngine
from .key_manager import KeyManager

app = FastAPI(title="SpeechMate API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = load_config()
key_manager = KeyManager(config)
asr_engine = ASREngine(config["asr_model"], config["device"])
translate_engine = TranslationEngine(config["translate_model"], config["device"])

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

@app.get("/", response_class=HTMLResponse)
async def index():
    template_path = TEMPLATES_DIR / "index.html"
    with open(template_path) as f:
        template = Template(f.read())
    
    models_info = {
        "asr": {
            "current": config["asr_model"],
            "available": ["base", "small", "medium", "large-v3"]
        },
        "translate": {
            "current": config["translate_model"],
            "available": ["m2m100-418M", "m2m100-1.2B"]
        },
        "device": config["device"]
    }
    
    return template.render(
        base_url=f"http://{config['host']}:{config['port']}",
        keys=key_manager.get_all_keys(),
        stats=key_manager.get_stats(),
        models=models_info
    )

@app.post("/api/v1/asr")
async def asr(
    audio: UploadFile = File(...),
    x_api_key: str = Header(...)
):
    if not key_manager.validate_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    key_manager.record_usage(x_api_key, "asr")
    
    audio_data = await audio.read()
    result = asr_engine.transcribe_audio_data(audio_data)
    
    return {"success": True, "data": result}

@app.post("/api/v1/translate")
async def translate(
    text: str = Form(...),
    src_lang: str = Form("zh"),
    tgt_lang: str = Form("en"),
    x_api_key: str = Header(...)
):
    if not key_manager.validate_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    key_manager.record_usage(x_api_key, "translate")
    
    result = translate_engine.translate(text, src_lang, tgt_lang)
    
    return {"success": True, "data": {"text": result}}

@app.get("/api/v1/models")
async def get_models():
    return {
        "asr": {
            "current": config["asr_model"],
            "available": [
                {"name": "base", "size": "140MB", "accuracy": "中", "speed": "快"},
                {"name": "small", "size": "290MB", "accuracy": "中高", "speed": "快"},
                {"name": "medium", "size": "1.5GB", "accuracy": "高", "speed": "中"},
                {"name": "large-v3", "size": "3.1GB", "accuracy": "最高", "speed": "中"}
            ]
        },
        "translate": {
            "current": config["translate_model"],
            "available": [
                {"name": "m2m100-418M", "size": "1.6GB", "speed": "中"},
                {"name": "m2m100-1.2B", "size": "2.5GB", "speed": "较慢"}
            ]
        }
    }

@app.post("/api/v1/models/switch")
async def switch_model(
    model_type: str = Form(...),
    model_name: str = Form(...),
    device: Optional[str] = Form(None)
):
    global asr_engine, translate_engine
    
    if model_type == "asr":
        asr_engine.unload_model()
        asr_engine = ASREngine(model_name, device or config["device"])
        config["asr_model"] = model_name
    elif model_type == "translate":
        translate_engine = TranslationEngine(model_name, device or config["device"])
        config["translate_model"] = model_name
    
    if device:
        config["device"] = device
    
    save_config(config)
    return {"success": True, "message": f"Switched to {model_name}"}

@app.get("/api/v1/stats")
async def get_stats(x_api_key: Optional[str] = Header(None)):
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config["host"], port=config["port"])
```

**Step 2: 创建 Web 管理页面模板**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SpeechMate 管理面板</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .nav-active { @apply border-b-2 border-blue-500 text-blue-600; }
    </style>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-8">SpeechMate 管理面板</h1>
        
        <!-- Base URL -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-semibold mb-4">服务信息</h2>
            <p class="text-gray-600">Base URL: <code class="bg-gray-100 px-2 py-1 rounded">{{ base_url }}</code></p>
        </div>
        
        <!-- API Keys -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-xl font-semibold">API Keys</h2>
                <button onclick="createKey()" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">创建新Key</button>
            </div>
            <div id="keysList" class="space-y-2">
                {% for key in keys %}
                <div class="flex justify-between items-center bg-gray-50 p-3 rounded">
                    <span class="font-mono text-sm">{{ key.key }}</span>
                    <span class="text-gray-500 text-sm">{{ key.name }}</span>
                    <button onclick="deleteKey('{{ key.key }}')" class="text-red-500 hover:text-red-700">删除</button>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <!-- Model Management -->
        <div class="bg-white rounded-lg shadow p-6 mb-6">
            <h2 class="text-xl font-semibold mb-4">模型管理</h2>
            
            <div class="mb-4">
                <label class="block text-gray-700 mb-2">语音识别模型 (ASR)</label>
                <select id="asrModel" class="w-full border rounded p-2">
                    {% for model in models.asr.available %}
                    <option value="{{ model.name }}" {% if model.name == models.asr.current %}selected{% endif %}>
                        {{ model.name }} - {{ model.size }} - {{ model.accuracy }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="mb-4">
                <label class="block text-gray-700 mb-2">翻译模型</label>
                <select id="translateModel" class="w-full border rounded p-2">
                    {% for model in models.translate.available %}
                    <option value="{{ model.name }}" {% if model.name == models.translate.current %}selected{% endif %}>
                        {{ model.name }} - {{ model.size }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="mb-4">
                <label class="block text-gray-700 mb-2">运行设备</label>
                <select id="device" class="w-full border rounded p-2">
                    <option value="cpu" {% if models.device == 'cpu' %}selected{% endif %}>CPU</option>
                    <option value="cuda" {% if models.device == 'cuda' %}selected{% endif %}>GPU (CUDA)</option>
                </select>
            </div>
            
            <button onclick="switchModel()" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">切换模型</button>
        </div>
        
        <!-- Stats -->
        <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold mb-4">使用统计</h2>
            <div class="grid grid-cols-3 gap-4">
                <div class="bg-blue-50 p-4 rounded">
                    <h3 class="font-semibold text-blue-600">总计调用</h3>
                    <p id="totalCalls" class="text-2xl font-bold">{{ stats.daily|length }}</p>
                </div>
            </div>
            <div class="mt-4">
                <h3 class="font-semibold mb-2">详细统计</h3>
                <pre id="statsDetail" class="bg-gray-50 p-4 rounded text-sm overflow-auto">{{ stats }}</pre>
            </div>
        </div>
    </div>
    
    <script>
        const baseUrl = '{{ base_url }}';
        
        async function createKey() {
            const response = await fetch('/api/v1/keys', { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                alert('API Key: ' + data.key);
                location.reload();
            }
        }
        
        async function deleteKey(key) {
            if (!confirm('确定删除?')) return;
            await fetch('/api/v1/keys/' + key, { method: 'DELETE' });
            location.reload();
        }
        
        async function switchModel() {
            const asrModel = document.getElementById('asrModel').value;
            const translateModel = document.getElementById('translateModel').value;
            const device = document.getElementById('device').value;
            
            const response = await fetch('/api/v1/models/switch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'model_type=asr&model_name=' + asrModel + '&device=' + device
            });
            
            const response2 = await fetch('/api/v1/models/switch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'model_type=translate&model_name=' + translateModel + '&device=' + device
            });
            
            alert('模型切换成功，请重启服务');
        }
    </script>
</body>
</html>
```

---

## Part 2: Client端实现

### Task 6: Electron 项目初始化

**Files:**
- Create: `client/package.json`
- Create: `client/tsconfig.json`
- Create: `client/vite.config.ts`
- Create: `client/tailwind.config.js`
- Create: `client/postcss.config.js`
- Create: `client/electron-builder.json`
- Create: `client/index.html`

**Step 1: 创建 package.json**

```json
{
  "name": "speechmate",
  "version": "1.0.0",
  "description": "Speech Recognition and Translation Assistant",
  "main": "dist-electron/main.js",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build && electron-builder",
    "build:win": "tsc && vite build && electron-builder --win --portable"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "electron": "^28.1.0",
    "electron-log": "^5.0.3",
    "axios": "^1.6.5",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "lucide-react": "^0.309.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "autoprefixer": "^10.4.17",
    "electron-builder": "^24.9.1",
    "postcss": "^8.4.33",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.11",
    "vite-plugin-electron": "^0.28.0",
    "vite-plugin-electron-renderer": "^0.14.5"
  },
  "build": {
    "appId": "com.speechmate.app",
    "productName": "SpeechMate",
    "directories": {
      "output": "release"
    },
    "win": {
      "target": [
        {
          "target": "portable",
          "arch": ["x64"]
        }
      ]
    },
    "portable": {
      "artifactName": "SpeechMate-Portable.exe"
    }
  }
}
```

**Step 2: 创建 Electron 主进程文件**

```typescript
// client/electron/main.ts
import { app, BrowserWindow, globalShortcut, Tray, Menu, nativeImage, ipcMain, clipboard } from 'electron';
import * as path from 'path';
import * as fs from 'fs';
import axios from 'axios';
import log from 'electron-log';

log.transports.file.level = 'info';
log.info('SpeechMate starting...');

let mainWindow: BrowserWindow | null = null;
let tray: Tray | null = null;
let isRecording = false;
let audioChunks: Buffer[] = [];

let config = {
  base_url: 'http://localhost:3456',
  api_key: '',
  hotkey_asr: 'alt',
  hotkey_translate_zh_en: 'shift',
  hotkey_translate_en_zh: 'shift+a'
};

function loadConfig() {
  const configPath = path.join(app.getPath('userData'), 'config.json');
  if (fs.existsSync(configPath)) {
    config = { ...config, ...JSON.parse(fs.readFileSync(configPath, 'utf-8')) };
  }
}

function saveConfig() {
  const configPath = path.join(app.getPath('userData'), 'config.json');
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 400,
    height: 500,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    resizable: false,
    minimizable: true,
    show: false
  });
  
  if (process.env.VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(process.env.VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }
  
  mainWindow.on('close', (event) => {
    event.preventDefault();
    mainWindow?.hide();
  });
}

function createTray() {
  const iconPath = path.join(__dirname, '../public/icon.png');
  let icon = nativeImage.createEmpty();
  
  if (fs.existsSync(iconPath)) {
    icon = nativeImage.createFromPath(iconPath);
  }
  
  tray = new Tray(icon.isEmpty() ? nativeImage.createFromDataURL('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAADRSURBVDiNpdMxTsNAEIXhf9cEokCFRINDcANuwAG4ATfgBpyAG3ADbkBHSEg0KKSI4MdZyRZ2d0MSBz7Jatsz/5md3dlRBhKRKrAGHCQSc4qU3gKPwF3CJvCW2AKuks4lXY8kXY4l3YxZ0uWYJd2NWdL9mCXdj1nS45glPY5Z0tOYJT2NWdLTmCU9jVnS85glPY9Z0suYJb2MWdLzmCW9jFnSy5glvYxZ0uuYJb2MWdLrmCW9jFnS65glvYxZ0uuYJb2MWdLrmCW9jFnS65glvYxZ0uuYJf0Df2FJp3B1pGkAAAAASUVORK5CYII=') : icon);
  
  const contextMenu = Menu.buildFromTemplate([
    { label: '显示主界面', click: () => mainWindow?.show() },
    { type: 'separator' },
    { label: '设置', click: () => mainWindow?.show() },
    { type: 'separator' },
    { label: '退出', click: () => { mainWindow?.destroy(); app.quit(); } }
  ]);
  
  tray.setToolTip('SpeechMate');
  tray.setContextMenu(contextMenu);
  tray.on('double-click', () => mainWindow?.show());
}

async function startRecording() {
  isRecording = true;
  mainWindow?.webContents.send('recording-status', true);
  log.info('Recording started');
}

async function stopRecording(mode: 'asr' | 'translate_zh_en' | 'translate_en_zh') {
  isRecording = false;
  mainWindow?.webContents.send('recording-status', false);
  
  try {
    let result: string;
    
    if (mode === 'asr') {
      const response = await axios.post(`${config.base_url}/api/v1/asr`, formData, {
        headers: { 'X-API-Key': config.api_key }
      });
      result = response.data.data.text;
    } else {
      const srcLang = mode === 'translate_zh_en' ? 'zh' : 'en';
      const tgtLang = mode === 'translate_zh_en' ? 'en' : 'zh';
      
      const response = await axios.post(`${config.base_url}/api/v1/translate`, 
        new URLSearchParams({ text: recognizedText, src_lang: srcLang, tgt_lang: tgtLang }),
        { headers: { 'X-API-Key': config.api_key, 'Content-Type': 'application/x-www-form-urlencoded' } }
      );
      result = response.data.data.text;
    }
    
    // Output result
    // Try to paste to active window, fallback to clipboard
    clipboard.writeText(result);
    log.info('Result:', result);
  } catch (error) {
    log.error('Error:', error);
  }
}

function registerHotkeys() {
  globalShortcut.unregisterAll();
  
  // Alt - ASR
  globalShortcut.register('Alt', () => {
    if (!isRecording) startRecording();
  });
  
  globalShortcut.register('Alt', () => {
    if (isRecording) stopRecording('asr');
  });
  
  // Shift - Translate ZH to EN
  globalShortcut.register('Shift', () => {
    if (!isRecording) startRecording();
  });
  
  globalShortcut.register('Shift', () => {
    if (isRecording) stopRecording('translate_zh_en');
  });
  
  // Shift+A - Translate EN to ZH  
  // This requires special handling as Shift+A is a combination
}

app.whenReady().then(() => {
  loadConfig();
  createWindow();
  createTray();
  registerHotkeys();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

ipcMain.handle('get-config', () => config);
ipcMain.handle('save-config', (_, newConfig) => {
  config = { ...config, ...newConfig };
  saveConfig();
  registerHotkeys();
  return true;
});
```

**Step 3: 创建 preload.ts**

```typescript
import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('electronAPI', {
  getConfig: () => ipcRenderer.invoke('get-config'),
  saveConfig: (config: any) => ipcRenderer.invoke('save-config', config),
  onRecordingStatus: (callback: (status: boolean) => void) => {
    ipcRenderer.on('recording-status', (_, status) => callback(status));
  }
});
```

**Step 4: 创建 React 组件**

```tsx
// client/src/App.tsx
import { useState, useEffect } from 'react';
import { Settings, Mic, Globe, Copy, Check } from 'lucide-react';

interface Config {
  base_url: string;
  api_key: string;
  hotkey_asr: string;
  hotkey_translate_zh_en: string;
  hotkey_translate_en_zh: string;
}

declare global {
  interface Window {
    electronAPI: {
      getConfig: () => Promise<Config>;
      saveConfig: (config: Partial<Config>) => Promise<boolean>;
      onRecordingStatus: (callback: (status: boolean) => void) => void;
    };
  }
}

function App() {
  const [config, setConfig] = useState<Config>({
    base_url: 'http://localhost:3456',
    api_key: '',
    hotkey_asr: 'alt',
    hotkey_translate_zh_en: 'shift',
    hotkey_translate_en_zh: 'shift+a'
  });
  const [isRecording, setIsRecording] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    window.electronAPI.getConfig().then(setConfig);
    window.electronAPI.onRecordingStatus(setIsRecording);
  }, []);

  const handleSave = async () => {
    await window.electronAPI.saveConfig(config);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-md mx-auto bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-6">
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Mic className="w-8 h-8" />
            SpeechMate
          </h1>
          <p className="text-blue-100 mt-1">语音识别 & 翻译助手</p>
        </div>

        <div className="p-6 space-y-6">
          {/* Recording Status */}
          <div className={`flex items-center justify-center p-4 rounded-lg ${isRecording ? 'bg-red-50 animate-pulse' : 'bg-gray-50'}`}>
            <Mic className={`w-8 h-8 ${isRecording ? 'text-red-500' : 'text-gray-400'}`} />
            <span className={`ml-2 font-medium ${isRecording ? 'text-red-600' : 'text-gray-500'}`}>
              {isRecording ? '录音中...' : '等待录音'}
            </span>
          </div>

          {/* Settings */}
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Base URL</label>
              <input
                type="text"
                value={config.base_url}
                onChange={(e) => setConfig({ ...config, base_url: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="http://localhost:3456"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
              <input
                type="password"
                value={config.api_key}
                onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="sk-xxx"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">快捷键配置</label>
              <div className="bg-gray-50 rounded-lg p-3 space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>语音识别:</span>
                  <kbd className="px-2 py-1 bg-white rounded border">{config.hotkey_asr}</kbd>
                </div>
                <div className="flex justify-between">
                  <span>中→英翻译:</span>
                  <kbd className="px-2 py-1 bg-white rounded border">{config.hotkey_translate_zh_en}</kbd>
                </div>
                <div className="flex justify-between">
                  <span>英→中翻译:</span>
                  <kbd className="px-2 py-1 bg-white rounded border">{config.hotkey_translate_en_zh}</kbd>
                </div>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            className={`w-full py-3 rounded-lg font-medium transition-all ${
              saved 
                ? 'bg-green-500 text-white' 
                : 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:from-blue-700 hover:to-indigo-700'
            }`}
          >
            {saved ? <span className="flex items-center justify-center gap-2"><Check className="w-5 h-5" /> 已保存</span> : '保存设置'}
          </button>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-3 text-center text-xs text-gray-500">
          按 Alt 识别 | 按 Shift 翻译(中→英) | 按 Shift+A 翻译(英→中)
        </div>
      </div>
    </div>
  );
}

export default App;
```

---

## Part 3: 测试与部署

### Task 7: 一键部署测试

**Step 1: 创建 Windows 批处理部署脚本**

```batch
@echo off
echo === SpeechMate Host 一键部署 ===

echo 创建虚拟环境...
python -m venv venv
call venv\Scripts\activate

echo 安装依赖...
pip install -r requirements.txt

echo 安装 ffmpeg...
choco install ffmpeg -y

echo 下载默认模型...
python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"

echo 启动服务...
python -m src.api_server

pause
```

**Step 2: 运行测试验证**

```bash
# 测试 API
curl -X POST http://localhost:3456/api/v1/keys -d "name=test"
curl http://localhost:3456/api/v1/models
curl http://localhost:3456/api/v1/stats

# 访问 Web 页面
# 浏览器打开 http://localhost:3456
```

---

## 部署指南

### Host 部署 (Windows/Linux)

```bash
cd host

# Windows
deploy.bat

# Linux
chmod +x deploy.sh
./deploy.sh
```

### Client 部署

```bash
cd client
npm install
npm run build:win
# 输出: release/SpeechMate-Portable.exe
```

---

## 使用说明

### Host 端
1. 运行 `deploy.bat` 或 `deploy.sh`
2. 打开浏览器访问 http://localhost:3456
3. 创建 API Key
4. 可在页面切换模型

### Client 端
1. 运行 `SpeechMate-Portable.exe`
2. 配置 Base URL 和 API Key
3. 保存设置
4. 使用快捷键:
   - Alt: 语音识别 → 输出文本
   - Shift: 中译英 → 输出文本
   - Shift+A: 英译中 → 输出文本
