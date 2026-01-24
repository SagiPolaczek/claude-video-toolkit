"""
Base class for cache layers.
"""

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


def generate_cache_key(data: dict) -> str:
    """
    Generate a deterministic cache key from a dictionary.

    Args:
        data: Dictionary of values to hash

    Returns:
        16-character hex string
    """
    key_string = str(sorted(data.items()))
    return hashlib.sha256(key_string.encode()).hexdigest()[:16]


class CacheLayer(ABC):
    """
    Abstract base class for cache layers.

    Each cache layer manages a specific type of cached content:
    - Generated content (Layer 0)
    - TTS audio (Layer 1)
    - Video segments (Layer 2)
    - Combined video+audio (Layer 3)
    """

    def __init__(self, base_dir: Path):
        """
        Initialize cache layer.

        Args:
            base_dir: Directory for cached files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def get_path(self, key: str, **kwargs) -> Path:
        """
        Get the cache path for a given key.

        Args:
            key: Cache key
            **kwargs: Additional parameters for path generation

        Returns:
            Path to the cached file
        """
        pass

    def exists(self, key: str, **kwargs) -> bool:
        """
        Check if a cached file exists.

        Args:
            key: Cache key
            **kwargs: Additional parameters

        Returns:
            True if cached file exists
        """
        return self.get_path(key, **kwargs).exists()

    def invalidate(self, key: str, **kwargs) -> bool:
        """
        Invalidate (delete) a cached file.

        Args:
            key: Cache key
            **kwargs: Additional parameters

        Returns:
            True if file was deleted, False if it didn't exist
        """
        path = self.get_path(key, **kwargs)
        if path.exists():
            path.unlink()
            return True
        return False

    def clear(self) -> int:
        """
        Clear all cached files in this layer.

        Returns:
            Number of files deleted
        """
        count = 0
        for file in self.base_dir.glob("*"):
            if file.is_file():
                file.unlink()
                count += 1
        return count
