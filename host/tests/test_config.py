"""
Tests for Configuration Module
"""
import pytest
from pathlib import Path


class TestConfigImport:
    """Test config module imports"""

    def test_import_config(self):
        """Test that config module can be imported"""
        from app import config
        assert config is not None

    def test_import_config_class(self):
        """Test that Config class is available"""
        from app.config import Config
        assert Config is not None

    def test_import_global_config(self):
        """Test that global config instance is available"""
        from app.config import config
        assert config is not None


class TestConfigValues:
    """Test configuration values"""

    def test_server_config(self):
        """Test server configuration"""
        from app.config import config

        assert hasattr(config, "server")
        assert hasattr(config.server, "api_host")
        assert hasattr(config.server, "api_port")
        assert config.server.api_port > 0

    def test_model_config(self):
        """Test model configuration"""
        from app.config import config

        assert hasattr(config, "model")
        assert hasattr(config.model, "asr_model")
        assert hasattr(config.model, "asr_device")
        assert hasattr(config.model, "asr_compute_type")

    def test_database_config(self):
        """Test database configuration"""
        from app.config import config

        assert hasattr(config, "database")
        assert hasattr(config.database, "db_path")

    def test_asr_models_dict(self):
        """Test ASR_MODELS dictionary"""
        from app.config import ASR_MODELS

        assert isinstance(ASR_MODELS, dict)
        assert "tiny" in ASR_MODELS
        assert "base" in ASR_MODELS
        assert "small" in ASR_MODELS
        assert "medium" in ASR_MODELS
        assert "large-v3" in ASR_MODELS


class TestConfigFunctions:
    """Test configuration functions"""

    def test_get_local_ip(self):
        """Test get_local_ip function"""
        from app.config import get_local_ip

        ip = get_local_ip()
        assert isinstance(ip, str)
        # Should be a valid IP format
        parts = ip.split(".")
        assert len(parts) == 4

    def test_get_base_url(self):
        """Test get_base_url function"""
        from app.config import get_base_url

        url = get_base_url()
        assert isinstance(url, str)
        assert url.startswith("http://")

    def test_detect_gpu(self):
        """Test detect_gpu function"""
        from app.config import detect_gpu

        device, compute_type = detect_gpu()
        assert device in ["cpu", "cuda"]
        assert compute_type in ["float16", "int8", "int8_float16"]


class TestConfigSaveLoad:
    """Test configuration save/load"""

    def test_save_config(self, tmp_path):
        """Test saving configuration"""
        from app.config import config, save_config

        # This should not raise error
        save_config()

    def test_load_config_from_file(self, tmp_path):
        """Test loading configuration from file"""
        from app.config import load_config_from_file

        # This should not raise error even if file doesn't exist
        load_config_from_file()