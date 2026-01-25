"""Subtitle overlay implementation."""

from dataclasses import dataclass
from typing import Any, Dict, Tuple, TYPE_CHECKING

from moviepy import CompositeVideoClip

from .base import Overlay
from video_toolkit.utils import create_text_clip, rgb_to_string

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


@dataclass
class SubtitleOverlay(Overlay):
    """Subtitle/narration text overlay."""

    text: str = ""
    font_size: int = 28
    max_width: int = 1600
    text_color: Tuple[int, int, int] = (30, 30, 40)  # Dark text for white backgrounds
    stroke_color: Tuple[int, int, int] = (0, 0, 0)
    stroke_width: int = 0  # No stroke by default for cleaner look
    margin_bottom: int = 50
    font: str = "Arial"
    background: bool = False  # No background by default
    background_color: Tuple[int, int, int, int] = (255, 255, 255, 200)
    background_padding: int = 10

    def apply(self, clip: Any, config: "ProjectConfig") -> Any:
        """Apply subtitle overlay to clip."""
        if not self.text:
            return clip

        dims = self.get_scaled_dimensions(config)

        txt = create_text_clip(
            text=self.text,
            font_size=dims["font_size"],
            color=rgb_to_string(self.text_color),
            font=self.font,
            stroke_color=rgb_to_string(self.stroke_color) if self.stroke_width else None,
            stroke_width=dims["stroke_width"],
            duration=clip.duration,
            max_width=dims["max_width"],
            text_align="center",
        )

        x = (config.width - txt.w) // 2
        y = config.height - dims["margin_bottom"] - txt.h

        txt = txt.with_position((x, y))

        return CompositeVideoClip([clip, txt], size=config.dimensions)

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
