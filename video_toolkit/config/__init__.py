"""
Configuration module for video toolkit.
"""

from .resolution import Resolution
from .project import ProjectConfig
from .styles import TextStyle, ColorScheme, BarStyle

__all__ = [
    "Resolution",
    "ProjectConfig",
    "TextStyle",
    "ColorScheme",
    "BarStyle",
]
