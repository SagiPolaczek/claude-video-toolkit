"""
Video Toolkit - A modular video generation framework.

This toolkit provides a clean API for creating narrated presentation videos
with support for static assets and programmatically generated content.
"""

from .config import Resolution, ProjectConfig
from .project import VideoProject
from .validation import MediaValidationError, MediaValidationReport, validate_media

__version__ = "0.2.0"

__all__ = [
    "VideoProject",
    "Resolution",
    "ProjectConfig",
    "MediaValidationError",
    "MediaValidationReport",
    "validate_media",
    "__version__",
]
