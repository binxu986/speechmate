"""
SpeechMate Audio Recorder Module
"""
import queue
import threading
import tempfile
import wave
from pathlib import Path
from typing import Optional, Callable

import numpy as np
import sounddevice as sd
from loguru import logger


class AudioRecorder:
    """Audio recorder using sounddevice"""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        dtype: str = "float32"
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype

        self._is_recording = False
        self._audio_queue = queue.Queue()
        self._recording_thread: Optional[threading.Thread] = None
        self._stream: Optional[sd.InputStream] = None

        # Callback when recording state changes
        self._on_state_change: Optional[Callable[[bool], None]] = None

    def set_state_callback(self, callback: Callable[[bool], None]):
        """Set callback for recording state changes"""
        self._on_state_change = callback

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            logger.warning(f"Audio status: {status}")
        if self._is_recording:
            self._audio_queue.put(indata.copy())

    def start_recording(self):
        """Start recording audio"""
        if self._is_recording:
            logger.warning("Already recording")
            return

        logger.info("Starting recording...")
        self._is_recording = True
        self._audio_queue = queue.Queue()

        try:
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=self.dtype,
                callback=self._audio_callback
            )
            self._stream.start()

            if self._on_state_change:
                self._on_state_change(True)

        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            self._is_recording = False
            raise

    def stop_recording(self) -> Optional[str]:
        """Stop recording and save to temporary file"""
        if not self._is_recording:
            logger.warning("Not recording")
            return None

        logger.info("Stopping recording...")
        self._is_recording = False

        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        if self._on_state_change:
            self._on_state_change(False)

        # Collect recorded audio
        frames = []
        while not self._audio_queue.empty():
            try:
                frames.append(self._audio_queue.get_nowait())
            except queue.Empty:
                break

        if not frames:
            logger.warning("No audio recorded")
            return None

        # Concatenate frames
        audio_data = np.concatenate(frames, axis=0)

        # Check if audio is too short (less than 0.3 seconds)
        duration = len(audio_data) / self.sample_rate
        if duration < 0.3:
            logger.warning(f"Audio too short: {duration:.2f}s")
            return None

        # Save to temporary WAV file
        try:
            temp_file = tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            )
            temp_path = temp_file.name
            temp_file.close()

            # Write WAV file
            with wave.open(temp_path, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)

                # Convert float32 to int16
                audio_int16 = (audio_data * 32767).astype(np.int16)
                wf.writeframes(audio_int16.tobytes())

            logger.info(f"Audio saved to {temp_path} ({duration:.2f}s)")
            return temp_path

        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            return None

    @property
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self._is_recording

    def get_input_devices(self) -> list:
        """Get list of available input devices"""
        devices = []
        for i, dev in enumerate(sd.query_devices()):
            if dev["max_input_channels"] > 0:
                devices.append({
                    "id": i,
                    "name": dev["name"],
                    "channels": dev["max_input_channels"],
                    "default": dev.get("default_input", False)
                })
        return devices


# Global recorder instance
recorder = AudioRecorder()
