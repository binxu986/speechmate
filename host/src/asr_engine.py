import os
import io
from typing import Optional, Dict, Union
import numpy as np
import torch
from faster_whisper import WhisperModel


class ASREngine:
    def __init__(self, model_name: str = "base", device: str = "cpu", compute_type: str = "int8"):
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type if device == "cpu" else "float16"
        self.model = None
        
    def load_model(self):
        if self.model is None:
            self.model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type
            )
        return self.model
    
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, any]:
        model = self.load_model()
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True
        )
        text = " ".join([seg.text for seg in segments])
        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability
        }
    
    def transcribe_audio_data(self, audio_data: bytes, sample_rate: int = 16000) -> Dict[str, any]:
        import soundfile as sf
        
        audio_buffer = io.BytesIO(audio_data)
        try:
            audio_array, sr = sf.read(audio_buffer)
        except Exception as e:
            raise ValueError(f"Failed to read audio data: {e}")
        
        if sr != sample_rate:
            try:
                import librosa
                audio_array = librosa.resample(audio_array, orig_sr=sr, target_sr=sample_rate)
            except ImportError:
                from scipy import signal
                num_samples = int(len(audio_array) * sample_rate / sr)
                audio_array = signal.resample(audio_array, num_samples)
        
        if audio_array.ndim > 1:
            audio_array = audio_array.mean(axis=1)
        
        audio_array = audio_array.astype(np.float32)
        
        model = self.load_model()
        segments, info = model.transcribe(
            audio_array,
            language=None,
            beam_size=5
        )
        text = "".join([seg.text for seg in segments])
        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability
        }
    
    def transcribe_numpy(self, audio_array: np.ndarray, sample_rate: int = 16000) -> Dict[str, any]:
        if audio_array.ndim > 1:
            audio_array = audio_array.mean(axis=1)
        
        audio_array = audio_array.astype(np.float32)
        
        model = self.load_model()
        segments, info = model.transcribe(
            audio_array,
            language=None,
            beam_size=5
        )
        text = "".join([seg.text for seg in segments])
        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability
        }
    
    def unload_model(self):
        if self.model:
            del self.model
            self.model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    
    def get_model_info(self) -> Dict:
        return {
            "model_name": self.model_name,
            "device": self.device,
            "compute_type": self.compute_type
        }
