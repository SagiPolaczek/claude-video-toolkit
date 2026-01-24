"""
Base class for overlays.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


@dataclass
class Overlay(ABC):
    """
    Abstract base class for video overlays.

    Overlays are visual elements added on top of video content,
    such as title bars, subtitles, or watermarks.
    """

    @abstractmethod
    def apply(self, clip: Any, config: "ProjectConfig") -> Any:
        """
        Apply this overlay to a video clip.

        Args:
            clip: MoviePy VideoClip
            config: Project configuration

        Returns:
            New VideoClip with overlay applied
        """
        pass

    @abstractmethod
    def get_scaled_dimensions(self, config: "ProjectConfig") -> Dict[str, int]:
        """
        Get overlay dimensions scaled for the given resolution.

        Args:
            config: Project configuration

        Returns:
            Dict with scaled dimension values
        """
        pass
