"""
SpeechMate Web Admin Interface
"""
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request, redirect, url_for

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import config, ASR_MODELS, get_base_url, get_local_ip, save_config, MODELS_DIR
from app.database import (
    get_all_api_keys, create_api_key, delete_api_key, toggle_api_key,
    get_stats, init_db
)
from models.model_downloader import get_downloader, DownloadStatus
from models.asr_model import check_available_models

app = Flask(__name__)
app.secret_key = config.jwt_secret


@app.route("/")
def index():
    """Main page"""
    return render_template(
        "index.html",
        base_url=get_base_url(),
        admin_key=config.admin_api_key,
        current_model=config.model.asr_model,
        current_device=config.model.asr_device,
        available_models=ASR_MODELS,
        api_keys=get_all_api_keys(),
        model_cache_path=str(MODELS_DIR)
    )


@app.route("/api/stats")
def api_stats():
    """Get usage statistics"""
    days = request.args.get("days", 30, type=int)
    stats = get_stats(days=days)
    return jsonify({"success": True, "stats": stats})


@app.route("/api/keys", methods=["GET"])
def list_keys():
    """List all API keys"""
    keys = get_all_api_keys()
    return jsonify({"success": True, "keys": keys})


@app.route("/api/keys", methods=["POST"])
def create_key():
    """Create new API key"""
    data = request.get_json()
    name = data.get("name", "New Key")
    key = create_api_key(name)
    return jsonify({"success": True, "key": key, "name": name})


@app.route("/api/keys/<int:key_id>", methods=["DELETE"])
def delete_key(key_id):
    """Delete API key"""
    success = delete_api_key(key_id)
    return jsonify({"success": success})


@app.route("/api/keys/<int:key_id>/toggle", methods=["POST"])
def toggle_key(key_id):
    """Toggle API key status"""
    is_active = toggle_api_key(key_id)
    return jsonify({"success": True, "is_active": is_active})


@app.route("/api/config/model", methods=["POST"])
def update_model():
    """Update model configuration"""
    data = request.get_json()

    asr_model = data.get("asr_model")
    asr_device = data.get("asr_device")
    asr_compute_type = data.get("asr_compute_type")

    if asr_model and asr_model in ASR_MODELS:
        config.model.asr_model = asr_model

    if asr_device in ["cpu", "cuda"]:
        config.model.asr_device = asr_device

    if asr_compute_type in ["float16", "int8", "int8_float16"]:
        config.model.asr_compute_type = asr_compute_type

    save_config()

    return jsonify({
        "success": True,
        "config": {
            "asr_model": config.model.asr_model,
            "asr_device": config.model.asr_device,
            "asr_compute_type": config.model.asr_compute_type
        }
    })


@app.route("/api/info")
def server_info():
    """Get server information"""
    return jsonify({
        "success": True,
        "base_url": get_base_url(),
        "local_ip": get_local_ip(),
        "api_port": config.server.api_port,
        "current_model": {
            "asr": config.model.asr_model,
            "device": config.model.asr_device,
            "compute_type": config.model.asr_compute_type
        },
        "available_models": ASR_MODELS,
        "model_cache_path": str(MODELS_DIR)
    })


# ============================================================================
# Model Download Management API
# ============================================================================

@app.route("/api/models/status")
def models_status():
    """Get download status for all ASR models"""
    try:
        # Get downloaded models from asr_model module
        downloaded = check_available_models()

        # Get download progress from downloader
        downloader = get_downloader()
        download_status = downloader.get_all_download_status()

        # Merge information
        result = {}
        for model_name in ASR_MODELS.keys():
            is_downloaded = downloaded.get(model_name, False)
            status = download_status.get(model_name, {})

            result[model_name] = {
                "name": ASR_MODELS[model_name]["name"],
                "size": ASR_MODELS[model_name]["size"],
                "description": ASR_MODELS[model_name]["description"],
                "speed": ASR_MODELS[model_name]["speed"],
                "accuracy": ASR_MODELS[model_name]["accuracy"],
                "is_downloaded": is_downloaded,
                "download_status": status.get("status", "idle"),
                "download_progress": status.get("progress", 0),
                "error_message": status.get("error_message", ""),
                "elapsed_time": status.get("elapsed_time", 0)
            }

        return jsonify({"success": True, "models": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/models/<model_name>/status")
def model_status(model_name):
    """Get download status for a specific model"""
    if model_name not in ASR_MODELS:
        return jsonify({"success": False, "error": "Invalid model name"}), 400

    try:
        # Get downloaded status
        downloaded = check_available_models()
        is_downloaded = downloaded.get(model_name, False)

        # Get download progress
        downloader = get_downloader()
        progress = downloader.get_model_status(model_name)

        return jsonify({
            "success": True,
            "model": {
                "name": ASR_MODELS[model_name]["name"],
                "size": ASR_MODELS[model_name]["size"],
                "is_downloaded": is_downloaded,
                "download_status": progress.status.value,
                "download_progress": progress.progress,
                "error_message": progress.error_message,
                "elapsed_time": progress._get_elapsed_time()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/models/<model_name>/download", methods=["POST"])
def start_model_download(model_name):
    """Start downloading a model"""
    if model_name not in ASR_MODELS:
        return jsonify({"success": False, "error": "Invalid model name"}), 400

    try:
        downloader = get_downloader()

        # Check if already downloaded
        if downloader.is_model_downloaded(model_name):
            return jsonify({
                "success": False,
                "error": "Model already downloaded"
            })

        # Start download
        started = downloader.start_download(
            model_name,
            device=config.model.asr_device,
            compute_type=config.model.asr_compute_type
        )

        if started:
            return jsonify({
                "success": True,
                "message": f"Started downloading {model_name}"
            })
        else:
            # Check if already downloading
            progress = downloader.get_model_status(model_name)
            if progress.status == DownloadStatus.DOWNLOADING:
                return jsonify({
                    "success": False,
                    "error": "Model is already downloading"
                })
            return jsonify({
                "success": False,
                "error": "Failed to start download"
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/models/<model_name>/cancel", methods=["POST"])
def cancel_model_download(model_name):
    """Cancel an ongoing model download"""
    if model_name not in ASR_MODELS:
        return jsonify({"success": False, "error": "Invalid model name"}), 400

    try:
        downloader = get_downloader()
        cancelled = downloader.cancel_download(model_name)

        if cancelled:
            return jsonify({
                "success": True,
                "message": f"Cancelled download for {model_name}"
            })
        else:
            return jsonify({
                "success": False,
                "error": "No active download to cancel"
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/models/<model_name>", methods=["DELETE"])
def delete_model(model_name):
    """Delete a downloaded model"""
    if model_name not in ASR_MODELS:
        return jsonify({"success": False, "error": "Invalid model name"}), 400

    try:
        downloader = get_downloader()
        deleted = downloader.delete_model(model_name)

        if deleted:
            return jsonify({
                "success": True,
                "message": f"Deleted model {model_name}"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Model not found or could not be deleted"
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def run_web_server():
    """Run the web admin server"""
    init_db()
    app.run(
        host=config.server.web_host,
        port=config.server.web_port,
        debug=config.server.debug
    )


if __name__ == "__main__":
    run_web_server()
