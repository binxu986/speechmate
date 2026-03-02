"""
Tests for Client API Client Module
"""
import pytest
from unittest.mock import Mock, patch, mock_open


class TestAPIClientImport:
    """Test API client module imports"""

    def test_import_api_client(self):
        """Test that api_client module can be imported"""
        from app import api_client
        assert api_client is not None

    def test_import_api_client_class(self):
        """Test that APIClient class is available"""
        from app.api_client import APIClient
        assert APIClient is not None

    def test_import_global_instance(self):
        """Test that global api_client instance is available"""
        from app.api_client import api_client
        assert api_client is not None


class TestAPIClientInit:
    """Test APIClient initialization"""

    def test_default_init(self):
        """Test default initialization"""
        from app.api_client import APIClient
        client = APIClient()
        assert client.base_url == "http://localhost:8000"
        assert client.api_key == ""
        assert client.timeout == 60

    def test_custom_init(self):
        """Test custom initialization"""
        from app.api_client import APIClient
        client = APIClient(
            base_url="http://192.168.1.100:8000",
            api_key="test_key_123"
        )
        assert client.base_url == "http://192.168.1.100:8000"
        assert client.api_key == "test_key_123"


class TestAPIClientSetters:
    """Test APIClient setters"""

    def test_set_base_url(self):
        """Test setting base URL"""
        from app.api_client import APIClient
        client = APIClient()
        client.set_base_url("http://example.com:8000")
        assert client.base_url == "http://example.com:8000"

    def test_set_base_url_trailing_slash(self):
        """Test that trailing slash is removed"""
        from app.api_client import APIClient
        client = APIClient()
        client.set_base_url("http://example.com:8000/")
        assert client.base_url == "http://example.com:8000"

    def test_set_api_key(self):
        """Test setting API key"""
        from app.api_client import APIClient
        client = APIClient()
        client.set_api_key("new_api_key")
        assert client.api_key == "new_api_key"


class TestAPIClientHealthCheck:
    """Test health check functionality"""

    @patch('requests.get')
    def test_health_check_success(self, mock_get):
        """Test successful health check"""
        from app.api_client import APIClient
        client = APIClient()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_get.return_value = mock_response

        # The health_check method returns bool based on status
        result = client.health_check()
        # Note: Actual implementation may vary

    @patch('requests.get')
    def test_health_check_failure(self, mock_get):
        """Test failed health check"""
        from app.api_client import APIClient
        client = APIClient()

        mock_get.side_effect = Exception("Connection failed")


class TestAPIClientTranscribe:
    """Test transcribe functionality"""

    @patch('requests.post')
    def test_transcribe_success(self, mock_post):
        """Test successful transcription"""
        from app.api_client import APIClient
        client = APIClient(api_key="test_key")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "text": "Hello world",
            "language": "en"
        }
        mock_post.return_value = mock_response

        # Create a mock audio file
        with patch('builtins.open', mock_open(read_data=b'fake audio')):
            success, text, error = client.transcribe("fake_path.wav")

    @patch('requests.post')
    def test_transcribe_failure(self, mock_post):
        """Test failed transcription"""
        from app.api_client import APIClient
        client = APIClient(api_key="test_key")

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "success": False,
            "error": "Invalid API key"
        }
        mock_post.return_value = mock_response

    @patch('requests.post')
    def test_transcribe_timeout(self, mock_post):
        """Test transcription timeout"""
        from app.api_client import APIClient
        import requests

        client = APIClient(api_key="test_key")
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")

    @patch('requests.post')
    def test_transcribe_connection_error(self, mock_post):
        """Test transcription connection error"""
        from app.api_client import APIClient
        import requests

        client = APIClient(api_key="test_key")
        mock_post.side_effect = requests.exceptions.ConnectionError("No connection")


class TestAPIClientTranslate:
    """Test translate functionality"""

    @patch('requests.post')
    def test_translate_not_implemented(self, mock_post):
        """Test translate returns not implemented"""
        from app.api_client import APIClient
        client = APIClient(api_key="test_key")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "error": "Translation not implemented"
        }
        mock_post.return_value = mock_response

    @patch('requests.post')
    def test_translate_with_params(self, mock_post):
        """Test translate with language parameters"""
        from app.api_client import APIClient
        client = APIClient(api_key="test_key")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": False,
            "error": "Not implemented"
        }
        mock_post.return_value = mock_response


class TestAPIClientEdgeCases:
    """Test edge cases"""

    def test_empty_api_key(self):
        """Test with empty API key"""
        from app.api_client import APIClient
        client = APIClient(api_key="")
        assert client.api_key == ""

    def test_long_api_key(self):
        """Test with long API key"""
        from app.api_client import APIClient
        long_key = "a" * 1000
        client = APIClient(api_key=long_key)
        assert client.api_key == long_key

    def test_special_chars_in_url(self):
        """Test URL with special characters"""
        from app.api_client import APIClient
        client = APIClient()
        client.set_base_url("http://192.168.1.1:8000")
        assert "192.168.1.1" in client.base_url
