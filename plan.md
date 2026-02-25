# SpeechMate 开发计划

本文档详细列出 SpeechMate 项目的开发需求和任务清单。

---

## 项目状态

> ⚠️ **当前状态**: 项目存在已知问题，正在调试中

根据代码分析，项目核心架构已搭建完成，但存在以下关键缺失：

---

## 一、紧急修复 (P0)

### 1.1 模型模块缺失

**问题**: API 文件引用了 `models.asr_model` 和 `models.translation_model`，但 `host/models/` 目录不存在

**需要实现**:

- [ ] 创建 `host/models/__init__.py`
- [ ] 实现 `host/models/asr_model.py`:
  - `get_asr_model(model_name, device, compute_type)` - 加载 Whisper 模型
  - `transcribe_audio(audio_path, model_name, device, language)` - 语音转文字
  - `get_audio_duration(audio_path)` - 获取音频时长
  - `unload_model()` - 卸载模型释放内存
  
- [ ] 实现 `host/models/translation_model.py`:
  - `translate_text(text, source_lang, target_lang)` - 文本翻译
  - 模型: `Helsinki-NLP/opus-mt-zh-en` 和 `Helsinki-NLP/opus-mt-en-zh`

### 1.2 测试验证

- [ ] 修复后运行 `python host/test_server.py` 验证所有测试通过
- [ ] 确保 `test_imports`、`test_config`、`test_database` 全部通过
- [ ] 测试 ASR 模型加载（需要网络下载模型）

---

## 二、核心功能完善 (P1)

### 2.1 Host 服务器

- [ ] **API 健康检查**: 确保 `/health` 端点正常返回
- [ ] **API 文档**: 验证 `/docs` 端点可用
- [ ] **模型热加载**: 实现模型切换不需要重启服务
- [ ] **错误处理**: 完善所有 API 的异常处理和日志

### 2.2 Web 管理界面

- [ ] 检查 Flask Web 应用完整性
- [ ] 验证 `host/web/templates/index.html` 存在
- [ ] 添加 Web 静态资源 (CSS/JS) - 如缺失
- [ ] 测试 `http://localhost:5000` 访问
- [ ] 实现 API Key 管理界面功能

### 2.3 Client 客户端

- [ ] 验证主窗口 UI 完整性 (`client/ui/main_window.py`)
- [ ] 检查系统托盘功能 (`client/ui/tray_icon.py`)
- [ ] 检查录音指示器 (`client/ui/recording_indicator.py`)
- [ ] 实现设置对话框 - 如缺失

---

## 三、功能增强 (P2)

### 3.1 语音识别增强

- [ ] 添加支持更多 Whisper 模型 (medium, large-v3)
- [ ] 实现批量音频处理
- [ ] 添加音频预处理 (降噪、静音检测)
- [ ] 支持更多语言 (日语、韩语等)

### 3.2 翻译增强

- [ ] 添加更多翻译模型支持
- [ ] 实现翻译缓存减少重复请求
- [ ] 添加翻译质量评分

### 3.3 Client 功能增强

- [ ] 添加多语言 UI 支持 (中/英)
- [ ] 实现录音历史记录
- [ ] 添加快捷键冲突检测
- [ ] 实现自动更新功能

---

## 四、性能优化 (P2)

### 4.1 服务器优化

- [ ] 实现模型缓存，避免重复加载
- [ ] 添加请求队列和限流
- [ ] 实现异步处理 (后台任务)
- [ ] 优化音频文件处理流程

### 4.2 客户端优化

- [ ] 优化录音缓冲，减少延迟
- [ ] 实现本地音频缓存
- [ ] 减少内存占用

---

## 五、测试与文档 (P2)

### 5.1 测试完善

- [ ] 添加单元测试覆盖关键函数
- [ ] 添加集成测试覆盖 API 流程
- [ ] 添加端到端测试
- [ ] 建立 CI/CD 流程

### 5.2 文档完善

- [ ] 完善 API 文档
- [ ] 添加开发者指南
- [ ] 添加故障排除文档
- [ ] 录制使用教程视频

---

## 六、发布准备 (P3)

### 6.1 版本发布

- [ ] 修复所有已知问题
- [ ] 完成功能测试
- [ ] 更新版本号
- [ ] 打包 Release 版本
- [ ] 编写发布说明

### 6.2 客户端打包

- [ ] 完善 PyInstaller 打包配置
- [ ] 添加必要的资源文件
- [ ] 解决依赖冲突
- [ ] 生成稳定的 `SpeechMate.exe`

---

## 七、未来规划 (长期)

- [ ] **多平台支持**: 开发 macOS/Linux 客户端
- [ ] **移动端**: 开发 iOS/Android 版本
- [ ] **Web 客户端**: 开发浏览器版本
- [ ] **团队协作**: 添加多用户管理和权限控制
- [ ] **插件系统**: 支持自定义 ASR/翻译后端
- [ ] **语音合成**: 添加 TTS 功能

---

## 任务优先级说明

| 优先级 | 说明 |
|--------|------|
| P0 | 紧急 - 项目无法运行 |
| P1 | 高优先级 - 核心功能不完整 |
| P2 | 中优先级 - 功能增强和优化 |
| P3 | 低优先级 - 发布准备 |

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'Add xxx'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

---

*最后更新: 2024*
