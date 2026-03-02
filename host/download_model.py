#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SpeechMate Model Download Utility

This script handles ASR model downloading with:
- HuggingFace mirror support (auto-detect for China users)
- Progress bar display
- Model verification
"""
import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# Configure HuggingFace mirror before importing huggingface_hub
def setup_hf_mirror():
    """Setup HuggingFace mirror for better connectivity"""
    # Priority: Environment variable > Auto-detect > Default mirror
    if "HF_ENDPOINT" not in os.environ:
        # Default to China mirror (works globally, just slower for non-China users)
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        print(f"[INFO] Using HuggingFace mirror: {os.environ['HF_ENDPOINT']}")
        print("[INFO] Set HF_ENDPOINT environment variable to use a different mirror")
    else:
        print(f"[INFO] Using HuggingFace endpoint: {os.environ['HF_ENDPOINT']}")


# Available models
AVAILABLE_MODELS = {
    "tiny": {
        "name": "faster-whisper-tiny",
        "size": "39MB",
        "description": "最快的模型，适合快速响应场景"
    },
    "base": {
        "name": "faster-whisper-base",
        "size": "74MB",
        "description": "速度和精度的平衡选择"
    },
    "small": {
        "name": "faster-whisper-small",
        "size": "244MB",
        "description": "推荐的默认选择"
    },
    "medium": {
        "name": "faster-whisper-medium",
        "size": "769MB",
        "description": "高精度识别"
    },
    "large-v3": {
        "name": "faster-whisper-large-v3",
        "size": "1.5GB",
        "description": "最高精度的模型"
    }
}


def format_size(size_str: str) -> int:
    """Convert size string to bytes"""
    size_str = size_str.upper()
    if "GB" in size_str:
        return int(float(size_str.replace("GB", "")) * 1024 * 1024 * 1024)
    elif "MB" in size_str:
        return int(float(size_str.replace("MB", "")) * 1024 * 1024)
    return 0


def download_with_progress(model_name: str, download_root: str, device: str = "cpu", compute_type: str = "int8"):
    """
    Download model with progress display.

    Args:
        model_name: Name of the model (tiny, base, small, medium, large-v3)
        download_root: Directory to download model to
        device: Device to use (cpu or cuda)
        compute_type: Computation type
    """
    from faster_whisper import WhisperModel

    model_info = AVAILABLE_MODELS.get(model_name, {})
    model_size = model_info.get("size", "Unknown")
    model_desc = model_info.get("description", "")

    print(f"\n{'='*60}")
    print(f"  Downloading: faster-whisper-{model_name}")
    print(f"  Size: {model_size}")
    print(f"  Description: {model_desc}")
    print(f"{'='*60}\n")

    # Create download directory
    Path(download_root).mkdir(parents=True, exist_ok=True)

    # Download and load model (this will show huggingface_hub progress)
    print("Starting download... (this may take a few minutes)")
    print("Progress:")

    try:
        model = WhisperModel(
            model_name,
            device=device,
            compute_type=compute_type,
            download_root=download_root
        )

        print(f"\n{'='*60}")
        print("  ✓ Model downloaded and verified successfully!")
        print(f"  Location: {download_root}")
        print(f"{'='*60}\n")

        # Clean up
        del model
        return True

    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        return False


def list_models():
    """List all available models"""
    print("\nAvailable ASR Models:")
    print("-" * 60)
    for name, info in AVAILABLE_MODELS.items():
        print(f"  {name:12} | {info['size']:8} | {info['description']}")
    print("-" * 60)


def check_model_exists(model_name: str, download_root: str) -> bool:
    """Check if model is already downloaded"""
    model_path = Path(download_root) / f"models--Systran--faster-whisper-{model_name}"
    return model_path.exists()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Download ASR models for SpeechMate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_model.py                    # Download default model (small)
  python download_model.py --model tiny       # Download tiny model
  python download_model.py --model all        # Download all models
  python download_model.py --list             # List available models
  python download_model.py --check            # Check downloaded models
        """
    )

    parser.add_argument(
        "--model", "-m",
        default="small",
        help="Model to download (tiny, base, small, medium, large-v3, all)"
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Download directory (default: ./model_cache)"
    )
    parser.add_argument(
        "--device", "-d",
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device to optimize for"
    )
    parser.add_argument(
        "--compute-type", "-c",
        default="int8",
        choices=["int8", "float16", "int8_float16"],
        help="Computation type"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available models"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check which models are already downloaded"
    )
    parser.add_argument(
        "--no-mirror",
        action="store_true",
        help="Don't use mirror, download from official HuggingFace"
    )

    args = parser.parse_args()

    # Setup mirror
    if args.no_mirror:
        os.environ["HF_ENDPOINT"] = "https://huggingface.co"
    else:
        setup_hf_mirror()

    # Set download directory
    base_dir = Path(__file__).parent
    download_root = args.output or str(base_dir / "model_cache")

    # List models
    if args.list:
        list_models()
        return 0

    # Check downloaded models
    if args.check:
        print("\nDownloaded Models Status:")
        print("-" * 60)
        for name in AVAILABLE_MODELS:
            exists = check_model_exists(name, download_root)
            status = "✓ Downloaded" if exists else "✗ Not downloaded"
            size = AVAILABLE_MODELS[name]["size"]
            print(f"  {name:12} | {size:8} | {status}")
        print("-" * 60)
        return 0

    # Download model(s)
    models_to_download = []

    if args.model == "all":
        models_to_download = list(AVAILABLE_MODELS.keys())
    elif args.model in AVAILABLE_MODELS:
        models_to_download = [args.model]
    else:
        print(f"Error: Unknown model '{args.model}'")
        print("Use --list to see available models")
        return 1

    # Download each model
    success_count = 0
    for model_name in models_to_download:
        # Check if already downloaded
        if check_model_exists(model_name, download_root):
            print(f"\n[SKIP] Model '{model_name}' already downloaded")
            print(f"       Location: {download_root}")
            success_count += 1
            continue

        if download_with_progress(model_name, download_root, args.device, args.compute_type):
            success_count += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"  Download complete: {success_count}/{len(models_to_download)} models")
    print(f"{'='*60}\n")

    return 0 if success_count == len(models_to_download) else 1


if __name__ == "__main__":
    sys.exit(main())
