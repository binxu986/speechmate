@echo off
chcp 65001 >nul
echo ====================================
echo   SpeechMate Host 一键部署
echo ====================================
echo.

cd /d "%~dp0"

echo [1/5] 创建Python虚拟环境...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/5] 安装Python依赖...
pip install -r requirements.txt

echo [3/5] 检查 ffmpeg...
where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ffmpeg 未安装，正在尝试安装...
    choco install ffmpeg -y
)

echo [4/5] 下载默认模型 (Faster Whisper base)...
python -c "from faster_whisper import WhisperModel; WhisperModel('base', device='cpu', compute_type='int8')"

echo.
echo ====================================
echo   部署完成！
echo ====================================
echo 访问 http://localhost:3456 查看管理界面
echo 按 Ctrl+C 停止服务
echo.

echo [5/5] 启动服务...
python -m src.api_server

pause
