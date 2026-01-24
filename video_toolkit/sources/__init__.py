"""
Content sources for video segments.

Sources represent where video/image content comes from:
- Asset: Static file on disk
- Placeholder: Debug placeholder (colored rectangle with text)
- Generator: Programmatically generated content (Manim, matplotlib, etc.)
"""

from .base import ContentSource, Asset, Placeholder

__all__ = [
    "ContentSource",
    "Asset",
    "Placeholder",
]
