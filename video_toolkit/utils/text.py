"""Text rendering utilities.

This module provides consistent text rendering across the toolkit,
ensuring proper margins to prevent text clipping issues.
"""

from typing import List, Optional, Tuple

from moviepy import TextClip
from PIL import ImageFont


def wrap_text(
    text: str,
    font: str,
    font_size: int,
    max_width: int,
) -> str:
    """
    Wrap text to fit within a maximum width.

    Args:
        text: The text to wrap
        font: Font name
        font_size: Font size in pixels
        max_width: Maximum width in pixels

    Returns:
        Text with newlines inserted for wrapping
    """
    if not text or max_width <= 0:
        return text

    try:
        pil_font = ImageFont.truetype(font, font_size)
    except OSError:
        # Fallback if font not found - use default
        try:
            pil_font = ImageFont.truetype("Arial", font_size)
        except OSError:
            # Can't measure, return original text
            return text

    words = text.split()
    lines: List[str] = []
    current_line: List[str] = []

    for word in words:
        # Try adding word to current line
        test_line = " ".join(current_line + [word])
        bbox = pil_font.getbbox(test_line)
        width = bbox[2] - bbox[0] if bbox else 0

        if width <= max_width:
            current_line.append(word)
        else:
            # Word doesn't fit, start new line
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]

    # Add remaining words
    if current_line:
        lines.append(" ".join(current_line))

    return "\n".join(lines)


def create_text_clip(
    text: str,
    font_size: int,
    color: str,
    font: str = "Arial",
    stroke_color: Optional[str] = None,
    stroke_width: int = 0,
    margin: Tuple[int, int] = (10, 10),
    duration: Optional[float] = None,
    max_width: Optional[int] = None,
    text_align: str = "center",
) -> TextClip:
    """
    Create a TextClip with proper margins to prevent text clipping.

    MoviePy's TextClip can clip text at the edges due to font metrics
    not being fully accounted for. This function ensures consistent
    margins are applied to all text rendering.

    Args:
        text: The text content to render
        font_size: Font size in pixels
        color: Text color as "rgb(r, g, b)" string
        font: Font name (default: Arial)
        stroke_color: Optional stroke color as "rgb(r, g, b)" string
        stroke_width: Stroke width in pixels (default: 0)
        margin: (horizontal, vertical) margin in pixels (default: (10, 10))
        duration: Optional clip duration
        max_width: Optional maximum width for text wrapping
        text_align: Text alignment for multi-line text ("left", "center", "right")

    Returns:
        TextClip with proper margins applied
    """
    # Apply text wrapping if max_width is specified
    if max_width is not None:
        text = wrap_text(text, font, font_size, max_width)

    clip = TextClip(
        font,
        text=text,
        font_size=font_size,
        color=color,
        stroke_color=stroke_color if stroke_width else None,
        stroke_width=stroke_width,
        margin=margin,
        text_align=text_align,
    )

    if duration is not None:
        clip = clip.with_duration(duration)

    return clip


def rgb_to_string(color: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to MoviePy color string."""
    return f"rgb{color}"
