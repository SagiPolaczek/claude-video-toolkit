"""
Resolution presets for video generation.
"""

from enum import Enum
from typing import Tuple


class Resolution(Enum):
    """Video resolution presets."""

    DRAFT = (854, 480)
    HD_1080 = (1920, 1080)
    HD_2K = (2560, 1440)

    def __init__(self, width: int, height: int):
        self._width = width
        self._height = height

    @property
    def width(self) -> int:
        """Width in pixels."""
        return self._width

    @property
    def height(self) -> int:
        """Height in pixels."""
        return self._height

    @property
    def dimensions(self) -> Tuple[int, int]:
        """Return (width, height) tuple."""
        return (self._width, self._height)

    @property
    def scale_factor(self) -> float:
        """Scale factor relative to 1080p baseline."""
        return self._height / 1080

    @classmethod
    def from_string(cls, name: str) -> "Resolution":
        """
        Create Resolution from string name.

        Supported names:
            - 'draft' -> DRAFT
            - 'standard', '1080p' -> HD_1080
            - 'high', '2k' -> HD_2K

        Args:
            name: Resolution name (case-insensitive)

        Returns:
            Resolution enum value

        Raises:
            ValueError: If name is not recognized
        """
        name_lower = name.lower()
        mapping = {
            "draft": cls.DRAFT,
            "standard": cls.HD_1080,
            "1080p": cls.HD_1080,
            "high": cls.HD_2K,
            "2k": cls.HD_2K,
        }

        if name_lower not in mapping:
            valid = ", ".join(mapping.keys())
            raise ValueError(f"Unknown resolution '{name}'. Valid: {valid}")

        return mapping[name_lower]
