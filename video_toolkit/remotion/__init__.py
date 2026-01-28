"""Remotion rendering backend for video_toolkit.

Provides React-based video rendering via Remotion, enabling rich animations,
web-quality typography, and custom React compositions. Rendered segments
are MP4 files that flow through the existing MoviePy pipeline unchanged.
"""

from .config import RemotionConfig
from .exceptions import RemotionError, BundleError, RenderError, DependencyError
from .renderer import RemotionRenderer
from .segments import (
    RemotionSegment,
    RemotionTitleSegment,
    RemotionImageSegment,
    RemotionKenBurnsSegment,
    RemotionSplitScreenSegment,
    RemotionCarouselSegment,
)
from .transitions import RemotionTransition
from .generator import RemotionGenerator

__all__ = [
    "RemotionConfig",
    "RemotionError",
    "BundleError",
    "RenderError",
    "DependencyError",
    "RemotionRenderer",
    "RemotionSegment",
    "RemotionTitleSegment",
    "RemotionImageSegment",
    "RemotionKenBurnsSegment",
    "RemotionSplitScreenSegment",
    "RemotionCarouselSegment",
    "RemotionTransition",
    "RemotionGenerator",
]
