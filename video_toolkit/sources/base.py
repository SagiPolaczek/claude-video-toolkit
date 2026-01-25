"""Base classes for content sources."""

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, TYPE_CHECKING

from moviepy import VideoFileClip, ImageClip, ColorClip, TextClip, CompositeVideoClip

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


def generate_cache_key(data: dict) -> str:
    """Generate a deterministic cache key from a dictionary."""
    key_string = str(sorted(data.items()))
    return hashlib.sha256(key_string.encode()).hexdigest()[:16]


class ContentSource(ABC):
    """Abstract base class for content sources."""

    @abstractmethod
    def get_clip(self, config: "ProjectConfig") -> Any:
        """Get a MoviePy clip from this source."""
        pass

    @abstractmethod
    def cache_key(self) -> str:
        """Generate a unique cache key for this source."""
        pass


class Asset(ContentSource):
    """Static file asset (video or image)."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def get_clip(self, config: "ProjectConfig") -> Any:
        """Load the file as a MoviePy clip."""
        suffix = self.path.suffix.lower()
        if suffix in (".mp4", ".mov", ".avi", ".mkv", ".webm"):
            return VideoFileClip(str(self.path))
        elif suffix in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
            return ImageClip(str(self.path))
        else:
            return VideoFileClip(str(self.path))

    def cache_key(self) -> str:
        return generate_cache_key({
            "type": "asset",
            "path": str(self.path),
        })

    def __str__(self) -> str:
        return f"Asset({self.path})"

    def __repr__(self) -> str:
        return f"Asset(path={self.path!r})"


class Placeholder(ContentSource):
    """Debug placeholder content."""

    def __init__(
        self,
        text: str,
        duration: float = 3.0,
        color: tuple = (255, 255, 255),  # White background by default
        text_color: tuple = (100, 100, 100),
    ):
        self.text = text
        self.duration = duration
        self.color = color
        self.text_color = text_color

    def get_clip(self, config: "ProjectConfig") -> Any:
        """Create a placeholder clip with text."""
        bg = ColorClip(
            size=config.dimensions,
            color=self.color,
            duration=self.duration,
        )

        txt = TextClip(
            text=self.text,
            font_size=int(48 * config.scale_factor),
            color=f"rgb{self.text_color}",
            font="Arial",
        )
        txt = txt.with_position("center").with_duration(self.duration)
        return CompositeVideoClip([bg, txt])

    def cache_key(self) -> str:
        return generate_cache_key({
            "type": "placeholder",
            "text": self.text,
            "duration": self.duration,
            "color": self.color,
        })

    def __str__(self) -> str:
        return f"Placeholder({self.text!r})"

    def __repr__(self) -> str:
        return f"Placeholder(text={self.text!r}, duration={self.duration})"
