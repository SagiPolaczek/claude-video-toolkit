"""
Composition module for video toolkit.

Handles:
- Applying overlays to video clips
- Synchronizing audio with video
- Concatenating segments into final output
"""

from .audio_sync import AudioSync
from .compositor import Compositor
from .concatenator import FFmpegConcatenator, MoviePyConcatenator

__all__ = [
    "AudioSync",
    "Compositor",
    "FFmpegConcatenator",
    "MoviePyConcatenator",
]
