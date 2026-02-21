# SpeechMate 部署指南

## 系统要求

### Host 服务器
- **操作系统**: Windows 10/11 或 Linux (Ubuntu 20.04+)
- **Python**: 3.9 - 3.11
- **内存**: 最少 4GB，推荐 8GB+（取决于使用的模型）
- **存储**: 至少 5GB 可用空间（用于模型）
- **GPU**: 可选，支持 CUDA 的 NVIDIA GPU 可显著提升性能

### Client 客户端
- **操作系统**: Windows 10/11
- **内存**: 最少 2GB
- **麦克风**: 任意兼容的音频输入设备

---

## Host 服务器部署

### 方法一：一键部署（推荐）

1. **克隆或下载项目**
```bash
git clone https://github.com/binxu986/speechmate.git
cd speechmate/host
```

2. **运行启动脚本**
```bash
# Windows
python start_server.py

# Linux
python3 start_server.py
```

3. **等待部署完成**
- 脚本会自动创建虚拟环境
- 安装所有依赖
- 下载默认的语音识别模型（首次运行）
- 启动 API 服务和 Web 管理界面

4. **访问服务**
- API 服务: `http://<服务器IP>:8000`
- API 文档: `http://<服务器IP>:8000/docs`
- Web 管理: `http://<服务器IP>:5000`

### 方法二：手动部署

1. **创建虚拟环境**
```bash
cd speechmate/host
python -m venv venv

# Windows
venv\Scripts\activate

# Linux
source venv/bin/activate
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动服务**
```bash
# 启动 API 服务
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 在另一个终端启动 Web 管理界面
python -m web.app
```

### 停止服务

```bash
# 使用停止脚本
python stop_server.py

# 或者按 Ctrl+C 停止 start_server.py
```

---

## Client 客户端部署

### 方法一：使用打包好的 EXE（推荐）

1. 从 Release 页面下载 `SpeechMate.exe`
2. 双击运行，无需安装

### 方法二：从源码运行

1. **安装依赖**
```bash
cd speechmate/client
pip install -r requirements.txt
```

2. **运行程序**
```bash
python app/main.py
```

### 方法三：自行打包 EXE

```bash
cd speechmate/client
pip install pyinstaller
python build.py --all
```

打包完成后，可执行文件位于 `dist/SpeechMate.exe`

---

## 配置说明

### Host 服务器配置

配置保存在 `host/data/config.yaml`：

```yaml
server:
  api_host: "0.0.0.0"
  api_port: 8000
  web_host: "0.0.0.0"
  web_port: 5000

model:
  asr_model: "small"  # tiny, base, small, medium, large-v3
  asr_device: "cpu"   # cpu 或 cuda
  asr_compute_type: "int8"  # float16, int8, int8_float16
```

### Client 客户端配置

在应用设置界面中配置：

- **Base URL**: Host 服务器的 API 地址
- **API Key**: 从 Web 管理界面获取
- **快捷键**: 自定义各功能的快捷键

---

## 防火墙配置

### Windows

1. 打开 Windows Defender 防火墙
2. 点击"允许应用通过防火墙"
3. 添加 Python 或 SpeechMate.exe
4. 确保允许专用和公用网络

### Linux (Ubuntu)

```bash
# 开放端口
sudo ufw allow 8000
sudo ufw allow 5000
```

---

## 常见问题

### 1. 模型下载失败

**问题**: 首次运行时模型下载失败

**解决**:
- 检查网络连接
- 使用代理或镜像源
- 手动下载模型到 `host/model_cache` 目录

### 2. CUDA 相关错误

**问题**: GPU 加速不工作

**解决**:
- 确保安装了正确版本的 CUDA 和 cuDNN
- 检查 PyTorch 是否支持 CUDA:
  ```python
  import torch
  print(torch.cuda.is_available())
  ```

### 3. 端口被占用

**问题**: 启动时提示端口被占用

**解决**:
- 使用 `stop_server.py` 停止现有服务
- 或修改配置文件中的端口号

### 4. Client 无法连接

**问题**: 客户端显示连接失败

**解决**:
- 检查 Host 服务器是否正在运行
- 确认防火墙已放行相关端口
- 检查 Base URL 是否正确（使用实际 IP 而非 localhost）
