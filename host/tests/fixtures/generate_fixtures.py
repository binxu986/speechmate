#!/usr/bin/env python3
"""
Generate test audio fixtures for SpeechMate tests.

Run this script to create test audio files:
    python generate_fixtures.py
"""
import os
import wave
import struct
import math
from pathlib import Path


def generate_sine_wave(
    output_path: str,
    duration: float = 3.0,
    frequency: float = 440.0,
    sample_rate: int = 16000,
    amplitude: float = 0.5
):
    """
    Generate a sine wave audio file.

    Args:
        output_path: Output file path
        duration: Duration in seconds
        frequency: Frequency in Hz
        sample_rate: Sample rate (default 16kHz for speech)
        amplitude: Amplitude (0.0 to 1.0)
    """
    n_samples = int(duration * sample_rate)
    n_channels = 1  # Mono
    sample_width = 2  # 16-bit

    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)

        for i in range(n_samples):
            t = i / sample_rate
            value = amplitude * math.sin(2 * math.pi * frequency * t)
            # Convert to 16-bit integer
            sample = int(value * 32767)
            # Clamp to valid range
            sample = max(-32768, min(32767, sample))
            wav_file.writeframes(struct.pack('<h', sample))

    print(f"Generated: {output_path} ({duration}s, {frequency}Hz)")


def generate_silence(
    output_path: str,
    duration: float = 2.0,
    sample_rate: int = 16000
):
    """
    Generate a silent audio file.

    Args:
        output_path: Output file path
        duration: Duration in seconds
        sample_rate: Sample rate
    """
    n_samples = int(duration * sample_rate)
    n_channels = 1
    sample_width = 2

    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)

        for _ in range(n_samples):
            wav_file.writeframes(struct.pack('<h', 0))

    print(f"Generated: {output_path} (silence, {duration}s)")


def generate_multi_tone(
    output_path: str,
    duration: float = 3.0,
    frequencies: list = None,
    sample_rate: int = 16000,
    amplitude: float = 0.3
):
    """
    Generate audio with multiple frequencies (simulates speech-like pattern).

    Args:
        output_path: Output file path
        duration: Duration in seconds
        frequencies: List of frequencies to mix
        sample_rate: Sample rate
        amplitude: Amplitude per frequency
    """
    if frequencies is None:
        frequencies = [300, 500, 800, 1200]  # Speech-like frequencies

    n_samples = int(duration * sample_rate)
    n_channels = 1
    sample_width = 2

    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(n_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)

        for i in range(n_samples):
            t = i / sample_rate
            value = 0
            for freq in frequencies:
                # Add time-varying amplitude for more speech-like pattern
                envelope = math.sin(math.pi * t / duration)
                value += amplitude * envelope * math.sin(2 * math.pi * freq * t)

            value /= len(frequencies)
            sample = int(value * 32767)
            sample = max(-32768, min(32767, sample))
            wav_file.writeframes(struct.pack('<h', sample))

    print(f"Generated: {output_path} (multi-tone, {duration}s)")


def main():
    """Generate all test audio fixtures."""
    fixtures_dir = Path(__file__).parent
    fixtures_dir.mkdir(parents=True, exist_ok=True)

    print("Generating test audio fixtures...")
    print(f"Output directory: {fixtures_dir}")
    print("-" * 50)

    # Standard test audio (3 seconds, 440Hz)
    generate_sine_wave(
        str(fixtures_dir / "test_audio.wav"),
        duration=3.0,
        frequency=440.0
    )

    # Chinese-like audio (lower frequencies)
    generate_multi_tone(
        str(fixtures_dir / "test_audio_zh.wav"),
        duration=3.0,
        frequencies=[200, 400, 600, 800]
    )

    # Short audio (boundary test)
    generate_sine_wave(
        str(fixtures_dir / "test_audio_short.wav"),
        duration=0.5,
        frequency=440.0
    )

    # Silent audio (boundary test)
    generate_silence(
        str(fixtures_dir / "test_audio_silent.wav"),
        duration=2.0
    )

    # Long audio for stress test
    generate_sine_wave(
        str(fixtures_dir / "test_audio_long.wav"),
        duration=10.0,
        frequency=440.0
    )

    print("-" * 50)
    print("All test fixtures generated successfully!")

    # List generated files
    print("\nGenerated files:")
    for f in fixtures_dir.glob("*.wav"):
        size = f.stat().st_size
        print(f"  {f.name}: {size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
