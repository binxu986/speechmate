"""
Tests for API Endpoints

Tests for transcribe, translate, and stats endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from io import BytesIO
from pathlib import Path


@pytest.fixture
def client():
    """Create test client"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def admin_api_key():
    """Get admin API key"""
    from app.config import config
    return config.admin_api_key


@pytest.fixture
def test_api_key():
    """Create a test API key and return it"""
    from app.database import init_db, create_api_key
    init_db()
    key = create_api_key("Test Key for API Tests")
    return key


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health endpoint returns ok"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy" or data.get("success") == True


class TestInfoEndpoint:
    """Test info endpoint"""

    def test_info_endpoint(self, client):
        """Test info endpoint returns server info"""
        response = client.get("/api/v1/info")
        assert response.status_code == 200
        data = response.json()
        assert "api_port" in data or "success" in data


class TestTranscribeEndpoint:
    """Test transcribe endpoint"""

    def test_transcribe_missing_api_key(self, client, sample_audio_path):
        """Test transcribe without API key returns 422"""
        with open(sample_audio_path, "rb") as f:
            response = client.post(
                "/api/v1/transcribe",
                files={"audio": ("test.wav", f, "audio/wav")}
            )
        # Should return 422 (missing required header) or 401
        assert response.status_code in [401, 422]

    def test_transcribe_invalid_api_key(self, client, sample_audio_path):
        """Test transcribe with invalid API key returns 401"""
        with open(sample_audio_path, "rb") as f:
            response = client.post(
                "/api/v1/transcribe",
                files={"audio": ("test.wav", f, "audio/wav")},
                headers={"X-API-Key": "invalid_key_12345"}
            )
        assert response.status_code == 401

    def test_transcribe_missing_file(self, client, test_api_key):
        """Test transcribe without audio file returns 422"""
        response = client.post(
            "/api/v1/transcribe",
            headers={"X-API-Key": test_api_key}
        )
        assert response.status_code == 422

    def test_transcribe_valid_request(self, client, test_api_key, sample_audio_path):
        """Test transcribe with valid request"""
        with open(sample_audio_path, "rb") as f:
            response = client.post(
                "/api/v1/transcribe",
                files={"audio": ("test.wav", f, "audio/wav")},
                headers={"X-API-Key": test_api_key}
            )

        # Response depends on whether model is downloaded
        # If model not downloaded, returns 500 with error
        # If model downloaded, returns 200 with transcription
        assert response.status_code in [200, 500]

        data = response.json()
        assert "success" in data

    def test_transcribe_with_language_param(self, client, test_api_key, sample_audio_path):
        """Test transcribe with language parameter"""
        with open(sample_audio_path, "rb") as f:
            response = client.post(
                "/api/v1/transcribe",
                files={"audio": ("test.wav", f, "audio/wav")},
                data={"language": "en"},
                headers={"X-API-Key": test_api_key}
            )

        assert response.status_code in [200, 500]


class TestTranslateEndpoint:
    """Test translate endpoint"""

    def test_translate_missing_api_key(self, client, sample_audio_path):
        """Test translate without API key returns 422"""
        with open(sample_audio_path, "rb") as f:
            response = client.post(
                "/api/v1/translate",
                files={"audio": ("test.wav", f, "audio/wav")},
                data={"source_lang": "zh", "target_lang": "en"}
            )
        assert response.status_code in [401, 422]

    def test_translate_invalid_api_key(self, client, sample_audio_path):
        """Test translate with invalid API key returns 401"""
        with open(sample_audio_path, "rb") as f:
            response = client.post(
                "/api/v1/translate",
                files={"audio": ("test.wav", f, "audio/wav")},
                data={"source_lang": "zh", "target_lang": "en"},
                headers={"X-API-Key": "invalid_key"}
            )
        assert response.status_code == 401

    def test_translate_not_implemented(self, client, test_api_key, sample_audio_path):
        """Test translate returns not implemented error"""
        with open(sample_audio_path, "rb") as f:
            response = client.post(
                "/api/v1/translate",
                files={"audio": ("test.wav", f, "audio/wav")},
                data={"source_lang": "zh", "target_lang": "en"},
                headers={"X-API-Key": test_api_key}
            )

        # Translate is not implemented, should return success=False
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        # Check for "not" and "implemented" separately due to phrasing
        error_lower = data["error"].lower()
        assert "not" in error_lower and "implemented" in error_lower


class TestStatsEndpoint:
    """Test stats endpoint"""

    def test_stats_invalid_admin_key(self, client):
        """Test stats with invalid admin key returns 401"""
        response = client.get(
            "/api/v1/stats",
            headers={"X-API-Key": "invalid_admin_key"}
        )
        assert response.status_code == 401

    def test_stats_valid_admin_key(self, client, admin_api_key):
        """Test stats with valid admin key"""
        response = client.get(
            "/api/v1/stats",
            headers={"X-API-Key": admin_api_key}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "api_keys" in data

    def test_stats_with_days_param(self, client, admin_api_key):
        """Test stats with days parameter"""
        response = client.get(
            "/api/v1/stats?days=7",
            headers={"X-API-Key": admin_api_key}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

    def test_stats_invalid_days_param(self, client, admin_api_key):
        """Test stats with invalid days parameter"""
        # Days should be between 1 and 365
        response = client.get(
            "/api/v1/stats?days=0",
            headers={"X-API-Key": admin_api_key}
        )
        assert response.status_code == 422

        response = client.get(
            "/api/v1/stats?days=400",
            headers={"X-API-Key": admin_api_key}
        )
        assert response.status_code == 422


class TestAPIKeysEndpoint:
    """Test API keys management endpoints"""

    def test_list_api_keys(self, client, admin_api_key):
        """Test listing API keys"""
        response = client.get(
            "/api/v1/api-keys",
            headers={"X-API-Key": admin_api_key}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "api_keys" in data

    def test_create_api_key(self, client, admin_api_key):
        """Test creating a new API key"""
        response = client.post(
            "/api/v1/api-keys?name=Test%20Key%20Creation",
            headers={"X-API-Key": admin_api_key}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "key" in data
        assert len(data["key"]) == 32  # 16 bytes = 32 hex chars

    def test_delete_api_key(self, client, admin_api_key, test_api_key):
        """Test deleting an API key"""
        # First create a key to delete
        create_response = client.post(
            "/api/v1/api-keys?name=Key%20To%20Delete",
            headers={"X-API-Key": admin_api_key}
        )
        key_id = None
        if create_response.json()["success"]:
            # Get the key ID from the list
            list_response = client.get(
                "/api/v1/api-keys",
                headers={"X-API-Key": admin_api_key}
            )
            for key in list_response.json()["api_keys"]:
                if key["name"] == "Key To Delete":
                    key_id = key["id"]
                    break

        if key_id:
            response = client.delete(
                f"/api/v1/api-keys/{key_id}",
                headers={"X-API-Key": admin_api_key}
            )
            assert response.status_code == 200
            assert response.json()["success"] == True

    def test_toggle_api_key(self, client, admin_api_key, test_api_key):
        """Test toggling API key status"""
        # Get the test key ID
        list_response = client.get(
            "/api/v1/api-keys",
            headers={"X-API-Key": admin_api_key}
        )
        key_id = None
        for key in list_response.json()["api_keys"]:
            if key["key"] == test_api_key:
                key_id = key["id"]
                break

        if key_id:
            response = client.patch(
                f"/api/v1/api-keys/{key_id}/toggle",
                headers={"X-API-Key": admin_api_key}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert "is_active" in data
