"""
Title bar overlay implementation.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, TYPE_CHECKING

from .base import Overlay

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


@dataclass
class TitleBarOverlay(Overlay):
    """
    Title/section bar overlay.

    Displays a bar with text at the top or bottom of the video,
    typically showing the current section name.
    """

    text: str = ""
    position: str = "top"  # "top" or "bottom"
    height: int = 60  # Base height at 1080p
    font_size: int = 28  # Base font size at 1080p
    background_color: Tuple[int, int, int, int] = (0, 0, 0, 200)
    text_color: Tuple[int, int, int] = (255, 255, 255)
    padding: int = 20
    font: str = "Arial"

    def apply(self, clip: Any, config: "ProjectConfig") -> Any:
        """Apply title bar overlay to clip."""
        from moviepy import CompositeVideoClip, ColorClip, TextClip

        dims = self.get_scaled_dimensions(config)

        # Create semi-transparent bar
        bar = ColorClip(
            size=(config.width, dims["height"]),
            color=self.background_color[:3],
        ).with_duration(clip.duration)

        # Add transparency if RGBA
        if len(self.background_color) == 4:
            bar = bar.with_opacity(self.background_color[3] / 255)

        # Create text
        try:
            txt = TextClip(
                text=self.text,
                font_size=dims["font_size"],
                color=f"rgb{self.text_color}",
                font=self.font,
            ).with_duration(clip.duration)

            # Position text within bar
            text_y = (dims["height"] - txt.h) // 2
            txt = txt.with_position((dims["padding"], text_y))
        except Exception:
            txt = None

        # Position bar
        if self.position == "top":
            bar_y = 0
        else:
            bar_y = config.height - dims["height"]

        bar = bar.with_position((0, bar_y))

        # Compose
        clips = [clip, bar]
        if txt:
            txt = txt.with_position((dims["padding"], bar_y + text_y))
            clips.append(txt)

        return CompositeVideoClip(clips, size=config.dimensions)

    def get_scaled_dimensions(self, config: "ProjectConfig") -> Dict[str, int]:
        """Get scaled dimensions for resolution."""
        scale = config.scale_factor
        return {
            "height": int(self.height * scale),
            "font_size": int(self.font_size * scale),
            "padding": int(self.padding * scale),
        }
