"""
Style configurations for text, colors, and overlays.
"""

from dataclasses import dataclass, replace
from typing import Tuple, Optional


# Type alias for colors
RGBColor = Tuple[int, int, int]
RGBAColor = Tuple[int, int, int, int]
Color = RGBColor | RGBAColor


@dataclass(frozen=True)
class TextStyle:
    """
    Text rendering style configuration.

    Attributes:
        font: Font name or path
        font_size: Base font size in pixels
        color: Text color as RGB or RGBA tuple
        stroke_color: Optional stroke/outline color
        stroke_width: Stroke width in pixels
        align: Text alignment ('left', 'center', 'right')
    """

    font: str = "Arial"
    font_size: int = 36
    color: Color = (255, 255, 255)
    stroke_color: Optional[Color] = None
    stroke_width: int = 0
    align: str = "center"

    def scale(self, factor: float) -> "TextStyle":
        """
        Return a new TextStyle with scaled font size.

        Args:
            factor: Scale factor (e.g., 2.0 for double size)

        Returns:
            New TextStyle instance with scaled font_size
        """
        return replace(
            self,
            font_size=int(self.font_size * factor),
            stroke_width=int(self.stroke_width * factor) if self.stroke_width else 0,
        )


@dataclass(frozen=True)
class ColorScheme:
    """
    Color scheme for video project.

    Attributes:
        background: Background color
        text: Primary text color
        accent: Accent color for highlights
        subtitle_bg: Subtitle background color (with alpha)
        placeholder: Placeholder content color
    """

    background: Color = (255, 255, 255)
    text: Color = (30, 30, 40)
    accent: Color = (44, 125, 160)
    subtitle_bg: RGBAColor = (0, 0, 0, 180)
    placeholder: Color = (255, 255, 255)  # White by default


@dataclass(frozen=True)
class BarStyle:
    """
    Style for title/section bar overlay.

    Attributes:
        height: Bar height in pixels (at 1080p)
        background: Bar background color
        text_style: Text style for bar content
        padding: Horizontal padding
    """

    height: int = 60
    background: RGBAColor = (0, 0, 0, 200)
    text_style: TextStyle = None
    padding: int = 20

    def __post_init__(self):
        # Set default text style if not provided
        if self.text_style is None:
            object.__setattr__(
                self,
                "text_style",
                TextStyle(font_size=28, color=(255, 255, 255)),
            )

    def scale(self, factor: float) -> "BarStyle":
        """Return a new BarStyle with scaled dimensions."""
        return BarStyle(
            height=int(self.height * factor),
            background=self.background,
            text_style=self.text_style.scale(factor) if self.text_style else None,
            padding=int(self.padding * factor),
        )
