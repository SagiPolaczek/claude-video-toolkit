"""
Base class for content generators.
"""

from abc import abstractmethod
from pathlib import Path
from typing import Any, TYPE_CHECKING

from ..base import ContentSource, generate_cache_key

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


class Generator(ContentSource):
    """
    Abstract base class for content generators.

    Generators produce video content programmatically
    (e.g., Manim animations, matplotlib charts, etc.)

    The generated content is cached based on the cache key,
    which should include all parameters that affect the output.
    """

    def __init__(self, key: str, cache_dir: str | Path = "./generated"):
        """
        Initialize generator.

        Args:
            key: Unique key for this generator configuration
            cache_dir: Directory for caching generated content
        """
        self.key = key
        self.cache_dir = Path(cache_dir)

    @abstractmethod
    def generate(self, output_path: Path, config: "ProjectConfig") -> Path:
        """
        Generate content and save to output path.

        Args:
            output_path: Path to save the generated video/image
            config: Project configuration

        Returns:
            Path to the generated file
        """
        pass

    def get_clip(self, config: "ProjectConfig") -> Any:
        """
        Get a MoviePy clip, generating if needed.

        This handles caching: if the content is already generated
        and cached, it loads from cache. Otherwise, it generates
        the content first.

        Args:
            config: Project configuration

        Returns:
            MoviePy VideoClip
        """
        from moviepy import VideoFileClip

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Check cache
        cache_path = self.cache_dir / f"{self.cache_key()}.mp4"
        if not cache_path.exists():
            self.generate(cache_path, config)

        return VideoFileClip(str(cache_path))
