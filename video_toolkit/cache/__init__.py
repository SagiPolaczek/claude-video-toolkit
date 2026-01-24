"""
Cache system for video toolkit.

Four-layer caching:
- Layer 0 (GeneratedCache): Generated content from Generators
- Layer 1 (TTSCache): TTS audio files
- Layer 2 (SegmentCache): Rendered segments (video only)
- Layer 3 (CombinedCache): Segments with audio
"""

from .base import CacheLayer
from .generated import GeneratedCache
from .tts import TTSCache
from .segments import SegmentCache
from .combined import CombinedCache
from .manager import CacheManager

__all__ = [
    "CacheLayer",
    "GeneratedCache",
    "TTSCache",
    "SegmentCache",
    "CombinedCache",
    "CacheManager",
]
