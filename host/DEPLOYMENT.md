# SpeechMate 环境管理指南

## 环境类型

| 环境 | 用途 | Python | 依赖文件 |
|------|------|--------|----------|
| 开发环境 | 本地开发、测试 | Anaconda/venv | `requirements-dev.txt` |
| 生产环境 | 服务器部署 | venv/Docker | `requirements.txt` |

---

## 开发环境设置

### 方式 1: 使用 Anaconda (推荐)

```bash
# 创建独立环境
conda create -n speechmate python=3.10 -y
conda activate speechmate

# 安装开发依赖
cd host
pip install -r requirements-dev.txt

# 下载模型
python download_model.py --model small

# 运行测试
pytest tests/ -v

# 启动服务 (开发模式)
python -m uvicorn app.main:app --reload --port 8000
python -m web.app  # 另一个终端
```

### 方式 2: 使用 venv

```bash
# 创建虚拟环境
cd host
python -m venv .venv

# 激活 (Windows)
.venv\Scripts\activate

# 激活 (Linux/macOS)
source .venv/bin/activate

# 安装依赖
pip install -r requirements-dev.txt
```

---

## 生产环境部署

### 方式 1: 一键启动脚本

```bash
# 首次部署 (自动创建 venv、安装依赖、下载模型)
python start_server.py

# 后续启动 (跳过模型下载)
python start_server.py --skip-models

# 停止服务
python stop_server.py
```

### 方式 2: Docker 部署 (推荐)

```bash
# 构建镜像
docker build -t speechmate-host .

# 运行容器
docker run -d \
  --name speechmate \
  -p 8000:8000 \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/model_cache:/app/model_cache \
  speechmate-host

# 或使用 docker-compose
docker-compose up -d
```

### 方式 3: Systemd 服务 (Linux)

```bash
# 创建服务文件
sudo cat > /etc/systemd/system/speechmate.service << EOF
[Unit]
Description=SpeechMate Host Server
After=network.target

[Service]
Type=simple
User=speechmate
WorkingDirectory=/opt/speechmate/host
ExecStart=/opt/speechmate/host/venv/bin/python start_server.py --skip-models
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable speechmate
sudo systemctl start speechmate
```

---

## 依赖管理

### 更新依赖

```bash
# 更新生产依赖
pip install --upgrade -r requirements.txt

# 更新开发依赖
pip install --upgrade -r requirements-dev.txt

# 冻结当前环境 (用于部署)
pip freeze > requirements-freeze.txt
```

### 添加新依赖

1. 生产依赖 → 添加到 `requirements.txt`
2. 开发依赖 → 添加到 `requirements-dev.txt`
3. 固定版本号确保一致性

---

## 环境变量配置

```bash
# 复制模板
cp .env.example .env

# 编辑配置
nano .env
```

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `ASR_MODEL` | `small` | ASR 模型大小 |
| `ASR_DEVICE` | `cpu` | 推理设备 (cpu/cuda) |
| `HF_ENDPOINT` | `https://hf-mirror.com` | HuggingFace 镜像 |
| `DEBUG` | `false` | 调试模式 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

---

## 目录结构

```
host/
├── .env                 # 环境变量配置 (不提交)
├── .env.example         # 环境变量模板
├── requirements.txt     # 生产依赖
├── requirements-dev.txt # 开发依赖
├── Dockerfile           # Docker 镜像
├── docker-compose.yml   # Docker Compose
├── start_server.py      # 一键启动脚本
├── stop_server.py       # 停止脚本
├── download_model.py    # 模型下载工具
├── data/                # 数据目录
│   ├── config.yaml      # 配置文件
│   └── speechmate.db    # SQLite 数据库
├── model_cache/         # 模型缓存
├── logs/                # 日志文件
└── venv/                # 虚拟环境 (自动创建)
```

---

## 常见问题

### Q: 模型下载太慢？
```bash
# 使用国内镜像 (自动配置)
# 或手动设置
export HF_ENDPOINT=https://hf-mirror.com
python download_model.py --model small
```

### Q: NumPy 版本冲突？
```bash
# 降级 NumPy
pip install "numpy<2"
```

### Q: Windows 上 ffmpeg 缺失？
```bash
# 安装 imageio-ffmpeg
pip install imageio-ffmpeg
```
