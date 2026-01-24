"""
Generated content cache (Layer 0).
"""

from pathlib import Path

from .base import CacheLayer


class GeneratedCache(CacheLayer):
    """
    Cache for generated content from Generators.

    This is Layer 0 of the cache system. It stores output from
    FunctionGenerator, ScriptGenerator, and other generator types.

    Cache key is based on:
    - Generator key (version identifier)
    - Generator kwargs (parameters)
    """

    def __init__(self, base_dir: Path = Path("./generated")):
        super().__init__(base_dir)

    def get_path(self, key: str, extension: str = ".mp4", **kwargs) -> Path:
        """
        Get cache path for generated content.

        Args:
            key: Generator cache key
            extension: File extension (default: .mp4)

        Returns:
            Path to cached file
        """
        return self.base_dir / f"{key}{extension}"
