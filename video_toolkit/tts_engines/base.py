"""
Abstract base class for TTS engines.
"""

import hashlib
import os
from abc import ABC, abstractmethod
from pathlib import Path


class TTSEngine(ABC):
    """Abstract base class for text-to-speech engines."""

    def __init__(self, cache_dir: str = "./tts_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def synthesize(self, text: str, output_path: str) -> str:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            output_path: Path to save audio file

        Returns:
            Path to the generated audio file
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Return the engine name for cache keys."""
        pass

    @abstractmethod
    def get_voice(self) -> str:
        """Return the current voice identifier."""
        pass

    def get_cache_params(self) -> dict:
        """
        Return additional parameters for cache key generation.
        Override in subclasses for engine-specific params.
        """
        return {}

    def get_cache_key(self, text: str) -> str:
        """Generate a unique cache key for the given text."""
        params = {
            "text": text,
            "engine": self.get_name(),
            "voice": self.get_voice(),
            **self.get_cache_params()
        }
        key_string = str(sorted(params.items()))
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]

    def get_cached_path(self, cache_key: str) -> Path:
        """Get the path for a cached audio file."""
        return self.cache_dir / f"{cache_key}.wav"

    def is_cached(self, text: str) -> bool:
        """Check if audio for this text is already cached."""
        cache_key = self.get_cache_key(text)
        return self.get_cached_path(cache_key).exists()

    def synthesize_cached(self, text: str) -> str:
        """
        Synthesize with caching.

        Returns cached audio if available, otherwise synthesizes and caches.

        Args:
            text: Text to synthesize

        Returns:
            Path to the audio file (cached or newly generated)
        """
        cache_key = self.get_cache_key(text)
        cached_path = self.get_cached_path(cache_key)

        if cached_path.exists():
            print(f"  [Cache HIT] {cache_key}")
            return str(cached_path)

        print(f"  [Cache MISS] {cache_key} - synthesizing...")

        # Synthesize to temporary path first
        temp_path = self.cache_dir / f"_temp_{cache_key}.wav"
        self.synthesize(text, str(temp_path))

        # Move to final cached location
        temp_path.rename(cached_path)

        return str(cached_path)


class DummyTTSEngine(TTSEngine):
    """Dummy TTS engine for testing (produces no audio)."""

    def synthesize(self, text: str, output_path: str) -> str:
        # Create empty WAV file
        import wave
        with wave.open(output_path, 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(22050)
            f.writeframes(b'')
        return output_path

    def get_name(self) -> str:
        return "dummy"

    def get_voice(self) -> str:
        return "none"
