"""
Tests for video_toolkit.utils module.
"""

import pytest

from video_toolkit.utils import wrap_text, create_text_clip, rgb_to_string


class TestWrapText:
    """Tests for the wrap_text function."""

    def test_short_text_no_wrap(self):
        """Short text that fits within max_width should not be wrapped."""
        text = "Hello world"
        result = wrap_text(text, "Arial", 28, 1600)
        assert result == "Hello world"
        assert "\n" not in result

    def test_long_text_wraps(self):
        """Long text that exceeds max_width should be wrapped to multiple lines."""
        text = "This is a very long sentence that should definitely wrap to multiple lines when rendered at this font size."
        result = wrap_text(text, "Arial", 28, 400)
        assert "\n" in result
        lines = result.split("\n")
        assert len(lines) > 1

    def test_empty_text(self):
        """Empty text should return empty string."""
        result = wrap_text("", "Arial", 28, 1600)
        assert result == ""

    def test_zero_max_width_returns_original(self):
        """Zero max_width should return original text."""
        text = "Hello world"
        result = wrap_text(text, "Arial", 28, 0)
        assert result == text

    def test_negative_max_width_returns_original(self):
        """Negative max_width should return original text."""
        text = "Hello world"
        result = wrap_text(text, "Arial", 28, -100)
        assert result == text

    def test_single_word_longer_than_max_width(self):
        """Single word longer than max_width should still appear (not truncated)."""
        text = "Supercalifragilisticexpialidocious"
        result = wrap_text(text, "Arial", 28, 50)
        # Word should still be present even if it exceeds max_width
        assert "Supercalifragilisticexpialidocious" in result

    def test_preserves_word_boundaries(self):
        """Text should wrap at word boundaries, not mid-word."""
        text = "Hello beautiful world"
        result = wrap_text(text, "Arial", 28, 200)
        # Should not split words
        lines = result.split("\n")
        for line in lines:
            words = line.split()
            for word in words:
                assert word in ["Hello", "beautiful", "world"]

    def test_multiple_spaces_handled(self):
        """Multiple spaces between words should be normalized."""
        text = "Hello    world"
        result = wrap_text(text, "Arial", 28, 1600)
        # Should work without error
        assert "Hello" in result
        assert "world" in result

    def test_font_fallback(self):
        """Invalid font should fallback and still produce output."""
        text = "Hello world"
        # Using invalid font name
        result = wrap_text(text, "NonExistentFont123", 28, 1600)
        # Should still return text (fallback to Arial or original)
        assert "Hello" in result
        assert "world" in result

    def test_narrow_width_wraps_each_word(self):
        """Very narrow width should wrap almost every word to its own line."""
        text = "One two three four"
        result = wrap_text(text, "Arial", 28, 100)
        lines = result.split("\n")
        # With very narrow width, should have multiple lines
        assert len(lines) >= 2

    def test_realistic_subtitle_scenario(self):
        """Test a realistic subtitle scenario with typical dimensions."""
        text = "We encode the entire scene into a small MLP network, inspired by NeRF. The network is optimized using Score Distillation Sampling, and dropout regularization encourages an ordered, layered structure."
        result = wrap_text(text, "Arial", 28, 1600)
        # Should wrap into 2 lines
        lines = result.split("\n")
        assert len(lines) == 2
        # First line should be the longer one
        assert len(lines[0]) > len(lines[1])


class TestRgbToString:
    """Tests for the rgb_to_string function."""

    def test_basic_conversion(self):
        """RGB tuple should be converted to MoviePy format."""
        result = rgb_to_string((255, 128, 0))
        assert result == "rgb(255, 128, 0)"

    def test_black(self):
        """Black color should convert correctly."""
        result = rgb_to_string((0, 0, 0))
        assert result == "rgb(0, 0, 0)"

    def test_white(self):
        """White color should convert correctly."""
        result = rgb_to_string((255, 255, 255))
        assert result == "rgb(255, 255, 255)"


class TestCreateTextClip:
    """Tests for the create_text_clip function."""

    def test_basic_creation(self):
        """Should create a basic text clip."""
        clip = create_text_clip(
            text="Hello",
            font_size=48,
            color="rgb(255, 255, 255)",
        )
        assert clip is not None
        assert clip.w > 0
        assert clip.h > 0

    def test_with_max_width_wrapping(self):
        """Text clip with max_width should wrap text."""
        text = "This is a long sentence that should wrap"
        clip = create_text_clip(
            text=text,
            font_size=48,
            color="rgb(255, 255, 255)",
            max_width=300,
        )
        # Clip should exist and have dimensions
        assert clip is not None
        assert clip.w > 0
        assert clip.h > 0

    def test_with_duration(self):
        """Text clip should have specified duration."""
        clip = create_text_clip(
            text="Hello",
            font_size=48,
            color="rgb(255, 255, 255)",
            duration=5.0,
        )
        assert clip.duration == 5.0

    def test_without_duration(self):
        """Text clip without duration should be static."""
        clip = create_text_clip(
            text="Hello",
            font_size=48,
            color="rgb(255, 255, 255)",
        )
        # Duration is None for static clips
        assert clip.duration is None
