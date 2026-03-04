"""
Tests for Model Downloader Module
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


sys.path.insert(0, str(Path(__file__).parent.parent))


class TestModelDownloader:
    """Test ModelDownloader class"""

    def test_model_sizes(self):
        """Test model size definitions"""
        from models.model_downloader import ModelDownloader

        assert "tiny" in ModelDownloader.MODEL_SIZES
        assert "base" in ModelDownloader.MODEL_SIZES
        assert "small" in ModelDownloader.MODEL_SIZES
        assert "medium" in ModelDownloader.MODEL_SIZES
        assert "large-v3" in ModelDownloader.MODEL_SIZES

        # Verify sizes are reasonable (in bytes)
        assert ModelDownloader.MODEL_SIZES["tiny"] < 100 * 1024 * 1024  # 39MB
        assert ModelDownloader.MODEL_SIZES["large-v3"] > 1024 * 1024 * 1024  # 1.5GB

    def test_model_info(self):
        """Test model info definitions"""
        from models.model_downloader import ModelDownloader

        assert "tiny" in ModelDownloader.MODEL_INFO
        assert "small" in ModelDownloader.MODEL_INFO
        assert "name" in ModelDownloader.MODEL_INFO["tiny"]
        assert "size" in ModelDownloader.MODEL_INFO["tiny"]
        assert "description" in ModelDownloader.MODEL_INFO["tiny"]

    def test_init_downloader(self):
        """Test downloader initialization"""
        from models.model_downloader import ModelDownloader
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            downloader = ModelDownloader(download_root=str(tmp_dir))
            assert downloader.download_root == str(tmp_dir)
            assert Path(downloader.download_root).exists()

    def test_is_model_downloaded(self):
        """Test is_model_downloaded method"""
        from models.model_downloader import ModelDownloader
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            downloader = ModelDownloader(download_root=str(tmp_dir))
            # Should not exist by default
            assert not downloader.is_model_downloaded("tiny")
            assert not downloader.is_model_downloaded("base")
            assert not downloader.is_model_downloaded("nonexistent_model")

    def test_get_all_download_status(self):
        """Test get_all_download_status method"""
        from models.model_downloader import ModelDownloader
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            downloader = ModelDownloader(download_root=str(tmp_dir))
            status = downloader.get_all_download_status()

            assert "tiny" in status
            assert "base" in status
            assert "small" in status
            assert "medium" in status
            assert "large-v3" in status

            for model_name, model_status in status.items():
                # Status is a DownloadProgress object with to_dict() method
                status_dict = model_status.to_dict() if hasattr(model_status, 'to_dict') else model_status
                assert "model_name" in status_dict
                assert "status" in status_dict
                assert "progress" in status_dict

    def test_get_model_status(self):
        """Test get_model_status method"""
        from models.model_downloader import ModelDownloader
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            downloader = ModelDownloader(download_root=str(tmp_dir))
            status = downloader.get_model_status("tiny")

            # Status is a DownloadProgress object
            assert hasattr(status, 'model_name')
            assert status.model_name == "tiny"
            assert hasattr(status, 'status')
            assert hasattr(status, 'progress')

    def test_start_download_invalid_model(self):
        """Test start_download with invalid model"""
        from models.model_downloader import ModelDownloader
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            downloader = ModelDownloader(download_root=str(tmp_dir))
            result = downloader.start_download("invalid_model")
            assert result == False


class TestModelDownloaderSingleton:
    """Test singleton pattern"""

    def test_get_downloader_singleton(self):
        """Test get_downloader returns same instance"""
        from models.model_downloader import get_downloader, _downloader
        import models.model_downloader as md

        # Reset singleton
        md._downloader = None

        downloader1 = get_downloader()
        downloader2 = get_downloader()
        assert downloader1 is downloader2

        # Cleanup
        md._downloader = None


class TestDownloadProgress:
    """Test DownloadProgress dataclass"""

    def test_download_progress_to_dict(self):
        """Test DownloadProgress.to_dict() method"""
        from models.model_downloader import DownloadProgress, DownloadStatus

        progress = DownloadProgress(
            model_name="test_model",
            status=DownloadStatus.DOWNLOADING,
            progress=50.0,
            downloaded_bytes=1024 * 1024,
            total_bytes=2 * 1024 * 1024,
            speed="1.0 MB/s"
        )

        result = progress.to_dict()
        assert result["model_name"] == "test_model"
        assert result["status"] == "downloading"
        assert result["progress"] == 50.0
        assert result["downloaded_bytes"] == 1024 * 1024
        assert result["total_bytes"] == 2 * 1024 * 1024
        assert result["speed"] == "1.0 MB/s"

    def test_download_status_structure(self):
        """Test download status has correct structure"""
        from models.model_downloader import ModelDownloader
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            downloader = ModelDownloader(download_root=str(tmp_dir))
            status = downloader.get_model_status("small")

            # Check attributes exist
            assert hasattr(status, 'model_name')
            assert hasattr(status, 'status')
            assert hasattr(status, 'progress')
            assert hasattr(status, 'to_dict')
