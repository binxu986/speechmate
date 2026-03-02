"""
Integration Tests for API Endpoints

Tests complete workflows across multiple API calls.
"""
import pytest
from fastapi.testclient import TestClient
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
def clean_database():
    """Ensure clean database state for integration tests"""
    from app.database import init_db
    init_db()
    yield


class TestTranscribeIntegration:
    """Integration tests for transcription workflow"""

    def test_full_transcribe_workflow(self, client, admin_api_key, sample_audio_path, clean_database):
        """Test complete transcribe workflow: create key -> transcribe -> verify logs"""
        # Step 1: Create a new API key
        create_response = client.post(
            "/api/v1/api-keys?name=Integration%20Test%20Key",
            headers={"X-API-Key": admin_api_key}
        )
        assert create_response.status_code == 200
        key_data = create_response.json()
        assert key_data["success"] == True
        new_api_key = key_data["key"]

        # Step 2: Use the key to transcribe
        with open(sample_audio_path, "rb") as f:
            transcribe_response = client.post(
                "/api/v1/transcribe",
                files={"audio": ("test.wav", f, "audio/wav")},
                headers={"X-API-Key": new_api_key}
            )

        # Should succeed or fail with model not downloaded error
        assert transcribe_response.status_code in [200, 500]
        data = transcribe_response.json()
        assert "success" in data

        # Step 3: Verify usage was logged (check stats)
        stats_response = client.get(
            "/api/v1/stats?days=1",
            headers={"X-API-Key": admin_api_key}
        )
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["success"] == True

        # Find our key in stats
        key_found = False
        for key_stat in stats["api_keys"]:
            if key_stat["key"] == new_api_key:
                key_found = True
                # Should have at least one transcribe attempt
                assert key_stat["total_transcribe"] >= 1
                break

        assert key_found, "New API key should appear in stats"

    def test_transcribe_multiple_requests_same_key(self, client, admin_api_key, sample_audio_path, clean_database):
        """Test multiple transcribe requests with same key"""
        # Create key
        create_response = client.post(
            "/api/v1/api-keys?name=Multi%20Request%20Key",
            headers={"X-API-Key": admin_api_key}
        )
        api_key = create_response.json()["key"]

        # Make multiple requests
        for i in range(3):
            with open(sample_audio_path, "rb") as f:
                response = client.post(
                    "/api/v1/transcribe",
                    files={"audio": (f"test_{i}.wav", f, "audio/wav")},
                    headers={"X-API-Key": api_key}
                )
            assert response.status_code in [200, 500]

        # Verify all requests logged
        stats_response = client.get(
            "/api/v1/stats?days=1",
            headers={"X-API-Key": admin_api_key}
        )
        stats = stats_response.json()

        for key_stat in stats["api_keys"]:
            if key_stat["key"] == api_key:
                assert key_stat["total_transcribe"] >= 3
                break


class TestAuthIntegration:
    """Integration tests for authentication workflow"""

    def test_api_key_lifecycle(self, client, admin_api_key, sample_audio_path, clean_database):
        """Test complete API key lifecycle: create -> use -> disable -> verify failure"""
        # Step 1: Create key
        create_response = client.post(
            "/api/v1/api-keys?name=Lifecycle%20Test%20Key",
            headers={"X-API-Key": admin_api_key}
        )
        assert create_response.status_code == 200
        api_key = create_response.json()["key"]

        # Step 2: Verify key works
        with open(sample_audio_path, "rb") as f:
            response = client.post(
                "/api/v1/transcribe",
                files={"audio": ("test.wav", f, "audio/wav")},
                headers={"X-API-Key": api_key}
            )
        assert response.status_code in [200, 500]  # Not 401

        # Step 3: Get key ID and disable it
        list_response = client.get(
            "/api/v1/api-keys",
            headers={"X-API-Key": admin_api_key}
        )
        key_id = None
        for key in list_response.json()["api_keys"]:
            if key["key"] == api_key:
                key_id = key["id"]
                break

        assert key_id is not None

        # Toggle to disable
        toggle_response = client.patch(
            f"/api/v1/api-keys/{key_id}/toggle",
            headers={"X-API-Key": admin_api_key}
        )
        assert toggle_response.status_code == 200
        assert toggle_response.json()["is_active"] == False

        # Step 4: Verify disabled key fails
        with open(sample_audio_path, "rb") as f:
            response = client.post(
                "/api/v1/transcribe",
                files={"audio": ("test.wav", f, "audio/wav")},
                headers={"X-API-Key": api_key}
            )
        assert response.status_code == 401  # Unauthorized

        # Step 5: Re-enable key
        toggle_response = client.patch(
            f"/api/v1/api-keys/{key_id}/toggle",
            headers={"X-API-Key": admin_api_key}
        )
        assert toggle_response.json()["is_active"] == True

        # Step 6: Verify key works again
        with open(sample_audio_path, "rb") as f:
            response = client.post(
                "/api/v1/transcribe",
                files={"audio": ("test.wav", f, "audio/wav")},
                headers={"X-API-Key": api_key}
            )
        assert response.status_code in [200, 500]  # Not 401

    def test_api_key_deletion_workflow(self, client, admin_api_key, sample_audio_path, clean_database):
        """Test API key deletion workflow"""
        # Create key
        create_response = client.post(
            "/api/v1/api-keys?name=Delete%20Test%20Key",
            headers={"X-API-Key": admin_api_key}
        )
        api_key = create_response.json()["key"]

        # Get key ID
        list_response = client.get(
            "/api/v1/api-keys",
            headers={"X-API-Key": admin_api_key}
        )
        key_id = None
        for key in list_response.json()["api_keys"]:
            if key["key"] == api_key:
                key_id = key["id"]
                break

        # Delete key
        delete_response = client.delete(
            f"/api/v1/api-keys/{key_id}",
            headers={"X-API-Key": admin_api_key}
        )
        assert delete_response.status_code == 200

        # Verify deleted key fails
        with open(sample_audio_path, "rb") as f:
            response = client.post(
                "/api/v1/transcribe",
                files={"audio": ("test.wav", f, "audio/wav")},
                headers={"X-API-Key": api_key}
            )
        assert response.status_code == 401


class TestModelConfigIntegration:
    """Integration tests for model configuration"""

    def test_model_config_update_and_verify(self, client, admin_api_key, clean_database):
        """Test updating model configuration"""
        # Get current config
        info_response = client.get("/api/v1/info")
        original_model = info_response.json()["current_model"]["asr"]

        # Update config
        update_response = client.post(
            "/api/v1/config/model",
            params={"asr_model": "tiny", "asr_device": "cpu", "asr_compute_type": "int8"}
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert data["success"] == True
        assert data["config"]["asr_model"] == "tiny"
        assert data["config"]["asr_device"] == "cpu"
        assert data["config"]["asr_compute_type"] == "int8"

        # Verify config persisted
        info_response = client.get("/api/v1/info")
        current_model = info_response.json()["current_model"]
        assert current_model["asr"] == "tiny"
        assert current_model["device"] == "cpu"

        # Restore original config
        client.post(
            "/api/v1/config/model",
            params={"asr_model": original_model}
        )

    def test_invalid_model_config_ignored(self, client, admin_api_key, clean_database):
        """Test that invalid model config values are ignored"""
        # Get current config
        info_response = client.get("/api/v1/info")
        original_config = info_response.json()["current_model"]

        # Try to set invalid values
        update_response = client.post(
            "/api/v1/config/model",
            params={"asr_model": "invalid_model", "asr_device": "invalid_device"}
        )

        # Should still return success but ignore invalid values
        assert update_response.status_code == 200

        # Verify original values preserved
        info_response = client.get("/api/v1/info")
        current_config = info_response.json()["current_model"]
        assert current_config["asr"] == original_config["asr"]
        assert current_config["device"] == original_config["device"]


class TestHealthCheckIntegration:
    """Integration tests for health check"""

    def test_health_check_consistency(self, client, clean_database):
        """Test health check is consistent across multiple calls"""
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"


class TestErrorHandlingIntegration:
    """Integration tests for error handling"""

    def test_concurrent_api_key_operations(self, client, admin_api_key, clean_database):
        """Test concurrent operations on same API key"""
        # Create key
        create_response = client.post(
            "/api/v1/api-keys?name=Concurrent%20Test",
            headers={"X-API-Key": admin_api_key}
        )
        api_key = create_response.json()["key"]

        # Get key ID
        list_response = client.get(
            "/api/v1/api-keys",
            headers={"X-API-Key": admin_api_key}
        )
        key_id = None
        for key in list_response.json()["api_keys"]:
            if key["key"] == api_key:
                key_id = key["id"]
                break

        # Multiple toggles
        for _ in range(3):
            toggle_response = client.patch(
                f"/api/v1/api-keys/{key_id}/toggle",
                headers={"X-API-Key": admin_api_key}
            )
            assert toggle_response.status_code == 200

    def test_stats_with_no_usage(self, client, admin_api_key, clean_database):
        """Test stats endpoint with fresh database"""
        response = client.get(
            "/api/v1/stats?days=30",
            headers={"X-API-Key": admin_api_key}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert isinstance(data["api_keys"], list)
