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
            get_model_info
        )
        assert callable(get_asr_model)
        assert callable(transcribe_audio)
        assert callable(get_audio_duration)
        assert callable(unload_model)
        assert callable(get_model_info)


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