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


class TestConfigValidation:
    """Test configuration validation"""

    def test_valid_asr_models(self):
        """Test that all ASR models in config are valid"""
        from app.config import ASR_MODELS

        for model_name, model_info in ASR_MODELS.items():
            assert "name" in model_info
            assert "size" in model_info
            assert "description" in model_info

    def test_server_port_range(self):
        """Test that server ports are in valid range"""
        from app.config import config

        assert 1 <= config.server.api_port <= 65535
        assert 1 <= config.server.web_port <= 65535

    def test_model_device_value(self):
        """Test that model device is valid"""
        from app.config import config

        assert config.model.asr_device in ["cpu", "cuda"]

    def test_model_compute_type_value(self):
        """Test that compute type is valid"""
        from app.config import config

        assert config.model.asr_compute_type in ["float16", "int8", "int8_float16"]


class TestConfigAdminSettings:
    """Test admin settings"""

    def test_admin_api_key_exists(self):
        """Test that admin API key is generated"""
        from app.config import config

        assert config.admin_api_key is not None
        assert len(config.admin_api_key) > 0

    def test_jwt_secret_exists(self):
        """Test that JWT secret is generated"""
        from app.config import config

        assert config.jwt_secret is not None
        assert len(config.jwt_secret) > 0

    def test_admin_api_key_format(self):
        """Test that admin API key is hex string"""
        from app.config import config

        # Should be valid hex string
        try:
            int(config.admin_api_key, 16)
            assert True
        except ValueError:
            assert False, "Admin API key should be hex string"


class TestConfigModelConfig:
    """Test model configuration model"""

    def test_model_config_defaults(self):
        """Test ModelConfig default values"""
        from app.config import ModelConfig

        mc = ModelConfig()
        assert mc.asr_model == "small"
        assert mc.asr_device in ["cpu", "cuda"]
        assert mc.asr_compute_type in ["int8", "float16"]

    def test_server_config_defaults(self):
        """Test ServerConfig default values"""
        from app.config import ServerConfig

        sc = ServerConfig()
        assert sc.api_host == "0.0.0.0"
        assert sc.api_port == 8000
        assert sc.web_host == "0.0.0.0"
        assert sc.web_port == 5000
        assert sc.debug == False


class TestConfigPaths:
    """Test configuration paths"""

    def test_base_dir_exists(self):
        """Test that BASE_DIR exists"""
        from app.config import BASE_DIR

        assert BASE_DIR.exists()

    def test_data_dir_created(self):
        """Test that DATA_DIR is created"""
        from app.config import DATA_DIR

        assert DATA_DIR.exists()

    def test_logs_dir_created(self):
        """Test that LOGS_DIR is created"""
        from app.config import LOGS_DIR

        assert LOGS_DIR.exists()

    def test_models_dir_created(self):
        """Test that MODELS_DIR is created"""
        from app.config import MODELS_DIR

        assert MODELS_DIR.exists()