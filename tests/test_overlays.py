"""
Tests for overlays module.
"""

import pytest
from pathlib import Path


class TestOverlayBase:
    """Tests for Overlay abstract base class."""

    def test_overlay_is_abstract(self):
        """Overlay should be abstract."""
        from video_toolkit.overlays import Overlay

        with pytest.raises(TypeError):
            Overlay()


class TestTitleBarOverlay:
    """Tests for TitleBarOverlay."""

    def test_title_bar_creation(self):
        """TitleBarOverlay should be creatable with text."""
        from video_toolkit.overlays import TitleBarOverlay

        overlay = TitleBarOverlay(text="Introduction")
        assert overlay.text == "Introduction"

    def test_title_bar_position(self):
        """TitleBarOverlay should have configurable position."""
        from video_toolkit.overlays import TitleBarOverlay

        top = TitleBarOverlay(text="Top", position="top")
        bottom = TitleBarOverlay(text="Bottom", position="bottom")

        assert top.position == "top"
        assert bottom.position == "bottom"

    def test_title_bar_height(self):
        """TitleBarOverlay should have configurable height."""
        from video_toolkit.overlays import TitleBarOverlay

        overlay = TitleBarOverlay(text="Test", height=80)
        assert overlay.height == 80

    def test_title_bar_background_color(self):
        """TitleBarOverlay should have configurable background."""
        from video_toolkit.overlays import TitleBarOverlay

        overlay = TitleBarOverlay(
            text="Test",
            background_color=(50, 50, 50, 200),
        )
        assert overlay.background_color == (50, 50, 50, 200)


class TestSubtitleOverlay:
    """Tests for SubtitleOverlay."""

    def test_subtitle_creation(self):
        """SubtitleOverlay should be creatable with text."""
        from video_toolkit.overlays import SubtitleOverlay

        overlay = SubtitleOverlay(text="Hello world")
        assert overlay.text == "Hello world"

    def test_subtitle_word_wrap(self):
        """SubtitleOverlay should support word wrapping config."""
        from video_toolkit.overlays import SubtitleOverlay

        overlay = SubtitleOverlay(
            text="Long text that might wrap",
            max_width=800,
        )
        assert overlay.max_width == 800

    def test_subtitle_font_size(self):
        """SubtitleOverlay should have configurable font size."""
        from video_toolkit.overlays import SubtitleOverlay

        overlay = SubtitleOverlay(text="Test", font_size=24)
        assert overlay.font_size == 24


class TestWatermarkOverlay:
    """Tests for WatermarkOverlay."""

    def test_watermark_creation(self):
        """WatermarkOverlay should be creatable."""
        from video_toolkit.overlays import WatermarkOverlay

        overlay = WatermarkOverlay(text="DRAFT")
        assert overlay.text == "DRAFT"

    def test_watermark_opacity(self):
        """WatermarkOverlay should support opacity."""
        from video_toolkit.overlays import WatermarkOverlay

        overlay = WatermarkOverlay(text="Test", opacity=0.5)
        assert overlay.opacity == 0.5

    def test_watermark_position(self):
        """WatermarkOverlay should support corner positions."""
        from video_toolkit.overlays import WatermarkOverlay

        overlay = WatermarkOverlay(text="Test", position="bottom_right")
        assert overlay.position == "bottom_right"


class TestOverlayScaling:
    """Tests for overlay scaling with resolution."""

    def test_title_bar_scales_with_resolution(self):
        """TitleBarOverlay should scale font with resolution."""
        from video_toolkit.overlays import TitleBarOverlay
        from video_toolkit.config import ProjectConfig, Resolution

        overlay = TitleBarOverlay(text="Test", height=60, font_size=28)

        # Get scaled dimensions for different resolutions
        config_1080 = ProjectConfig(resolution=Resolution.HD_1080)
        config_draft = ProjectConfig(resolution=Resolution.DRAFT)

        scaled_1080 = overlay.get_scaled_dimensions(config_1080)
        scaled_draft = overlay.get_scaled_dimensions(config_draft)

        assert scaled_1080["height"] > scaled_draft["height"]
        assert scaled_1080["font_size"] > scaled_draft["font_size"]
