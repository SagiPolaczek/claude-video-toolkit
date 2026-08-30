"""
Image segment implementation.
"""

from dataclasses import dataclass
from typing import Any, Optional, Tuple, TYPE_CHECKING

from .base import Segment

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig
    from video_toolkit.sources import ContentSource


@dataclass
class ImageSegment(Segment):
    """
    Static image segment with optional effects.

    Unlike VideoSegment, ImageSegment requires an explicit duration
    since images have no inherent duration.
    """

    source: "ContentSource" = None
    zoom: float = 1.0  # Zoom factor (1.0 = no zoom)
    pan: Optional[str] = None  # "left_to_right", "right_to_left", "top_to_bottom", etc.
    background_color: Tuple[int, int, int] = (255, 255, 255)  # White by default

    def render(self, config: "ProjectConfig") -> Any:
        """
        Render this segment to a MoviePy clip.

        Args:
            config: Project configuration

        Returns:
            MoviePy VideoClip
        """
        if self.source is None:
            raise ValueError(f"ImageSegment {self.id} has no source")

        if self.duration is None:
            raise ValueError(f"ImageSegment {self.id} requires explicit duration")

        # Get image clip from source
        clip = self.source.get_clip(config)

        # Ensure it's an image clip with duration
        clip = clip.with_duration(self.duration)

        # Scale and center on background
        clip = self._scale_and_center(clip, config)

        # Apply effects
        if self.zoom != 1.0 or self.pan is not None:
            clip = self._apply_effects(clip, config)

        return clip

    def _scale_and_center(self, clip: Any, config: "ProjectConfig") -> Any:
        """Scale image proportionally and center on white background."""
        from moviepy import ColorClip, CompositeVideoClip

        target_w, target_h = config.dimensions
        clip_w, clip_h = clip.size

        # Scale to fit while maintaining aspect ratio
        scale_w = target_w / clip_w
        scale_h = target_h / clip_h
        scale = min(scale_w, scale_h)

        if scale != 1.0:
            clip = clip.resized(scale)

        # Get new dimensions after scaling
        new_w, new_h = clip.size

        # Create white background
        bg = ColorClip(
            size=config.dimensions,
            color=self.background_color,
            duration=clip.duration,
        )

        # Center the image on the background
        x = (target_w - new_w) // 2
        y = (target_h - new_h) // 2
        clip = clip.with_position((x, y))

        return CompositeVideoClip([bg, clip], size=config.dimensions)

    def _apply_effects(self, clip: Any, config: "ProjectConfig") -> Any:
        """Apply zoom and pan effects (Ken Burns effect)."""
        # This is a simplified implementation
        # Full Ken Burns would require frame-by-frame transforms

        if self.zoom != 1.0:
            clip = clip.resized(self.zoom)

        # Pan would be implemented with position animation
        # For now, just return the zoomed clip

        return clip

    def get_duration(self, config: "ProjectConfig") -> float:
        """Get explicit duration (required for images)."""
        if self.duration is None:
            raise ValueError(f"ImageSegment {self.id} requires explicit duration")
        return self.duration
