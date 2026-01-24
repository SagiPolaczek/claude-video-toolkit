"""
Tests for configuration module.
"""

import pytest


class TestResolution:
    """Tests for Resolution enum."""

    def test_resolution_presets_exist(self):
        """Resolution should have standard presets."""
        from video_toolkit.config import Resolution

        assert hasattr(Resolution, "DRAFT")
        assert hasattr(Resolution, "HD_1080")
        assert hasattr(Resolution, "HD_2K")

    def test_resolution_draft_dimensions(self):
        """Draft resolution should be 854x480."""
        from video_toolkit.config import Resolution

        assert Resolution.DRAFT.width == 854
        assert Resolution.DRAFT.height == 480

    def test_resolution_hd_1080_dimensions(self):
        """HD 1080 resolution should be 1920x1080."""
        from video_toolkit.config import Resolution

        assert Resolution.HD_1080.width == 1920
        assert Resolution.HD_1080.height == 1080

    def test_resolution_hd_2k_dimensions(self):
        """HD 2K resolution should be 2560x1440."""
        from video_toolkit.config import Resolution

        assert Resolution.HD_2K.width == 2560
        assert Resolution.HD_2K.height == 1440

    def test_resolution_dimensions_property(self):
        """Resolution should have dimensions property returning (width, height)."""
        from video_toolkit.config import Resolution

        assert Resolution.HD_1080.dimensions == (1920, 1080)
        assert Resolution.DRAFT.dimensions == (854, 480)

    def test_resolution_scale_factor(self):
        """Resolution should calculate scale factor relative to 1080p."""
        from video_toolkit.config import Resolution

        assert Resolution.HD_1080.scale_factor == 1.0
        assert Resolution.DRAFT.scale_factor == pytest.approx(480 / 1080, rel=0.01)
        assert Resolution.HD_2K.scale_factor == pytest.approx(1440 / 1080, rel=0.01)

    def test_resolution_from_string(self):
        """Resolution should be creatable from string names."""
        from video_toolkit.config import Resolution

        assert Resolution.from_string("draft") == Resolution.DRAFT
        assert Resolution.from_string("standard") == Resolution.HD_1080
        assert Resolution.from_string("high") == Resolution.HD_2K
        assert Resolution.from_string("1080p") == Resolution.HD_1080

    def test_resolution_from_string_invalid(self):
        """Invalid resolution string should raise ValueError."""
        from video_toolkit.config import Resolution

        with pytest.raises(ValueError):
            Resolution.from_string("invalid")


class TestProjectConfig:
    """Tests for ProjectConfig dataclass."""

    def test_project_config_defaults(self):
        """ProjectConfig should have sensible defaults."""
        from video_toolkit.config import ProjectConfig

        config = ProjectConfig()
        assert config.fps == 30
        assert config.codec == "libx264"
        assert config.audio_codec == "aac"

    def test_project_config_resolution(self):
        """ProjectConfig should accept resolution."""
        from video_toolkit.config import ProjectConfig, Resolution

        config = ProjectConfig(resolution=Resolution.DRAFT)
        assert config.resolution == Resolution.DRAFT

    def test_project_config_resolution_string(self):
        """ProjectConfig should accept resolution as string."""
        from video_toolkit.config import ProjectConfig, Resolution

        config = ProjectConfig(resolution="draft")
        assert config.resolution == Resolution.DRAFT

    def test_project_config_width_height(self):
        """ProjectConfig should provide width and height properties."""
        from video_toolkit.config import ProjectConfig, Resolution

        config = ProjectConfig(resolution=Resolution.HD_1080)
        assert config.width == 1920
        assert config.height == 1080


class TestTextStyle:
    """Tests for TextStyle configuration."""

    def test_text_style_defaults(self):
        """TextStyle should have default values."""
        from video_toolkit.config import TextStyle

        style = TextStyle()
        assert style.font_size > 0
        assert style.color is not None
        assert style.font is not None

    def test_text_style_scale(self):
        """TextStyle should scale font size by factor."""
        from video_toolkit.config import TextStyle

        style = TextStyle(font_size=36)
        scaled = style.scale(2.0)
        assert scaled.font_size == 72

    def test_text_style_immutable(self):
        """TextStyle.scale should return new instance."""
        from video_toolkit.config import TextStyle

        style = TextStyle(font_size=36)
        scaled = style.scale(2.0)
        assert style.font_size == 36  # Original unchanged
        assert scaled.font_size == 72


class TestColorScheme:
    """Tests for ColorScheme configuration."""

    def test_color_scheme_defaults(self):
        """ColorScheme should have default colors."""
        from video_toolkit.config import ColorScheme

        scheme = ColorScheme()
        assert scheme.background is not None
        assert scheme.text is not None
        assert scheme.accent is not None

    def test_color_scheme_rgb_tuples(self):
        """ColorScheme colors should be RGB tuples."""
        from video_toolkit.config import ColorScheme

        scheme = ColorScheme()
        assert len(scheme.background) >= 3
        assert all(0 <= c <= 255 for c in scheme.background[:3])
