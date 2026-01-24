"""
Subtitle overlay implementation.
"""

from dataclasses import dataclass
from typing import Any, Dict, Tuple, TYPE_CHECKING

from .base import Overlay

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


@dataclass
class SubtitleOverlay(Overlay):
    """
    Subtitle/narration text overlay.

    Displays text at the bottom of the video,
    typically showing the narration text.
    """

    text: str = ""
    font_size: int = 32  # Base font size at 1080p
    max_width: int = 1600  # Maximum text width at 1080p
    text_color: Tuple[int, int, int] = (255, 255, 255)
    stroke_color: Tuple[int, int, int] = (0, 0, 0)
    stroke_width: int = 2
    margin_bottom: int = 80  # Distance from bottom
    font: str = "Arial"
    background: bool = True
    background_color: Tuple[int, int, int, int] = (0, 0, 0, 180)
    background_padding: int = 10

    def apply(self, clip: Any, config: "ProjectConfig") -> Any:
        """Apply subtitle overlay to clip."""
        from moviepy import CompositeVideoClip, TextClip

        if not self.text:
            return clip

        dims = self.get_scaled_dimensions(config)

        try:
            # Create text clip
            txt = TextClip(
                text=self.text,
                font_size=dims["font_size"],
                color=f"rgb{self.text_color}",
                font=self.font,
                stroke_color=f"rgb{self.stroke_color}" if self.stroke_width else None,
                stroke_width=dims["stroke_width"],
            ).with_duration(clip.duration)

            # Position at bottom center
            x = (config.width - txt.w) // 2
            y = config.height - dims["margin_bottom"] - txt.h

            txt = txt.with_position((x, y))

            return CompositeVideoClip([clip, txt], size=config.dimensions)

        except Exception:
            # Text rendering may fail
            return clip

    def get_scaled_dimensions(self, config: "ProjectConfig") -> Dict[str, int]:
        """Get scaled dimensions for resolution."""
        scale = config.scale_factor
        return {
            "font_size": int(self.font_size * scale),
            "max_width": int(self.max_width * scale),
            "margin_bottom": int(self.margin_bottom * scale),
            "stroke_width": int(self.stroke_width * scale),
            "background_padding": int(self.background_padding * scale),
        }
