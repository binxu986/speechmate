"""
SpeechMate API Client Module
"""
import os
import time
from typing import Optional, Tuple
from pathlib import Path

import requests
from loguru import logger


class APIClient:
    """Client for SpeechMate API"""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = 60  # seconds

    def set_base_url(self, base_url: str):
        """Set API base URL"""
        self.base_url = base_url.rstrip("/")

    def set_api_key(self, api_key: str):
        """Set API key"""
        self.api_key = api_key

    def _get_headers(self) -> dict:
        """Get request headers"""
        return {
            "X-API-Key": self.api_key,
            "Accept": "application/json"
        }

    def health_check(self) -> bool:
        """Check if server is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_server_info(self) -> Optional[dict]:
        """Get server information"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/info",
                headers=self._get_headers(),
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get server info: {e}")
            return None

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Tuple[bool, str, str]:
        """
        Transcribe audio file to text

        Args:
            audio_path: Path to audio file
            language: Language code (zh, en, or None for auto-detect)

        Returns:
            Tuple of (success, text, error_message)
        """
        try:
            with open(audio_path, "rb") as audio_file:
                files = {"audio": (os.path.basename(audio_path), audio_file, "audio/wav")}
                data = {}

                if language:
                    data["language"] = language

                response = requests.post(
                    f"{self.base_url}/api/v1/transcribe",
                    headers={"X-API-Key": self.api_key},
                    files=files,
                    data=data,
                    timeout=self.timeout
                )

            result = response.json()

            if response.status_code == 200 and result.get("success"):
                return True, result.get("text", ""), ""
            else:
                error = result.get("error", f"HTTP {response.status_code}")
                return False, "", error

        except requests.exceptions.Timeout:
            return False, "", "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, "", "Connection error - check server URL"
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return False, "", str(e)

    def translate(
        self,
        audio_path: str,
        source_lang: str = "zh",
        target_lang: str = "en"
    ) -> Tuple[bool, str, str, str]:
        """
        Translate audio file to target language

        Args:
            audio_path: Path to audio file
            source_lang: Source language (zh or en)
            target_lang: Target language (zh or en)

        Returns:
            Tuple of (success, original_text, translated_text, error_message)
        """
        try:
            with open(audio_path, "rb") as audio_file:
                files = {"audio": (os.path.basename(audio_path), audio_file, "audio/wav")}
                data = {
                    "source_lang": source_lang,
                    "target_lang": target_lang
                }

                response = requests.post(
                    f"{self.base_url}/api/v1/translate",
                    headers={"X-API-Key": self.api_key},
                    files=files,
                    data=data,
                    timeout=self.timeout
                )

            result = response.json()

            if response.status_code == 200 and result.get("success"):
                return (
                    True,
                    result.get("original_text", ""),
                    result.get("translated_text", ""),
                    ""
                )
            else:
                error = result.get("error", f"HTTP {response.status_code}")
                return False, "", "", error

        except requests.exceptions.Timeout:
            return False, "", "", "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, "", "", "Connection error - check server URL"
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return False, "", "", str(e)


# Global API client instance
api_client = APIClient()
