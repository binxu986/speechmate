"""
SpeechMate Client Build Script
Builds the Windows executable using PyInstaller
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.absolute()
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
SPEC_FILE = BASE_DIR / "SpeechMate.spec"


def clean():
    """Clean build artifacts"""
    print("Cleaning build artifacts...")

    dirs_to_clean = [DIST_DIR, BUILD_DIR]
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"Removed: {dir_path}")

    if SPEC_FILE.exists():
        SPEC_FILE.unlink()
        print(f"Removed: {SPEC_FILE}")


def build():
    """Build the executable"""
    print("Building SpeechMate Client...")

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=SpeechMate",
        "--onefile",
        "--windowed",  # No console window
        "--clean",
        f"--distpath={DIST_DIR}",
        f"--workpath={BUILD_DIR}",
        f"--specpath={BASE_DIR}",
        # Add hidden imports
        "--hidden-import=PyQt5",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=pynput",
        "--hidden-import=pynput.keyboard",
        "--hidden-import=sounddevice",
        "--hidden-import=soundfile",
        "--hidden-import=numpy",
        "--hidden-import=requests",
        "--hidden-import=pyperclip",
        "--hidden-import=loguru",
        # Add data files if any
        # f"--add-data=resources;resources",
        # Entry point
        "app/main.py"
    ]

    # Run PyInstaller
    result = subprocess.run(cmd, cwd=BASE_DIR)

    if result.returncode == 0:
        print(f"\nBuild successful!")
        print(f"Executable: {DIST_DIR / 'SpeechMate.exe'}")
    else:
        print(f"\nBuild failed with error code: {result.returncode}")
        sys.exit(1)


def create_portable_package():
    """Create a portable package with all dependencies"""
    print("Creating portable package...")

    portable_dir = DIST_DIR / "SpeechMate_Portable"
    if portable_dir.exists():
        shutil.rmtree(portable_dir)

    portable_dir.mkdir(parents=True)

    # Copy executable
    exe_src = DIST_DIR / "SpeechMate.exe"
    if exe_src.exists():
        shutil.copy(exe_src, portable_dir / "SpeechMate.exe")

    # Create README
    readme_content = """# SpeechMate - 语音识别与翻译助手

## 使用方法

1. 确保 Host 服务器已启动
2. 双击运行 SpeechMate.exe
3. 在设置中配置服务器 URL 和 API Key
4. 使用快捷键进行语音输入:
   - Alt (按住): 语音识别
   - Shift (按住): 中译英
   - Shift+A (按住): 英译中

## 注意事项

- 首次运行可能需要允许防火墙访问
- 确保麦克风已正确配置
- 如果快捷键不工作，请尝试以管理员身份运行

## 系统要求

- Windows 10 或更高版本
- 麦克风设备
- 网络连接（连接到 Host 服务器）
"""

    with open(portable_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print(f"Portable package created: {portable_dir}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Build SpeechMate Client")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    parser.add_argument("--build", action="store_true", help="Build executable")
    parser.add_argument("--package", action="store_true", help="Create portable package")
    parser.add_argument("--all", action="store_true", help="Clean, build, and package")

    args = parser.parse_args()

    if args.all:
        clean()
        build()
        create_portable_package()
    elif args.clean:
        clean()
    elif args.build:
        build()
    elif args.package:
        create_portable_package()
    else:
        # Default: build
        build()


if __name__ == "__main__":
    main()
