"""
Tests for Web Admin Interface (Flask)

Tests for Flask routes in web/__init__.py
"""
import pytest
import sys
from pathlib import Path


@pytest.fixture
def web_client():
    """Create Flask test client"""
    # Add host directory to path
    host_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(host_dir))

    from web import app as flask_app
    flask_app.config['TESTING'] = True
    return flask_app.test_client()


@pytest.fixture
def admin_api_key():
    """Get admin API key"""
    from app.config import config
    return config.admin_api_key


class TestWebIndexRoute:
    """Test index page route"""

    def test_index_page(self, web_client):
        """Test index page loads"""
        response = web_client.get("/")
        assert response.status_code == 200

    def test_index_contains_title(self, web_client):
        """Test index page contains title"""
        response = web_client.get("/")
        data = response.data.decode('utf-8')
        assert "SpeechMate" in data or "speechmate" in data.lower()


class TestWebAPIKeysRoutes:
    """Test API keys management routes"""

    def test_list_keys(self, web_client):
        """Test listing API keys"""
        response = web_client.get("/api/keys")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == True
        assert "keys" in data

    def test_create_key(self, web_client):
        """Test creating API key"""
        response = web_client.post(
            "/api/keys",
            json={"name": "Test Key from Web Test"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == True
        assert "key" in data
        assert len(data["key"]) == 32

    def test_create_key_no_name(self, web_client):
        """Test creating API key without name"""
        response = web_client.post(
            "/api/keys",
            json={}
        )
        # Should still work with default name
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == True

    def test_delete_key(self, web_client):
        """Test deleting API key"""
        # First create a key
        create_response = web_client.post(
            "/api/keys",
            json={"name": "Key to Delete"}
        )
        keys = web_client.get("/api/keys").get_json()["keys"]

        if keys:
            key_id = keys[-1]["id"]  # Get last created key
            response = web_client.delete(f"/api/keys/{key_id}")
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] == True

    def test_delete_nonexistent_key(self, web_client):
        """Test deleting non-existent key"""
        response = web_client.delete("/api/keys/99999")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == False

    def test_toggle_key(self, web_client):
        """Test toggling API key"""
        # Get first key
        keys_response = web_client.get("/api/keys")
        keys = keys_response.get_json()["keys"]

        if keys:
            key_id = keys[0]["id"]
            response = web_client.post(f"/api/keys/{key_id}/toggle")
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] == True
            assert "is_active" in data


class TestWebStatsRoute:
    """Test statistics route"""

    def test_stats_default(self, web_client):
        """Test getting stats with default days"""
        response = web_client.get("/api/stats")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == True
        assert "stats" in data

    def test_stats_with_days(self, web_client):
        """Test getting stats with days parameter"""
        response = web_client.get("/api/stats?days=7")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == True


class TestWebModelConfigRoute:
    """Test model configuration route"""

    def test_update_model_config(self, web_client):
        """Test updating model configuration"""
        response = web_client.post(
            "/api/config/model",
            json={
                "asr_model": "tiny",
                "asr_device": "cpu",
                "asr_compute_type": "int8"
            }
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == True
        assert "config" in data

    def test_update_model_config_invalid_model(self, web_client):
        """Test updating with invalid model name"""
        response = web_client.post(
            "/api/config/model",
            json={
                "asr_model": "invalid_model",
                "asr_device": "cpu"
            }
        )
        # Should still return success but ignore invalid model
        assert response.status_code == 200

    def test_update_model_config_invalid_device(self, web_client):
        """Test updating with invalid device"""
        response = web_client.post(
            "/api/config/model",
            json={
                "asr_model": "small",
                "asr_device": "invalid_device"
            }
        )
        # Should still return success but ignore invalid device
        assert response.status_code == 200


class TestWebInfoRoute:
    """Test server info route"""

    def test_server_info(self, web_client):
        """Test getting server info"""
        response = web_client.get("/api/info")
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == True
        assert "local_ip" in data
        assert "api_port" in data
        assert "current_model" in data
        assert "available_models" in data


class TestWebErrorHandling:
    """Test error handling"""

    def test_404_route(self, web_client):
        """Test 404 error handling"""
        response = web_client.get("/nonexistent/route")
        assert response.status_code == 404

    def test_invalid_json(self, web_client):
        """Test invalid JSON handling"""
        response = web_client.post(
            "/api/keys",
            data="not json",
            content_type="application/json"
        )
        # Should handle gracefully
        assert response.status_code in [200, 400, 415]
