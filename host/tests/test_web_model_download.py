"""
Tests for Web Admin Model Download API
Tests for Flask routes in web/__init__.py
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add test utilities
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def web_client(isolated_db):
    """Create Flask test client with isolated database"""
    # Add host directory to path for imports
    host_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(host_dir))

    # Patch the database to use isolated test database
    with patch('app.database.engine', isolated_db['engine']):
        with patch('app.database.SessionLocal', isolated_db['SessionLocal']):
            with patch('web.init_db'):  # Skip init_db in web module
                from web import app as flask_app
                flask_app.config['TESTING'] = True
                yield flask_app.test_client()


class TestModelDownloadStatusAPI:
    """Test model download status API endpoints"""

    def test_get_models_status(self, web_client):
        """Test getting all models status"""
        response = web_client.get("/api/models/status")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == True
        assert "models" in data

        # Check that all expected models are present
        expected_models = ["tiny", "base", "small", "medium", "large-v3"]
        for model_name in expected_models:
            assert model_name in data["models"], f"Model {model_name} not in response"
            model = data["models"][model_name]
            assert "is_downloaded" in model
            assert "name" in model
            assert "size" in model
            assert "download_status" in model
            assert "download_progress" in model

    def test_get_model_status(self, web_client):
        """Test getting single model status"""
        for model_name in ["tiny", "base", "small"]:
            response = web_client.get(f"/api/models/{model_name}/status")
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] == True
            assert "model" in data
            assert "is_downloaded" in data["model"]
            assert "name" in data["model"]
            assert "download_status" in data["model"]
            assert "download_progress" in data["model"]

    def test_get_model_status_invalid_model(self, web_client):
        """Test getting status for invalid model"""
        response = web_client.get("/api/models/invalid_model/status")
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] == False
        assert "error" in data

    def test_start_download_invalid_model(self, web_client):
        """Test starting download with invalid model"""
        response = web_client.post("/api/models/invalid_model/download")
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] == False
        assert "error" in data
