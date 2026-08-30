"""
Video segments module.

Segments represent individual parts of a video:
- VideoSegment: Video clip with optional narration
- ImageSegment: Static image with optional effects
- TitleSegment: Title card with text
- GridSegment: Multi-source grid layout
"""

from .base import Segment
from .video import VideoSegment
from .image import ImageSegment
from .title import TitleSegment
from .grid import GridSegment, GridCell, GridLayout

__all__ = [
    "Segment",
    "VideoSegment",
    "ImageSegment",
    "TitleSegment",
    "GridSegment",
    "GridCell",
    "GridLayout",
]
