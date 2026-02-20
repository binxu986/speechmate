#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "=== SpeechMate Host 一键部署 ==="

echo "[1/5] 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

echo "[2/5] 安装Python依赖..."
pip install -r requirements.txt

echo "[3/5] 安装系统依赖 (ffmpeg)..."
# Ubuntu
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y ffmpeg
# macOS
elif command -v brew &> /dev/null; then
    brew install ffmpeg
# Windows (assume choco)
elif command -v choco &> /dev/null; then
    choco install ffmpeg -y
fi

echo "[4/5] 下载默认模型 (Faster Whisper base)..."
python3 -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"

echo "[5/5] 启动服务..."
echo "服务启动成功！"
echo "访问 http://localhost:3456 查看管理界面"
echo "按 Ctrl+C 停止服务"
python3 -m src.api_server
