"""
Project-level configuration.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, Optional

from .resolution import Resolution


@dataclass
class ProjectConfig:
    """
    Configuration for a video project.

    Attributes:
        resolution: Video resolution (enum or string like 'draft', 'standard', 'high')
        fps: Frames per second (default: 30)
        codec: Video codec (default: libx264)
        audio_codec: Audio codec (default: aac)
        preset: Encoding preset (default: medium)
        output_dir: Directory for output files
        cache_dir: Directory for cache files
    """

    resolution: Union[Resolution, str] = Resolution.HD_1080
    fps: int = 30
    codec: str = "libx264"
    audio_codec: str = "aac"
    preset: str = "medium"
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    cache_dir: Path = field(default_factory=lambda: Path("./cache"))

    def __post_init__(self):
        """Convert string resolution to enum."""
        if isinstance(self.resolution, str):
            self.resolution = Resolution.from_string(self.resolution)

        # Ensure paths are Path objects
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)
        if isinstance(self.cache_dir, str):
            self.cache_dir = Path(self.cache_dir)

    @property
    def width(self) -> int:
        """Video width in pixels."""
        return self.resolution.width

    @property
    def height(self) -> int:
        """Video height in pixels."""
        return self.resolution.height

    @property
    def dimensions(self) -> tuple:
        """Video dimensions as (width, height)."""
        return self.resolution.dimensions

    @property
    def scale_factor(self) -> float:
        """Scale factor relative to 1080p."""
        return self.resolution.scale_factor
