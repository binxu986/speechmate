# SpeechMate 项目构建文档

## 项目概述

SpeechMate 是一款运行在 Windows 上的语音识别和翻译助手，采用 Client-Server 架构：
- **Host端**：部署在 Windows/Linux 服务器，提供语音识别和翻译 API 服务及 Web 管理界面
- **Client端**：Windows 客户端，通过快捷键调用 Host 服务进行语音识别/翻译

## 技术栈

### Host端
- Python 3.9+
- FastAPI - API 框架
- Faster Whisper - 语音识别模型
- m2m100 - 翻译模型

### Client端
- Electron 28
- React 18
- Tailwind CSS
- TypeScript
- Vite

## 项目结构

```
SpeechMate/
├── host/                      # Host服务端
│   ├── config.py             # 配置文件
│   ├── requirements.txt      # Python依赖
│   ├── deploy.bat            # Windows一键部署脚本
│   ├── deploy.sh             # Linux一键部署脚本
│   ├── stop_server.bat       # Windows停止服务脚本
│   ├── stop_server.sh        # Linux停止服务脚本
│   ├── src/
│   │   ├── __init__.py
│   │   ├── asr_engine.py     # 语音识别引擎
│   │   ├── translate_engine.py # 翻译引擎
│   │   ├── key_manager.py     # API Key管理
│   │   └── api_server.py     # FastAPI主服务
│   └── templates/
│       └── index.html        # Web管理页面
│
├── client/                    # Client客户端
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── electron/
│   │   ├── main.ts           # Electron主进程
│   │   └── preload.ts        # 预加载脚本
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       └── index.css
│
└── docs/
    └── plans/
        └── 2026-02-20-speechmate-design.md
```

## Host端部署

### Windows 一键部署

1. 进入 host 目录：
```bash
cd host
```

2. 运行部署脚本：
```bash
deploy.bat
```

3. 脚本会自动：
   - 创建 Python 虚拟环境
   - 安装依赖 (fastapi, faster-whisper, transformers等)
   - 安装 ffmpeg (如未安装)
   - 下载默认模型 (Faster Whisper base)
   - 启动服务

4. 服务启动后，访问 http://localhost:3456 查看管理界面

### Linux 一键部署

```bash
cd host
chmod +x deploy.sh
./deploy.sh
```

### 停止 Host 服务

```bash
# Windows
cd host
stop_server.bat

# Linux
cd host
./stop_server.sh
```

### 手动启动/停止

```bash
cd host
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux
python -m src.api_server
```

## Client端构建

### 开发模式

```bash
cd client
npm install
npm run dev
```

### 构建 Portable EXE

```bash
cd client
npm install
npm run build:win
```

构建完成后，EXE 文件位于 `client/release/SpeechMate-Portable.exe`

## 功能说明

### Host端功能

1. **API 服务** (端口: 3456)
   - `POST /api/v1/asr` - 语音识别
   - `POST /api/v1/translate` - 翻译
   - `GET /api/v1/models` - 获取模型列表
   - `POST /api/v1/models/switch` - 切换模型
   - `GET /api/v1/stats` - 获取使用统计
   - `GET/POST/DELETE /api/v1/keys` - API Key管理
   - `GET /` - Web管理页面

2. **Web管理页面**
   - 显示 Base URL
   - API Key 创建/删除
   - 流量统计 (日/周/月)
   - 模型切换 (ASR/翻译模型)
   - 运行设备选择 (CPU/GPU)

### Client端功能

1. **快捷键**
   - Alt: 语音识别 → 输出文本
   - Shift: 中译英 → 输出文本
   - Shift+A: 英译中 → 输出文本

2. **输出方式**
   - 光标在文本框 → 输出到文本框
   - 光标不在文本框 → 复制到剪贴板

3. **设置**
   - Base URL 配置
   - API Key 配置
   - 快捷键显示

## API 使用方式

### 语音识别

```bash
curl -X POST http://localhost:3456/api/v1/asr \
  -H "X-API-Key: sk-xxx" \
  -F "audio=@audio.wav"
```

### 翻译

```bash
curl -X POST http://localhost:3456/api/v1/translate \
  -H "X-API-Key: sk-xxx" \
  -d "text=Hello&src_lang=en&tgt_lang=zh"
```

## 配置说明

### Host 配置 (host/config.json)

```json
{
  "host": "0.0.0.0",
  "port": 3456,
  "asr_model": "base",
  "translate_model": "m2m100-418M",
  "device": "cpu",
  "api_keys": [],
  "stats": {}
}
```

### Client 配置

首次运行时会自动在用户目录创建配置：
- Windows: `%APPDATA%/SpeechMate/config.json`

## 模型说明

### 语音识别 (Faster Whisper)

| 模型 | 大小 | 精度 | 推荐场景 |
|------|------|------|----------|
| base | ~140MB | 中 | 快速测试 |
| small | ~290MB | 中高 | 日常使用 |
| medium | ~1.5GB | 高 | 精度要求高 |
| large-v3 | ~3.1GB | 最高 | 最高精度 |

### 翻译 (m2m100)

| 模型 | 大小 | 速度 |
|------|------|------|
| m2m100-418M | ~1.6GB | 中 |
| m2m100-1.2B | ~2.5GB | 较慢 |

## 常见问题

### 1. 端口被占用

修改 `host/config.json` 中的 port 值，或运行 `stop_server.bat` 停止现有服务。

### 2. 模型下载慢

首次运行会自动下载模型，可手动下载后放到对应目录。

### 3. Client 连接失败

确保：
- Host 服务已启动
- Base URL 正确
- API Key 正确

## 版本信息

- SpeechMate v1.0.0
- 构建日期: 2026-02-20
