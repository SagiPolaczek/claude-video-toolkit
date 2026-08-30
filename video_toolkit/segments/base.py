"""
Base class for video segments.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


@dataclass
class Segment(ABC):
    """
    Abstract base class for video segments.

    A segment represents a distinct section of the final video.
    Each segment has:
    - An ID for identification and caching
    - Optional narration text
    - Optional section name (for title bar)
    - Overlay configuration

    Subclasses must implement the render() method.
    """

    id: str
    narration: Optional[str] = None
    section: Optional[str] = None
    duration: Optional[float] = None
    overlays: Optional[Dict[str, bool]] = field(default_factory=dict)

    @abstractmethod
    def render(self, config: "ProjectConfig") -> Any:
        """
        Render this segment to a MoviePy clip.

        Args:
            config: Project configuration

        Returns:
            MoviePy VideoClip
        """
        pass

    def get_effective_overlays(self, defaults: Dict[str, bool]) -> Dict[str, bool]:
        """
        Get effective overlay settings by merging with defaults.

        The merge logic:
        - overlays=None: Disable all overlays (return empty dict)
        - overlays={}: Use all defaults
        - overlays={...}: Override specific settings, inherit rest from defaults

        Args:
            defaults: Project-level default overlay settings

        Returns:
            Dict of overlay name -> enabled status
        """
        if self.overlays is None:
            return {}

        # Merge segment overrides with defaults
        result = dict(defaults)
        result.update(self.overlays)
        return result

    def get_duration(self, config: "ProjectConfig") -> float:
        """
        Get the duration of this segment.

        If duration is explicitly set, return that.
        Otherwise, this should be overridden by subclasses
        to return the actual duration.

        Args:
            config: Project configuration

        Returns:
            Duration in seconds
        """
        if self.duration is not None:
            return self.duration
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_duration() "
            "or have duration set explicitly"
        )
