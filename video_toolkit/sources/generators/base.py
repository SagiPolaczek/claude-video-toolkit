"""Base class for content generators."""

from abc import abstractmethod
from pathlib import Path
from typing import Any, TYPE_CHECKING

from moviepy import VideoFileClip

from ..base import ContentSource

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


class Generator(ContentSource):
    """Abstract base class for content generators."""

    def __init__(self, key: str, cache_dir: str | Path = "./generated"):
        self.key = key
        self.cache_dir = Path(cache_dir)

    @abstractmethod
    def generate(self, output_path: Path, config: "ProjectConfig") -> Path:
        """Generate content and save to output path."""
        pass

    def get_clip(self, config: "ProjectConfig") -> Any:
        """Get a MoviePy clip, generating if needed."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        cache_path = self.cache_dir / f"{self.cache_key()}.mp4"
        if not cache_path.exists():
            self.generate(cache_path, config)

        return VideoFileClip(str(cache_path))
