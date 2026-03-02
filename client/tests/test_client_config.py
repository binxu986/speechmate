"""
Tests for Client Configuration Module
"""
import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestConfigImport:
    """Test config module imports"""

    def test_import_config(self):
        """Test that config module can be imported"""
        from app import config
        assert config is not None

    def test_import_config_classes(self):
        """Test that config classes are available"""
        from app.config import ClientConfig, HotkeyConfig
        assert ClientConfig is not None
        assert HotkeyConfig is not None

    def test_import_global_config(self):
        """Test that global config instance is available"""
        from app.config import config
        assert config is not None


class TestHotkeyConfig:
    """Test HotkeyConfig model"""

    def test_default_values(self):
        """Test default hotkey values"""
        from app.config import HotkeyConfig

        hc = HotkeyConfig()
        assert hc.transcribe == "alt"
        assert hc.translate_zh_to_en == "shift"
        assert hc.translate_en_to_zh == "shift+a"

    def test_custom_values(self):
        """Test custom hotkey values"""
        from app.config import HotkeyConfig

        hc = HotkeyConfig(
            transcribe="ctrl+alt+t",
            translate_zh_to_en="ctrl+shift+z",
            translate_en_to_zh="ctrl+shift+e"
        )
        assert hc.transcribe == "ctrl+alt+t"
        assert hc.translate_zh_to_en == "ctrl+shift+z"
        assert hc.translate_en_to_zh == "ctrl+shift+e"


class TestClientConfig:
    """Test ClientConfig model"""

    def test_default_values(self):
        """Test default configuration values"""
        from app.config import ClientConfig

        cc = ClientConfig()
        assert cc.base_url == "http://localhost:8000"
        assert cc.api_key == ""
        assert cc.auto_start == False
        assert cc.minimize_to_tray == True
        assert cc.show_recording_indicator == True
        assert cc.language == "auto"

    def test_custom_values(self):
        """Test custom configuration values"""
        from app.config import ClientConfig

        cc = ClientConfig(
            base_url="http://192.168.1.100:8000",
            api_key="test_key_123",
            auto_start=True,
            language="zh"
        )
        assert cc.base_url == "http://192.168.1.100:8000"
        assert cc.api_key == "test_key_123"
        assert cc.auto_start == True
        assert cc.language == "zh"

    def test_nested_hotkey_config(self):
        """Test nested hotkey configuration"""
        from app.config import ClientConfig, HotkeyConfig

        hc = HotkeyConfig(transcribe="f1")
        cc = ClientConfig(hotkeys=hc)
        assert cc.hotkeys.transcribe == "f1"


class TestConfigSaveLoad:
    """Test configuration save and load"""

    def test_save_config(self, tmp_path):
        """Test saving configuration"""
        from app.config import ClientConfig, HotkeyConfig

        config = ClientConfig(
            base_url="http://test:8000",
            api_key="test_key",
            hotkeys=HotkeyConfig(transcribe="f1")
        )

        # Save to temp file
        config_file = tmp_path / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config.model_dump(), f)

        # Verify file exists
        assert config_file.exists()

        # Load and verify
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["base_url"] == "http://test:8000"
        assert data["api_key"] == "test_key"
        assert data["hotkeys"]["transcribe"] == "f1"

    def test_load_config(self, tmp_path):
        """Test loading configuration"""
        from app.config import ClientConfig

        # Create config file
        config_data = {
            "base_url": "http://loaded:8000",
            "api_key": "loaded_key",
            "hotkeys": {
                "transcribe": "f2",
                "translate_zh_to_en": "f3",
                "translate_en_to_zh": "f4"
            }
        }

        config_file = tmp_path / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f)

        # Load config
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        config = ClientConfig(**data)
        assert config.base_url == "http://loaded:8000"
        assert config.api_key == "loaded_key"
        assert config.hotkeys.transcribe == "f2"


class TestConfigValidation:
    """Test configuration validation"""

    def test_valid_language_values(self):
        """Test valid language values"""
        from app.config import ClientConfig

        for lang in ["auto", "zh", "en"]:
            cc = ClientConfig(language=lang)
            assert cc.language == lang

    def test_valid_url_format(self):
        """Test URL format"""
        from app.config import ClientConfig

        cc = ClientConfig(base_url="http://localhost:8000")
        assert cc.base_url.startswith("http://")


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

    def test_config_file_path(self):
        """Test config file path"""
        from app.config import CONFIG_FILE
        assert CONFIG_FILE.name == "config.json"


class TestConfigEdgeCases:
    """Test edge cases"""

    def test_empty_api_key(self):
        """Test with empty API key"""
        from app.config import ClientConfig

        cc = ClientConfig(api_key="")
        assert cc.api_key == ""

    def test_long_api_key(self):
        """Test with long API key"""
        from app.config import ClientConfig

        long_key = "a" * 100
        cc = ClientConfig(api_key=long_key)
        assert cc.api_key == long_key

    def test_url_with_port(self):
        """Test URL with custom port"""
        from app.config import ClientConfig

        cc = ClientConfig(base_url="http://192.168.1.1:9000")
        assert ":9000" in cc.base_url

    def test_url_with_https(self):
        """Test URL with HTTPS"""
        from app.config import ClientConfig

        cc = ClientConfig(base_url="https://api.example.com")
        assert cc.base_url.startswith("https://")

    def test_model_dump(self):
        """Test model_dump method"""
        from app.config import ClientConfig

        cc = ClientConfig()
        data = cc.model_dump()

        assert "base_url" in data
        assert "api_key" in data
        assert "hotkeys" in data
        assert isinstance(data["hotkeys"], dict)
