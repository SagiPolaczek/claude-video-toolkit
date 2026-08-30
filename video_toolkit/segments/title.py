"""
Title segment implementation.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Tuple, TYPE_CHECKING

from .base import Segment
from video_toolkit.utils import create_text_clip, rgb_to_string

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


@dataclass
class TitleSegment(Segment):
    """
    Title card segment with text.

    Creates a simple title card with optional subtitle.
    No external source is required.
    """

    title: str = ""
    subtitle: Optional[str] = None
    background_color: Tuple[int, int, int] = (255, 255, 255)
    title_color: Tuple[int, int, int] = (30, 30, 40)
    subtitle_color: Tuple[int, int, int] = (100, 100, 100)
    title_font: str = "Arial"
    subtitle_font: str = "Arial"
    # Override default overlays to None (title cards typically have no overlays)
    overlays: Optional[dict] = None

    def render(self, config: "ProjectConfig") -> Any:
        """
        Render this segment to a MoviePy clip.

        Args:
            config: Project configuration

        Returns:
            MoviePy VideoClip
        """
        from moviepy import ColorClip, CompositeVideoClip

        if self.duration is None:
            raise ValueError(f"TitleSegment {self.id} requires explicit duration")

        # Background
        bg = ColorClip(
            size=config.dimensions,
            color=self.background_color,
            duration=self.duration,
        )

        clips = [bg]

        # Title text
        title_size = int(64 * config.scale_factor)
        try:
            title_clip = create_text_clip(
                text=self.title,
                font_size=title_size,
                color=rgb_to_string(self.title_color),
                font=self.title_font,
            )

            # Position title (center, slightly above middle if subtitle exists)
            title_x = (config.width - title_clip.w) // 2
            if self.subtitle:
                title_y = int(config.height * 0.4) - title_clip.h // 2
            else:
                title_y = (config.height - title_clip.h) // 2

            title_clip = title_clip.with_position((title_x, title_y)).with_duration(self.duration)
            clips.append(title_clip)
        except Exception as e:
            print(f"Warning: Title text rendering failed: {e}")
            pass

        # Subtitle text
        if self.subtitle:
            subtitle_size = int(36 * config.scale_factor)
            try:
                subtitle_clip = create_text_clip(
                    text=self.subtitle,
                    font_size=subtitle_size,
                    color=rgb_to_string(self.subtitle_color),
                    font=self.subtitle_font,
                )
                subtitle_x = (config.width - subtitle_clip.w) // 2
                subtitle_y = int(config.height * 0.55)
                subtitle_clip = subtitle_clip.with_position(
                    (subtitle_x, subtitle_y)
                ).with_duration(self.duration)
                clips.append(subtitle_clip)
            except Exception as e:
                print(f"Warning: Subtitle text rendering failed: {e}")
                pass

        return CompositeVideoClip(clips, size=config.dimensions)

    def get_duration(self, config: "ProjectConfig") -> float:
        """Get explicit duration (required for title cards)."""
        if self.duration is None:
            raise ValueError(f"TitleSegment {self.id} requires explicit duration")
        return self.duration
