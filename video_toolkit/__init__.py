"""
Video Toolkit - A modular video generation framework.

This toolkit provides a clean API for creating narrated presentation videos
with support for static assets and programmatically generated content.
"""

from .config import Resolution, ProjectConfig
from .project import VideoProject

__version__ = "0.1.0"

__all__ = [
    "VideoProject",
    "Resolution",
    "ProjectConfig",
    "__version__",
]
