# SpeechMate - 语音识别与翻译助手

SpeechMate 是一个开源的语音识别和翻译助手应用程序，包含服务器端（Host）和客户端（Client）两部分。

## 功能特点

- 🎤 **语音识别**: 按住快捷键说话，松开后自动转文字
- 🌐 **语音翻译**: 支持中英互译（待补充）
- ⌨️ **自动输入**: 识别/翻译的文字自动输入到光标位置，如果不在输入状态下则自动输入到系统剪切板中
- 📊 **Web 管理**: 提供 Web 界面管理 API Key 和查看统计
- 🔧 **模型可选**: 支持多种大小的 Whisper 模型
- 💻 **跨平台**: Host 支持 Windows 和 Linux

## 后续功能

### SpeechMate 阶段
- 🎨 **更好看的 Client 界面**: 现代化 UI 设计，支持主题切换、动画效果
- 🔍 **语音调用搜索引擎**: 通过语音快速搜索 Google、Bing、百度等
- 🤖 **语音调用 AI 大模型**: 集成 ChatGPT、Claude、通义千问等，语音提问直接获取回答
- 💬 **语音对话模式**: 连续语音交互，支持多轮对话

### Agent 阶段
- 🧚 **桌面精灵 Aurelia**: 可爱的桌面虚拟助手，具有表情动画和语音交互能力
- 🎯 **智能任务执行**: 语音控制系统操作、文件管理、应用启动等
- 📅 **日程管理**: 语音创建提醒、日程安排
- 🌐 **多模态交互**: 结合视觉识别，实现更智能的桌面助手体验

## 系统架构

```
┌─────────────────┐         ┌─────────────────┐
│  Client (Win)   │  HTTP   │   Host Server   │
│  - PyQt5 GUI    │◄───────►│   - FastAPI     │
│  - 系统托盘     │         │   - Web Admin   │
│  - 录音指示器   │         │   - AI Models   │
└─────────────────┘         └─────────────────┘
```

## 快速开始

### 一键启动 (推荐)

```bash
# Windows
scripts\install.bat      # 首次安装
scripts\start_all.bat    # 启动所有服务
scripts\stop_all.bat     # 停止所有服务

# Linux/Mac
./scripts/install.sh
./scripts/start_all.sh
./scripts/stop_all.sh
```

### 单独启动

#### Host 服务器

```bash
# Windows
scripts\run_host.bat

# Linux/Mac
./scripts/run_host.sh
```

#### Client 客户端

```bash
# Windows
scripts\run_client.bat

# Linux/Mac
./scripts/run_client.sh
```

## 目录结构

```
speechmate/
├── host/                   # 服务器端
│   ├── app/               # FastAPI 应用
│   ├── models/            # 模型管理
│   ├── web/               # Web 管理界面
│   ├── start_server.py    # 一键启动
│   └── stop_server.py     # 停止服务
├── client/                 # 客户端
│   ├── app/               # 应用逻辑
│   ├── ui/                # PyQt5 界面
│   ├── build.py           # 打包脚本
│   └── requirements.txt
├── scripts/                # 脚本工具
│   ├── install.bat/sh     # 一键安装
│   ├── run_host.bat/sh    # 启动服务器
│   ├── run_client.bat/sh  # 启动客户端
│   ├── start_all.bat/sh   # 启动所有服务
│   └── stop_all.bat/sh    # 停止所有服务
├── docs/                   # 文档
│   ├── deployment_guide.md
│   └── user_manual.md
└── README.md
```

## 默认快捷键

| 快捷键 | 功能 |
|--------|------|
| Alt (按住) | 语音识别 |
| Shift (按住) | 中文译英文 |
| Shift+A (按住) | 英文译中文 |

## 支持的模型

| 模型 | 大小 | 速度 | 精度 |
|------|------|------|------|
| tiny | 39MB | 极快 | 一般 |
| base | 74MB | 快 | 较好 |
| small | 244MB | 中等 | 好 (推荐) |
| medium | 769MB | 较慢 | 很好 |
| large-v3 | 1.5GB | 慢 | 最好 |

## 端口说明

- `8000`: API 服务端口
- `5000`: Web 管理界面端口

## 技术栈

### Host
- FastAPI - API 框架
- Flask - Web 管理界面
- faster-whisper - 语音识别
- Helsinki-NLP/opus-mt - 翻译

### Client
- PyQt5 - GUI 框架
- sounddevice - 音频录制
- pynput - 快捷键监听
- PyInstaller - 打包工具

## 文档

- [部署指南](docs/deployment_guide.md)
- [使用手册](docs/user_manual.md)
- [架构设计](agent.md)

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
