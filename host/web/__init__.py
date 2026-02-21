"""
SpeechMate Web Admin Interface
"""
import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request, redirect, url_for

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import config, ASR_MODELS, get_base_url, get_local_ip, save_config
from app.database import (
    get_all_api_keys, create_api_key, delete_api_key, toggle_api_key,
    get_stats, init_db
)

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
        api_keys=get_all_api_keys()
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
        "available_models": ASR_MODELS
    })


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
