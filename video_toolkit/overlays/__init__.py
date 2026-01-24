"""
Overlay system for video segments.

Overlays add visual elements on top of video content:
- TitleBarOverlay: Section title bar at top/bottom
- SubtitleOverlay: Narration text overlay
- WatermarkOverlay: Watermark/logo overlay
"""

from .base import Overlay
from .title_bar import TitleBarOverlay
from .subtitle import SubtitleOverlay
from .watermark import WatermarkOverlay

__all__ = [
    "Overlay",
    "TitleBarOverlay",
    "SubtitleOverlay",
    "WatermarkOverlay",
]
