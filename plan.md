# SpeechMate 开发计划

本文档列出 SpeechMate 项目的开发需求和任务清单。

---

## 项目状态

> **当前状态**: 核心模块已实现，需要安装依赖后测试运行

### 模块状态

| 模块 | 状态 | 说明 |
|------|------|------|
| Host API (FastAPI) | ✅ 完整 | 主程序和models模块已实现 |
| Host Web (Flask) | ✅ 完整 | Web管理界面代码完整 |
| Host Database | ✅ 完整 | SQLAlchemy数据库模块完整 |
| Host Models | ✅ 已创建 | ASR模型模块已实现 |
| Host Tests | ✅ 已创建 | pytest测试框架已创建 |
| Client GUI (PyQt5) | ✅ 完整 | 主窗口、托盘、录音指示器完整 |
| Client Recorder | ✅ 完整 | sounddevice录音模块完整 |
| Client Hotkey | ✅ 完整 | pynput快捷键监听完整 |
| Client API Client | ✅ 完整 | HTTP客户端完整 |
| Translation | ⏸️ 跳过 | 翻译模块后续实现 |

---

## 一、紧急修复 (P0) - 已完成

- [x] 创建 `host/models/__init__.py`
- [x] 创建 `host/models/asr_model.py` - faster-whisper ASR模型封装
- [x] 修改 `host/app/api/translate.py` - 返回"功能未实现"提示
- [x] 创建 `host/tests/` 目录和测试文件
- [x] 安装依赖: `pip install -r host/requirements.txt`
- [x] 运行测试: `python host/test_server.py` - 33 passed, 2 skipped
- [x] 验证 API 服务启动: `python host/start_server.py`
- [x] 创建安装脚本: `install.sh`, `install.bat`
- [x] 创建启动脚本: `run_host.sh`, `run_host.bat`, `run_client.sh`, `run_client.bat`

---

## 二、核心功能完善 (P1) - 已完成

### 2.1 Host 服务器

- [x] API 端点验证 (/health, /docs, /transcribe, /info)
- [x] 配置管理 (config.yaml 读写)
- [ ] 错误处理增强 (日志、统一格式、请求ID)

### 2.2 Web 管理界面

- [x] `host/web/templates/index.html` 完整 (CSS/JS内嵌)
- [x] API Key 管理 (创建/删除/禁用)
- [x] 使用统计查看
- [x] 模型配置切换

### 2.3 Client 客户端

- [x] UI 完整性 (主窗口、系统托盘、录音指示器)
- [x] 功能模块 (快捷键监听、录音、API客户端、文字输入)

---

## 三、翻译功能 (后续实现)

- [ ] 创建 `host/models/translation_model.py`
- [ ] 实现中英互译 (Helsinki-NLP/opus-mt)
- [ ] 启用翻译 API 端点

---

## 四、功能增强 (P2) (后续实现)

### 4.1 语音识别增强

- [ ] 音频预处理 (降噪、VAD、归一化)
- [ ] 支持更多语言 (ja, ko, fr, de)
- [ ] 识别结果后处理 (标点、格式化)

### 4.2 Client 功能增强

- [ ] 多语言UI (中/英)
- [ ] 录音历史记录
- [ ] 快捷键冲突检测
- [ ] 自动更新功能

---

## 五、性能优化 (P2) (后续实现)

### 5.1 服务器优化

- [ ] 模型缓存
- [ ] 请求队列和限流
- [ ] 异步处理 (Celery)
- [ ] 内存优化

### 5.2 客户端优化

- [ ] 录音缓冲优化
- [ ] 本地音频缓存
- [ ] 内存占用优化
- [ ] 启动速度优化

---

## 六、测试与文档 (P2)

### 6.1 测试框架

已创建测试文件:
- `host/tests/__init__.py`
- `host/tests/conftest.py` - pytest fixtures
- `host/tests/test_asr_model.py` - ASR模块测试
- `host/tests/test_config.py` - 配置测试
- `host/tests/test_database.py` - 数据库测试
- `host/pytest.ini` - pytest配置

### 6.2 文档

- [x] API文档 (FastAPI自动生成 `/docs`)
- [x] CLAUDE.md 项目指南
- [ ] 开发者指南
- [ ] 故障排除文档

---

## 七、发布准备 (P3)

### 7.1 客户端打包

- [ ] 完善 PyInstaller 配置
- [ ] 添加必要资源文件
- [ ] 解决依赖冲突
- [ ] 生成稳定可执行文件

### 7.2 版本发布

- [ ] 更新版本号
- [ ] 编写发布说明
- [ ] 打包 Release

---

## 八、未来规划 (长期) (后续实现)

- [ ] 翻译功能实现
- [ ] 多平台客户端 (macOS, Linux)
- [ ] 移动端 (iOS, Android)
- [ ] Web客户端
- [ ] 插件系统
- [ ] 语音合成 (TTS)
- [ ] 实时语音识别 (流式)
- [ ] 说话人分离 (Diarization)

---

## 技术栈

### Host 服务器

| 组件 | 技术 |
|------|------|
| API框架 | FastAPI |
| Web框架 | Flask |
| ASR引擎 | faster-whisper |
| 数据库 | SQLite + SQLAlchemy |
| 日志 | loguru |
| 测试 | pytest |

### Client 客户端

| 组件 | 技术 |
|------|------|
| GUI框架 | PyQt5 |
| 音频录制 | sounddevice |
| 快捷键 | pynput |
| HTTP客户端 | requests |
| 打包工具 | PyInstaller |

---

## 参考项目

- [Whisper-WebUI](https://github.com/jhj0517/Whisper-WebUI) - 测试框架参考
- [WhisperX](https://github.com/m-bain/whisperX) - Diarization
- [faster-whisper-server](https://github.com/nirnaim/faster-whisper-server) - SSE streaming
- [whisper-type](https://github.com/TryoTrix/whisper-type) - Windows热键听写

---

*最后更新: 2026-02-28*