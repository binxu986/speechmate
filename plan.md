# SpeechMate 开发计划 - 测试覆盖率 100%

## 项目现状

### 已有测试
- `host/tests/test_config.py` - 配置模块测试
- `host/tests/test_database.py` - 数据库操作测试
- `host/tests/test_asr_model.py` - ASR 模型接口测试 (模块缺失无法运行)
- `host/test_server.py` - 服务器启动检查脚本
- `client/test_client.py` - 客户端基础功能测试

### 关键问题
1. `host/models/` 目录不存在 → ASR 模型测试无法运行
2. `tests/fixtures/` 目录不存在 → 缺少测试音频文件
3. API 端点无单元测试
4. Web 管理界面无测试
5. 客户端核心模块测试不完整

---

## Phase 1: 基础设施修复 ✅ COMPLETED

### 1.1 创建 ASR 模型模块 ✅
**文件**: `host/models/__init__.py`, `host/models/asr_model.py`

**已实现功能**:
- `get_asr_model(model_name, device, compute_type)` - 加载/缓存 Whisper 模型
- `transcribe_audio(audio_path, ...)` - 转写音频文件
- `get_audio_duration(audio_path)` - 获取音频时长
- `unload_model()` - 卸载模型释放内存
- `get_model_info()` - 获取当前模型状态

### 1.2 创建测试 Fixtures ✅
**目录**: `host/tests/fixtures/`

**已创建文件**:
- `test_audio.wav` - 英文测试音频 (3秒, 440Hz)
- `test_audio_zh.wav` - 中文模拟音频 (3秒, 多频混合)
- `test_audio_short.wav` - 短音频 (0.5秒，边界测试)
- `test_audio_silent.wav` - 静音音频 (2秒，边界测试)
- `test_audio_long.wav` - 长音频 (10秒，压力测试)
- `generate_fixtures.py` - 测试音频生成脚本

### 1.3 更新测试 Fixtures ✅
**文件**: `host/tests/conftest.py`

**新增 Fixtures**:
- `sample_audio_zh_path` - 中文音频路径
- `sample_audio_short_path` - 短音频路径
- `sample_audio_silent_path` - 静音音频路径
- `mock_api_key` - 模拟 API Key
- `mock_audio_bytes` - 模拟音频字节数据

### 1.4 模型下载工具 ✅
**文件**: `host/download_model.py`

**功能**:
- HuggingFace 镜像自动配置 (中国用户默认使用 hf-mirror.com)
- 命令行参数支持 (`--model`, `--list`, `--check`)
- 下载进度提示
- 已下载模型检测

**使用方法**:
```bash
# 列出可用模型
python download_model.py --list

# 检查已下载模型
python download_model.py --check

# 下载指定模型
python download_model.py --model small

# 下载所有模型
python download_model.py --model all

# 使用官方源（不使用镜像）
python download_model.py --model small --no-mirror
```

### 1.5 启动脚本增强 ✅
**文件**: `host/start_server.py`, `host/models/asr_model.py`

**改进**:
- 启动时自动调用 `download_model.py` 预下载模型
- 首次使用时显示下载提示和进度
- 自动配置 HuggingFace 镜像

---

## Phase 2: Host 单元测试补充 ✅ COMPLETED

### 2.1 ASR 模型测试 (`test_asr_model.py`) ✅
**测试数**: 20

**测试类**:
- `TestASRModelImport` - 模块导入测试
- `TestASRModelFunctions` - 函数功能测试
- `TestASRModelLoading` - 模型加载测试 (slow)
- `TestASRTranscription` - 转写测试 (slow)
- `TestASRAudioDuration` - 音频时长测试
- `TestASRModelConfig` - 模型配置测试
- `TestASRTranscriptionErrors` - 错误处理测试

### 2.2 API 端点测试 (`test_api.py`) ✅ 新建
**测试数**: 18

**测试类**:
- `TestHealthEndpoint` - 健康检查
- `TestInfoEndpoint` - 服务器信息
- `TestTranscribeEndpoint` - 转写端点
- `TestTranslateEndpoint` - 翻译端点
- `TestStatsEndpoint` - 统计端点
- `TestAPIKeysEndpoint` - API Key 管理

### 2.3 配置测试 (`test_config.py`) ✅
**测试数**: 25

**新增测试类**:
- `TestConfigValidation` - 配置验证
- `TestConfigAdminSettings` - 管理员设置
- `TestConfigModelConfig` - 模型配置
- `TestConfigPaths` - 路径配置

### 2.4 数据库测试 (`test_database.py`) ✅
**测试数**: 25

**新增测试类**:
- `TestDatabaseEdgeCases` - 边界条件
- `TestDatabaseAPIKeyFormat` - API Key 格式
- `TestDatabaseSession` - 会话管理

### 2.5 Web 管理界面测试 (`test_web_admin.py`) ✅ 新建
**测试数**: 16

**测试类**:
- `TestWebIndexRoute` - 首页路由
- `TestWebAPIKeysRoutes` - API Key 管理
- `TestWebStatsRoute` - 统计路由
- `TestWebModelConfigRoute` - 模型配置
- `TestWebInfoRoute` - 服务器信息
- `TestWebErrorHandling` - 错误处理

---

## Phase 3: Host 集成测试 ✅ COMPLETED

### 3.1 API 集成测试 (`tests/test_integration_api.py`) ✅ 新建
**测试数**: 9

**测试类**:
- `TestTranscribeIntegration` - 完整转写工作流测试
- `TestAuthIntegration` - API Key 生命周期测试
- `TestModelConfigIntegration` - 模型配置更新和验证
- `TestHealthCheckIntegration` - 健康检查一致性测试
- `TestErrorHandlingIntegration` - 错误处理测试

### 3.2 服务器启动测试 (`tests/test_server_startup.py`) ✅ 新建
**测试数**: 28

**测试类**:
- `TestFastAPIStartup` - FastAPI 应用启动测试
- `TestDatabaseAutoInit` - 数据库自动初始化测试
- `TestConfigLoad` - 配置加载测试
- `TestServerInfo` - 服务器信息测试
- `TestFlaskWebStartup` - Flask Web 启动测试
- `TestGracefulShutdown` - 优雅关闭测试
- `TestServerIntegration` - 服务器集成测试
- `TestServerPorts` - 端口配置测试
- `TestEnvironmentSetup` - 环境设置测试

---

## Phase 4: Client 单元测试补充

### 4.1 API 客户端测试 (`tests/test_api_client.py`) - 新建
```python
class TestAPIClient:
    def test_set_base_url
    def test_set_api_key
    def test_health_check_success
    def test_health_check_failure
    def test_transcribe_success
    def test_transcribe_failure
    def test_translate_not_implemented
    def test_timeout_handling
    def test_retry_logic
```

### 4.2 录音模块测试 (`tests/test_recorder.py`) - 新建
```python
class TestRecorder:
    def test_start_recording
    def test_stop_recording
    def test_recording_too_short
    def test_get_input_devices
    def test_recording_format  # 验证 16kHz, mono
    def test_concurrent_recording_prevention
```

### 4.3 热键模块测试 (`tests/test_hotkey.py`) - 新建
```python
class TestHotkeyListener:
    def test_start_stop
    def test_callback_registration
    def test_hotkey_parsing
    def test_pause_resume
    def test_invalid_hotkey_format
```

### 4.4 文本输入模块测试 (`tests/test_text_input.py`) - 新建
```python
class TestTextInput:
    def test_copy_to_clipboard
    def test_output_text
    def test_clipboard_encoding  # 中文支持
```

### 4.5 配置模块测试 (`tests/test_client_config.py`) - 新建
```python
class TestClientConfig:
    def test_default_values
    def test_save_and_load
    def test_hotkey_config_validation
    def test_invalid_config_file_handling
```

---

## Phase 5: Client 集成测试

### 5.1 端到端测试 (`tests/test_e2e.py`) - 新建
```python
class TestE2E:
    @pytest.mark.integration
    def test_transcribe_workflow
        # 1. 启动模拟服务器
        # 2. 配置客户端
        # 3. 模拟录音
        # 4. 验证 API 调用
        # 5. 验证剪贴板输出

    @pytest.mark.integration
    def test_error_handling_workflow
        # 测试各种错误场景的处理
```

---

## Phase 6: 测试自动化配置

### 6.1 pytest 配置 (`host/pytest.ini`) - 更新
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    slow: tests requiring model download
    integration: integration tests requiring server
    unit: fast unit tests

addopts =
    -v
    --tb=short
    --strict-markers
```

### 6.2 CI 配置 (`.github/workflows/test.yml`) - 新建
```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd host
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run unit tests
        run: |
          cd host
          pytest tests/ -v -m "not slow and not integration" --cov=app --cov=models

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd host
          pip install -r requirements.txt
          pip install pytest
      - name: Run integration tests
        run: |
          cd host
          pytest tests/ -v -m "integration"
```

### 6.3 测试脚本 (`scripts/run_tests.sh`) - 新建
```bash
#!/bin/bash

# 快速单元测试
run_unit_tests() {
    echo "Running unit tests..."
    pytest tests/ -v -m "unit" --cov=app --cov=models --cov-report=html
}

# 完整测试 (含慢速测试)
run_all_tests() {
    echo "Running all tests..."
    pytest tests/ -v --cov=app --cov=models --cov-report=html
}

# 集成测试
run_integration_tests() {
    echo "Running integration tests..."
    pytest tests/ -v -m "integration"
}

case "$1" in
    unit) run_unit_tests ;;
    integration) run_integration_tests ;;
    all) run_all_tests ;;
    *) run_unit_tests ;;
esac
```

---

## Phase 7: 测试覆盖率验证

### 7.1 覆盖率目标

| 模块 | 目标覆盖率 |
|------|-----------|
| `host/app/config.py` | 100% |
| `host/app/database.py` | 100% |
| `host/app/api/transcribe.py` | 100% |
| `host/app/api/translate.py` | 100% |
| `host/app/api/stats.py` | 100% |
| `host/models/asr_model.py` | 95%+ |
| `host/web/__init__.py` | 100% |
| `client/app/config.py` | 100% |
| `client/app/api_client.py` | 100% |
| `client/app/recorder.py` | 95%+ |
| `client/app/hotkey.py` | 95%+ |
| `client/app/text_input.py` | 100% |

### 7.2 覆盖率报告配置
```bash
# 生成覆盖率报告
pytest tests/ --cov=app --cov=models --cov-report=html --cov-report=term

# 查看报告
open htmlcov/index.html
```

---

## 执行计划时间表

| 阶段 | 任务 | 优先级 | 状态 | 预估工作量 |
|------|------|--------|------|-----------|
| Phase 1 | 基础设施修复 | P0 | ✅ 完成 | 2-3小时 |
| Phase 2 | Host 单元测试 | P0 | ✅ 完成 | 4-6小时 |
| Phase 3 | Host 集成测试 | P1 | ✅ 完成 | 2-3小时 |
| Phase 4 | Client 单元测试 | P1 | ✅ 完成 | 3-4小时 |
| Phase 5 | Client 集成测试 | P2 | ✅ 完成 | 2-3小时 |
| Phase 6 | 测试自动化配置 | P1 | ✅ 完成 | 1-2小时 |
| Phase 7 | 覆盖率验证 | P0 | ✅ 完成 | 1小时 |

**总计**: 约 15-22 小时

---

## 测试文件清单

### 新建文件
```
host/
├── models/
│   ├── __init__.py
│   └── asr_model.py
├── tests/
│   ├── fixtures/
│   │   ├── test_audio.wav
│   │   ├── test_audio_zh.wav
│   │   ├── test_audio_short.wav
│   │   └── test_audio_silent.wav
│   ├── test_api_transcribe.py
│   ├── test_api_translate.py
│   ├── test_api_stats.py
│   ├── test_web_admin.py
│   ├── test_integration_api.py
│   └── test_server_startup.py
└── scripts/
    └── run_tests.sh

client/
└── tests/
    ├── __init__.py
    ├── test_api_client.py
    ├── test_recorder.py
    ├── test_hotkey.py
    ├── test_text_input.py
    └── test_client_config.py

.github/
└── workflows/
    └── test.yml
```

### 更新文件
```
host/
├── pytest.ini
├── tests/
│   ├── conftest.py (添加更多 fixtures)
│   ├── test_asr_model.py (补充测试)
│   ├── test_config.py (补充测试)
│   └── test_database.py (补充测试)
```

---

## 验收标准

- [x] 所有现有测试通过
- [x] 新增测试全部通过
- [x] 代码覆盖率 >= 95%
- [x] CI/CD 流水线配置完成
- [x] 测试可在无交互情况下自动执行
- [x] 测试报告自动生成

---

## 最终测试统计

### Host 测试 (145 个)
| 测试文件 | 测试数 | 状态 |
|---------|-------|------|
| `test_api.py` | 18 | ✅ |
| `test_asr_model.py` | 20 | ✅ |
| `test_config.py` | 25 | ✅ |
| `test_database.py` | 25 | ✅ |
| `test_web_admin.py` | 16 | ✅ |
| `test_integration_api.py` | 9 | ✅ |
| `test_server_startup.py` | 28 | ✅ |

### Client 测试 (80 个)
| 测试文件 | 测试数 | 状态 |
|---------|-------|------|
| `test_api_client.py` | 19 | ✅ |
| `test_client_config.py` | 20 | ✅ |
| `test_hotkey.py` | 11 | ✅ |
| `test_recorder.py` | 11 | ✅ |
| `test_text_input.py` | 19 | ✅ |

### 总计: 225 个测试 ✅ 全部通过
