"""
Compositor for applying overlays to video clips.
"""

from dataclasses import dataclass, field
from typing import Any, List, TYPE_CHECKING

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig
    from video_toolkit.overlays import Overlay


@dataclass
class Compositor:
    """
    Applies overlays to video clips.

    The compositor manages a list of overlays and applies
    them in order to video clips.
    """

    overlays: List["Overlay"] = field(default_factory=list)

    def compose(
        self,
        clip: Any,
        config: "ProjectConfig",
    ) -> Any:
        """
        Apply all overlays to a clip.

        Args:
            clip: MoviePy VideoClip
            config: Project configuration

        Returns:
            VideoClip with overlays applied
        """
        result = clip

        for overlay in self.overlays:
            result = overlay.apply(result, config)

        return result

    def add_overlay(self, overlay: "Overlay") -> None:
        """Add an overlay to the compositor."""
        self.overlays.append(overlay)

    def clear_overlays(self) -> None:
        """Remove all overlays."""
        self.overlays.clear()
