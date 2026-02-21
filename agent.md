# SpeechMate - 语音识别与翻译助手

## 项目概述

SpeechMate 是一个语音识别和翻译助手应用程序，包含 Host 端（服务器）和 Client 端（Windows客户端）两部分。

### 核心功能
- **语音识别**：按住快捷键录音，松开后将语音转为文字输入到光标位置
- **语音翻译**：录音后直接翻译成目标语言并输入
- **多语言支持**：支持中文和英文的识别与互译

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         SpeechMate System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐         ┌──────────────────────┐      │
│  │     Client (Windows) │  HTTP   │    Host Server       │      │
│  │                      │◄───────►│    (Windows/Linux)   │      │
│  │  ┌────────────────┐  │  REST   │                      │      │
│  │  │  PyQt5 GUI     │  │   API   │  ┌────────────────┐  │      │
│  │  │  - 系统托盘    │  │         │  │  FastAPI       │  │      │
│  │  │  - 录音状态    │  │         │  │  - /transcribe │  │      │
│  │  │  - 配置界面    │  │         │  │  - /translate  │  │      │
│  │  └────────────────┘  │         │  │  - /stats      │  │      │
│  │  ┌────────────────┐  │         │  └────────────────┘  │      │
│  │  │  录音模块      │  │         │  ┌────────────────┐  │      │
│  │  │  - sounddevice │  │         │  │  AI Models     │  │      │
│  │  │  - 音频处理    │  │         │  │  - Whisper ASR │  │      │
│  │  └────────────────┘  │         │  │  - Translation │  │      │
│  │  ┌────────────────┐  │         │  └────────────────┘  │      │
│  │  │  快捷键监听    │  │         │  ┌────────────────┐  │      │
│  │  │  - pynput      │  │         │  │  Web Admin     │  │      │
│  │  └────────────────┘  │         │  │  - Flask       │  │      │
│  └──────────────────────┘         │  │  - 统计/管理   │  │      │
│                                   │  └────────────────┘  │      │
│                                   └──────────────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 目录结构

```
speechmate/
├── host/                          # Host 服务器端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI 主入口
│   │   ├── config.py             # 配置管理
│   │   ├── database.py           # SQLite 数据库
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── transcribe.py     # 语音识别 API
│   │       ├── translate.py      # 翻译 API
│   │       └── stats.py          # 统计 API
│   ├── models/
│   │   ├── __init__.py
│   │   ├── asr_model.py          # ASR 模型管理
│   │   └── translation_model.py  # 翻译模型管理
│   ├── web/
│   │   ├── __init__.py
│   │   ├── app.py                # Flask Web 管理界面
│   │   ├── templates/
│   │   │   └── index.html
│   │   └── static/
│   │       ├── css/
│   │       └── js/
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py
│   ├── start_server.py           # 一键启动脚本
│   ├── stop_server.py            # 停止服务脚本
│   ├── requirements.txt          # Python 依赖
│   └── README.md
│
├── client/                        # Windows 客户端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # 主程序入口
│   │   ├── config.py             # 客户端配置
│   │   ├── recorder.py           # 录音模块
│   │   ├── hotkey.py             # 快捷键监听
│   │   ├── api_client.py         # API 客户端
│   │   └── text_input.py         # 文本输入处理
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py        # 主窗口
│   │   ├── settings_dialog.py    # 设置对话框
│   │   ├── tray_icon.py          # 系统托盘
│   │   └── recording_indicator.py # 录音状态指示器
│   ├── resources/
│   │   ├── icons/
│   │   └── styles/
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py
│   ├── build.py                  # PyInstaller 打包脚本
│   ├── requirements.txt
│   └── README.md
│
├── docs/
│   ├── deployment_guide.md       # 部署指南
│   └── user_manual.md            # 使用手册
│
└── agent.md                       # 本文档
```

---

## 技术选型

### Host 端

| 组件 | 技术选择 | 说明 |
|------|----------|------|
| API 框架 | FastAPI | 高性能异步框架，自动生成 API 文档 |
| Web 管理界面 | Flask + Jinja2 | 轻量级，易于部署 |
| 语音识别模型 | faster-whisper | OpenAI Whisper 的高效实现 |
| 翻译模型 | Helsinki-NLP/opus-mt | 开源翻译模型，支持多语言 |
| 数据库 | SQLite | 轻量级，无需额外安装 |
| 模型推理 | PyTorch + CUDA (可选) | 支持 CPU/GPU |

### Client 端

| 组件 | 技术选择 | 说明 |
|------|----------|------|
| GUI 框架 | PyQt5 | 功能强大，跨平台 |
| 录音 | sounddevice | 低延迟音频采集 |
| 快捷键监听 | pynput | 全局热键支持 |
| HTTP 客户端 | requests | 简单易用 |
| 打包工具 | PyInstaller | 生成独立 exe |

---

## API 设计

### 语音识别 API

```
POST /api/v1/transcribe
Headers: X-API-Key: <api_key>
Body: multipart/form-data
  - audio: 音频文件 (wav/mp3)
  - language: 语言代码 (zh/en)
Response:
  {
    "text": "识别的文本",
    "language": "检测到的语言",
    "duration": 2.5
  }
```

### 翻译 API

```
POST /api/v1/translate
Headers: X-API-Key: <api_key>
Body: multipart/form-data
  - audio: 音频文件 (wav/mp3)
  - source_lang: 源语言 (zh/en)
  - target_lang: 目标语言 (en/zh)
Response:
  {
    "original_text": "原文",
    "translated_text": "译文",
    "source_lang": "zh",
    "target_lang": "en"
  }
```

### 统计 API

```
GET /api/v1/stats
Headers: X-API-Key: <admin_api_key>
Response:
  {
    "api_keys": [
      {
        "key": "xxx",
        "name": "user1",
        "daily_stats": {...},
        "total_calls": 100
      }
    ]
  }
```

---

## 支持的开源模型

### 语音识别模型 (ASR)

| 模型 | 大小 | 速度 | 精度 | 推荐场景 |
|------|------|------|------|----------|
| faster-whisper-tiny | 39MB | 极快 | 一般 | 快速响应 |
| faster-whisper-base | 74MB | 快 | 较好 | 平衡选择 |
| faster-whisper-small | 244MB | 中等 | 好 | 推荐默认 |
| faster-whisper-medium | 769MB | 较慢 | 很好 | 高精度 |
| faster-whisper-large-v3 | 1.5GB | 慢 | 最好 | 最高精度 |

### 翻译模型

| 模型 | 大小 | 方向 | 说明 |
|------|------|------|------|
| Helsinki-NLP/opus-mt-zh-en | 300MB | 中→英 | 中文翻译英文 |
| Helsinki-NLP/opus-mt-en-zh | 300MB | 英→中 | 英文翻译中文 |

---

## 快捷键设计

| 快捷键 | 功能 | 说明 |
|--------|------|------|
| Alt (按住) | 语音识别 | 松开后识别并输入文本 |
| Shift (按住) | 中译英 | 录音后翻译成英文 |
| Shift+A (按住) | 英译中 | 录音后翻译成中文 |
| 可自定义 | 用户配置 | 在设置界面修改 |

---

## 部署方式

### Host 端一键部署

```bash
# Windows
python start_server.py

# Linux
python3 start_server.py
```

脚本会自动：
1. 创建 Python 虚拟环境
2. 安装所有依赖
3. 下载必要的模型
4. 启动 API 服务和 Web 管理界面

### Client 端使用

1. 运行 `speechmate_client.exe`
2. 配置服务器 URL 和 API Key
3. 设置快捷键
4. 最小化到系统托盘，随时可用

---

## 默认配置

### Host 端默认值

- API 服务端口: 8000
- Web 管理端口: 5000
- 默认 API Key: 自动生成
- 默认模型: faster-whisper-small

### Client 端默认值

- 默认服务器: http://localhost:8000
- 语音识别快捷键: Alt
- 中译英快捷键: Shift
- 英译中快捷键: Shift+A

---

## 开发计划

- [x] 项目架构设计
- [ ] Host 端核心服务实现
- [ ] Host 端 Web 管理界面
- [ ] 一键部署脚本
- [ ] Client 端 GUI 实现
- [ ] 系统托盘和录音指示器
- [ ] 功能测试
- [ ] 文档完善
- [ ] GitHub 发布

---

## 版本历史

### v1.0.0 (2024-02)
- 初始版本发布
- 支持中英文语音识别和翻译
- Web 管理界面
- Windows 客户端
