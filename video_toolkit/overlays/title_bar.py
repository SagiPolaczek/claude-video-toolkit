"""Title bar overlay implementation."""

from dataclasses import dataclass
from typing import Any, Dict, Tuple, TYPE_CHECKING

from moviepy import CompositeVideoClip, ColorClip

from .base import Overlay
from video_toolkit.utils import create_text_clip, rgb_to_string

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


@dataclass
class TitleBarOverlay(Overlay):
    """Title/section bar overlay."""

    text: str = ""
    position: str = "top"
    height: int = 50
    font_size: int = 24
    background_color: Tuple[int, int, int, int] = (255, 255, 255, 0)  # Transparent (no bar)
    text_color: Tuple[int, int, int] = (30, 30, 40)  # Dark text
    padding: int = 20
    font: str = "Arial"

    def apply(self, clip: Any, config: "ProjectConfig") -> Any:
        """Apply title bar overlay to clip."""
        dims = self.get_scaled_dimensions(config)

        bar = ColorClip(
            size=(config.width, dims["height"]),
            color=self.background_color[:3],
        ).with_duration(clip.duration)

        if len(self.background_color) == 4:
            bar = bar.with_opacity(self.background_color[3] / 255)

        txt = create_text_clip(
            text=self.text,
            font_size=dims["font_size"],
            color=rgb_to_string(self.text_color),
            font=self.font,
            duration=clip.duration,
        )

        # Position text with proper vertical centering
        if self.position == "top":
            bar_y = 0
            text_y = max(5, (dims["height"] - txt.h) // 2)
        else:
            bar_y = config.height - dims["height"]
            text_y = bar_y + max(5, (dims["height"] - txt.h) // 2)

        bar = bar.with_position((0, bar_y))
        txt = txt.with_position((dims["padding"], text_y))

        return CompositeVideoClip([clip, bar, txt], size=config.dimensions)

    def get_scaled_dimensions(self, config: "ProjectConfig") -> Dict[str, int]:
        """Get scaled dimensions for resolution."""
        scale = config.scale_factor
        return {
            "height": int(self.height * scale),
            "font_size": int(self.font_size * scale),
            "padding": int(self.padding * scale),
        }
