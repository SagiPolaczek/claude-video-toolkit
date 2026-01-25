"""Watermark overlay implementation."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union, TYPE_CHECKING

from moviepy import CompositeVideoClip, TextClip, ImageClip

from .base import Overlay

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


@dataclass
class WatermarkOverlay(Overlay):
    """Watermark/logo overlay."""

    text: Optional[str] = None
    image_path: Optional[Union[str, Path]] = None
    position: str = "bottom_right"
    opacity: float = 0.5
    font_size: int = 24
    text_color: Tuple[int, int, int] = (255, 255, 255)
    margin: int = 20
    font: str = "Arial"

    def apply(self, clip: Any, config: "ProjectConfig") -> Any:
        """Apply watermark overlay to clip."""
        dims = self.get_scaled_dimensions(config)

        if self.text:
            watermark = TextClip(
                text=self.text,
                font_size=dims["font_size"],
                color=f"rgb{self.text_color}",
                font=self.font,
            ).with_duration(clip.duration).with_opacity(self.opacity)

        elif self.image_path:
            image_path = Path(self.image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Watermark image not found: {image_path}")
            watermark = ImageClip(str(image_path))
            watermark = watermark.with_duration(clip.duration)
            watermark = watermark.with_opacity(self.opacity)

        else:
            return clip

        x, y = self._calculate_position(
            watermark.size,
            config.dimensions,
            dims["margin"],
        )

        watermark = watermark.with_position((x, y))

        return CompositeVideoClip([clip, watermark], size=config.dimensions)

    def _calculate_position(
        self,
        watermark_size: Tuple[int, int],
        video_size: Tuple[int, int],
        margin: int,
    ) -> Tuple[int, int]:
        """Calculate watermark position based on position setting."""
        wm_w, wm_h = watermark_size
        vid_w, vid_h = video_size

        positions = {
            "top_left": (margin, margin),
            "top_right": (vid_w - wm_w - margin, margin),
            "bottom_left": (margin, vid_h - wm_h - margin),
            "bottom_right": (vid_w - wm_w - margin, vid_h - wm_h - margin),
        }

        return positions.get(self.position, positions["bottom_right"])

    def get_scaled_dimensions(self, config: "ProjectConfig") -> Dict[str, int]:
        """Get scaled dimensions for resolution."""
        scale = config.scale_factor
        return {
            "font_size": int(self.font_size * scale),
            "margin": int(self.margin * scale),
        }
