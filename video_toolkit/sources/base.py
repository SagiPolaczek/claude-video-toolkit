"""
Base classes for content sources.
"""

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


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


class ContentSource(ABC):
    """
    Abstract base class for content sources.

    A content source provides video/image content for a segment.
    It can be a static file, a placeholder, or generated content.
    """

    @abstractmethod
    def get_clip(self, config: "ProjectConfig") -> Any:
        """
        Get a MoviePy clip from this source.

        Args:
            config: Project configuration

        Returns:
            MoviePy VideoClip or ImageClip
        """
        pass

    @abstractmethod
    def cache_key(self) -> str:
        """
        Generate a unique cache key for this source.

        Returns:
            16-character hex string identifying this source
        """
        pass


class Asset(ContentSource):
    """
    Static file asset (video or image).

    Represents a file on disk that can be used as content.
    """

    def __init__(self, path: str | Path):
        """
        Create an asset from a file path.

        Args:
            path: Path to the video or image file
        """
        self.path = Path(path)

    def get_clip(self, config: "ProjectConfig") -> Any:
        """Load the file as a MoviePy clip."""
        from moviepy import VideoFileClip, ImageClip

        suffix = self.path.suffix.lower()
        if suffix in (".mp4", ".mov", ".avi", ".mkv", ".webm"):
            return VideoFileClip(str(self.path))
        elif suffix in (".png", ".jpg", ".jpeg", ".gif", ".bmp"):
            return ImageClip(str(self.path))
        else:
            # Try as video by default
            return VideoFileClip(str(self.path))

    def cache_key(self) -> str:
        """Cache key based on file path."""
        return generate_cache_key({
            "type": "asset",
            "path": str(self.path),
        })

    def __str__(self) -> str:
        return f"Asset({self.path})"

    def __repr__(self) -> str:
        return f"Asset(path={self.path!r})"


class Placeholder(ContentSource):
    """
    Debug placeholder content.

    Creates a colored rectangle with text, useful for
    prototyping and testing without real content.
    """

    def __init__(
        self,
        text: str,
        duration: float = 3.0,
        color: tuple = (240, 240, 245),
        text_color: tuple = (100, 100, 100),
    ):
        """
        Create a placeholder.

        Args:
            text: Text to display on the placeholder
            duration: Duration in seconds
            color: Background color as RGB tuple
            text_color: Text color as RGB tuple
        """
        self.text = text
        self.duration = duration
        self.color = color
        self.text_color = text_color

    def get_clip(self, config: "ProjectConfig") -> Any:
        """Create a placeholder clip with text."""
        from moviepy import ColorClip, TextClip, CompositeVideoClip

        # Background
        bg = ColorClip(
            size=config.dimensions,
            color=self.color,
            duration=self.duration,
        )

        # Text
        try:
            txt = TextClip(
                text=self.text,
                font_size=int(48 * config.scale_factor),
                color=f"rgb{self.text_color}",
                font="Arial",
            )
            txt = txt.with_position("center").with_duration(self.duration)
            return CompositeVideoClip([bg, txt])
        except Exception:
            # If text rendering fails, just return the background
            return bg

    def cache_key(self) -> str:
        """Cache key based on text and duration."""
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
