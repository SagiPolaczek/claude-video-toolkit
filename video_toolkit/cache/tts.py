"""
TTS audio cache (Layer 1).
"""

from pathlib import Path

from .base import CacheLayer, generate_cache_key


class TTSCache(CacheLayer):
    """
    Cache for TTS (text-to-speech) audio files.

    This is Layer 1 of the cache system. It stores synthesized
    audio from TTS engines.

    Cache key is based on:
    - Narration text
    - TTS engine name
    - Voice identifier
    """

    def __init__(self, base_dir: Path = Path("./tts_cache")):
        super().__init__(base_dir)

    def generate_key(self, text: str, engine: str, voice: str, **kwargs) -> str:
        """
        Generate cache key for TTS audio.

        Args:
            text: Narration text
            engine: TTS engine name
            voice: Voice identifier

        Returns:
            16-character hex key
        """
        return generate_cache_key({
            "text": text,
            "engine": engine,
            "voice": voice,
            **kwargs,
        })

    def get_path(self, key: str, extension: str = ".wav", **kwargs) -> Path:
        """
        Get cache path for TTS audio.

        Args:
            key: TTS cache key
            extension: File extension (default: .wav)

        Returns:
            Path to cached audio file
        """
        return self.base_dir / f"{key}{extension}"
