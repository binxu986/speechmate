"""
Tests for ASR Model Module
"""
import pytest
from pathlib import Path


class TestASRModelImport:
    """Test ASR model imports"""

    def test_import_asr_model(self):
        """Test that asr_model module can be imported"""
        from models import asr_model
        assert asr_model is not None

    def test_import_functions(self):
        """Test that all required functions are available"""
        from models.asr_model import (
            get_asr_model,
            transcribe_audio,
            get_audio_duration,
            unload_model,
            get_model_info,
            check_available_models,
            has_any_model,
            get_download_hint
        )
        assert callable(get_asr_model)
        assert callable(transcribe_audio)
        assert callable(get_audio_duration)
        assert callable(unload_model)
        assert callable(get_model_info)
        assert callable(check_available_models)
        assert callable(has_any_model)
        assert callable(get_download_hint)


class TestASRModelFunctions:
    """Test ASR model functions"""

    def test_get_model_info_no_model(self):
        """Test get_model_info when no model is loaded"""
        from models.asr_model import get_model_info, unload_model

        # Ensure no model is loaded
        unload_model()

        info = get_model_info()
        assert info["loaded"] == False

    def test_unload_model_no_model(self):
        """Test unload_model when no model is loaded"""
        from models.asr_model import unload_model

        # Should not raise error
        unload_model()

    def test_get_audio_duration_invalid(self):
        """Test get_audio_duration with invalid file"""
        from models.asr_model import get_audio_duration

        duration = get_audio_duration("nonexistent_file.wav")
        assert duration == 0.0

    def test_check_available_models(self):
        """Test check_available_models function"""
        from models.asr_model import check_available_models

        available = check_available_models()
        assert isinstance(available, dict)
        assert "tiny" in available
        assert "small" in available
        assert "large-v3" in available
        # All should be False if no models downloaded
        assert all(isinstance(v, bool) for v in available.values())

    def test_has_any_model(self):
        """Test has_any_model function"""
        from models.asr_model import has_any_model

        result = has_any_model()
        assert isinstance(result, bool)

    def test_get_download_hint(self):
        """Test get_download_hint function"""
        from models.asr_model import get_download_hint

        hint = get_download_hint("small")
        assert isinstance(hint, str)
        assert "small" in hint
        assert "download_model.py" in hint

    def test_get_asr_model_not_found(self):
        """Test get_asr_model raises error when model not downloaded"""
        from models.asr_model import get_asr_model

        with pytest.raises(RuntimeError) as exc_info:
            get_asr_model("small")

        error_msg = str(exc_info.value).lower()
        assert "not downloaded" in error_msg or "not found" in error_msg

    def test_transcribe_audio_model_not_found(self, sample_audio_path):
        """Test transcribe_audio raises error when model not downloaded"""
        from models.asr_model import transcribe_audio

        with pytest.raises(RuntimeError) as exc_info:
            transcribe_audio(sample_audio_path, model_name="small")

        assert "not downloaded" in str(exc_info.value).lower()


class TestASRModelLoading:
    """Test ASR model loading (requires network for first download)"""

    @pytest.mark.slow
    def test_load_tiny_model(self):
        """Test loading tiny model"""
        from models.asr_model import get_asr_model, unload_model, get_model_info

        try:
            model = get_asr_model("tiny", "cpu", "int8")
            assert model is not None

            info = get_model_info()
            assert info["loaded"] == True
            assert info["model_name"] == "tiny"
            assert info["device"] == "cpu"

        finally:
            unload_model()

    @pytest.mark.slow
    def test_model_caching(self):
        """Test that model is cached properly"""
        from models.asr_model import get_asr_model, unload_model

        try:
            # Load model first time
            model1 = get_asr_model("tiny", "cpu", "int8")

            # Load same model again - should return cached
            model2 = get_asr_model("tiny", "cpu", "int8")

            assert model1 is model2

        finally:
            unload_model()


class TestASRTranscription:
    """Test audio transcription"""

    @pytest.mark.slow
    def test_transcribe_audio(self, sample_audio_path):
        """Test transcribing audio file"""
        from models.asr_model import transcribe_audio, unload_model

        try:
            text, lang, time_taken = transcribe_audio(
                sample_audio_path,
                model_name="tiny",
                device="cpu"
            )

            assert isinstance(text, str)
            assert isinstance(lang, str)
            assert isinstance(time_taken, float)
            assert time_taken > 0

        finally:
            unload_model()

    @pytest.mark.slow
    def test_transcribe_with_language(self, sample_audio_path):
        """Test transcribing with specified language"""
        from models.asr_model import transcribe_audio, unload_model

        try:
            text, lang, time_taken = transcribe_audio(
                sample_audio_path,
                model_name="tiny",
                device="cpu",
                language="en"
            )

            assert isinstance(text, str)
            # Language should be what we specified or detected
            assert lang in ["en", "english"]

        finally:
            unload_model()

    def test_transcribe_nonexistent_file(self):
        """Test transcribing nonexistent file raises error"""
        from models.asr_model import transcribe_audio

        with pytest.raises(FileNotFoundError):
            transcribe_audio("nonexistent.wav", model_name="tiny", device="cpu")


class TestASRAudioDuration:
    """Test audio duration functionality"""

    def test_get_audio_duration_valid(self, sample_audio_path):
        """Test get_audio_duration with valid file"""
        from models.asr_model import get_audio_duration

        duration = get_audio_duration(sample_audio_path)
        assert duration > 0
        assert duration == 3.0  # test_audio.wav is 3 seconds

    def test_get_audio_duration_short(self, sample_audio_short_path):
        """Test get_audio_duration with short audio"""
        from models.asr_model import get_audio_duration

        duration = get_audio_duration(sample_audio_short_path)
        assert duration > 0
        assert duration == 0.5  # 0.5 seconds

    def test_get_audio_duration_silent(self, sample_audio_silent_path):
        """Test get_audio_duration with silent audio"""
        from models.asr_model import get_audio_duration

        duration = get_audio_duration(sample_audio_silent_path)
        assert duration > 0
        assert duration == 2.0  # 2 seconds

    def test_get_audio_duration_directory(self, tmp_path):
        """Test get_audio_duration with directory path"""
        from models.asr_model import get_audio_duration

        # Should return 0.0 for directory
        duration = get_audio_duration(str(tmp_path))
        assert duration == 0.0


class TestASRModelConfig:
    """Test ASR model configuration"""

    def test_invalid_model_name(self):
        """Test that invalid model name is handled"""
        from models.asr_model import get_asr_model, unload_model

        # Invalid model name should raise error (model not found)
        with pytest.raises(RuntimeError):
            get_asr_model("invalid_model_name")

        unload_model()

    def test_unload_model_multiple_times(self):
        """Test unloading model multiple times doesn't error"""
        from models.asr_model import unload_model

        # Should not raise any errors
        unload_model()
        unload_model()
        unload_model()

    def test_get_download_hint_different_models(self):
        """Test get_download_hint for different models"""
        from models.asr_model import get_download_hint

        for model_name in ["tiny", "base", "small", "medium", "large-v3"]:
            hint = get_download_hint(model_name)
            assert model_name in hint
            assert "download_model.py" in hint


class TestASRTranscriptionErrors:
    """Test transcription error handling"""

    def test_transcribe_empty_file(self, tmp_path):
        """Test transcribing empty file raises error"""
        from models.asr_model import transcribe_audio

        # Create empty file
        empty_file = tmp_path / "empty.wav"
        empty_file.touch()

        with pytest.raises(ValueError, match="empty"):
            transcribe_audio(str(empty_file), model_name="small")

    def test_transcribe_directory(self, tmp_path):
        """Test transcribing directory raises error"""
        from models.asr_model import transcribe_audio

        # Directory will raise ValueError (empty) or other error
        with pytest.raises((FileNotFoundError, ValueError, IsADirectoryError)):
            transcribe_audio(str(tmp_path), model_name="small")