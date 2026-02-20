# SpeechMate 完整设计方案

## 项目概述

SpeechMate 是一款运行在 Windows 上的语音识别和翻译助手，采用 Client-Server 架构：
- **Host端**：部署在 Windows/Linux 服务器，提供语音识别和翻译 API 服务及 Web 管理界面
- **Client端**：Windows 客户端，通过快捷键调用 Host 服务进行语音识别/翻译

---

## 一、系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         Host Server                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ Faster      │  │   m2m100   │  │    FastAPI Server       │ │
│  │ Whisper     │  │  Translation│  │  ┌─────────────────┐    │ │
│  │ (语音识别)   │  │   (翻译)    │  │  │ /api/v1/asr     │    │ │
│  │             │  │             │  │  │ /api/v1/translate│   │ │
│  │ CPU/GPU     │  │  CPU/GPU   │  │  │ /api/v1/models   │    │ │
│  │             │  │             │  │  │ /api/v1/stats   │    │ │
│  └─────────────┘  └─────────────┘  │  │ /api/v1/keys    │    │ │
│                                     │  └─────────────────┘    │ │
│                                     │  ┌─────────────────┐    │ │
│                                     │  │   Web 管理页面   │    │ │
│                                     │  │  (流量统计/模型) │    │ │
│                                     │  └─────────────────┘    │ │
│                                     └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTP API (Base URL + API Key)
                              │
┌─────────────────────────────────────────────────────────────────┐
│                       Windows Client                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Electron App                          │  │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐   │  │
│  │  │ React UI   │  │  Tray Icon │  │  Floating Icon   │   │  │
│  │  │ (设置界面)  │  │ (任务栏)    │  │   (录音状态)      │   │  │
│  │  └────────────┘  └────────────┘  └──────────────────┘   │  │
│  │  ┌─────────────────────────────────────────────────────┐│  │
│  │  │              Global Hotkey Listener                ││  │
│  │  │  Alt → 录音→ASR→输出文本                            ││  │
│  │  │  Shift → 录音→翻译(中→英)                          ││  │
│  │  │  Shift+A → 录音→翻译(英→中)                        ││  │
│  │  └─────────────────────────────────────────────────────┘│  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、技术栈

### Host端
- **模型推理**: Faster Whisper (语音识别), m2m100 (翻译)
- **API框架**: FastAPI
- **部署方式**: Python虚拟环境 + Shell脚本

### Client端
- **框架**: Electron + React 18
- **样式**: Tailwind CSS + shadcn/ui
- **打包**: electron-builder (Portable EXE)

---

## 三、端口配置

| 服务 | 端口 |
|------|------|
| Host API + Web管理页面 | **3456** |

---

## 四、API设计

| Endpoint | Method | 说明 |
|----------|--------|------|
| `/api/v1/asr` | POST | 语音识别 (audio → text) |
| `/api/v1/translate` | POST | 翻译 (text → translated text) |
| `/api/v1/models` | GET | 获取可选模型列表 |
| `/api/v1/models/switch` | POST | 切换运行模型 |
| `/api/v1/stats` | GET | 获取流量统计 |
| `/api/v1/keys` | GET/POST/DELETE | API Key管理 |
| `/` | GET | Web管理页面 |

---

## 五、快捷键设计

| 快捷键 | 功能 |
|--------|------|
| Alt (按住→松开) | 语音识别 → 输出文本 |
| Shift (按住→松开) | 录音 → 翻译(中→英) → 输出 |
| Shift+A (按住A→松开) | 录音 → 翻译(英→中) → 输出 |

**输出规则**：
- 光标在文本输入框 → 模拟键盘输入
- 光标不在文本输入框 → 写入剪切板

---

## 六、支持模型

### 语音识别 (Faster Whisper)
| 模型名 | 大小 | 精度 |
|--------|------|------|
| base | ~140MB | 中 |
| small | ~290MB | 中高 |
| medium | ~1.5GB | 高 |
| large-v3 | ~3.1GB | 最高 |

### 翻译 (m2m100)
| 模型名 | 大小 |
|--------|------|
| m2m100-418M | ~1.6GB |
| m2m100-1.2B | ~2.5GB |

---

## 七、部署脚本

### deploy.sh (一键部署)
1. 创建Python虚拟环境
2. 安装系统依赖 (ffmpeg)
3. 安装Python依赖
4. 下载默认模型
5. 启动FastAPI服务

### stop_server.sh (停止服务)
1. 查找并终止相关进程
2. 释放端口占用

---

## 八、数据存储

**Host配置**: `config.json`
```json
{
  "host": "0.0.0.0",
  "port": 3456,
  "asr_model": "base",
  "translate_model": "m2m100-418M",
  "device": "cpu",
  "api_keys": ["sk-xxx"],
  "stats": {...}
}
```

**Client配置**: `%APPDATA%/SpeechMate/config.json`
```json
{
  "base_url": "http://localhost:3456",
  "api_key": "sk-xxx",
  "hotkey_asr": "alt",
  "hotkey_translate_zh_en": "shift",
  "hotkey_translate_en_zh": "shift+a"
}
```

---

## 九、验收标准

1. Host一键部署成功，自动启动Web服务
2. Web管理页面显示流量统计、模型信息、API Key管理
3. Client可在任意文本框使用快捷键录音识别/翻译
4. 支持Alt(识别)、Shift(中→英)、Shift+A(英→中)
5. 未聚焦文本框时输出到剪切板
6. Tray菜单和浮动图标正常显示
7. Portable EXE可独立运行
