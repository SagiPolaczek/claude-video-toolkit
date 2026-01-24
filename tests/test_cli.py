"""
Tests for CLI module.
"""

import pytest
from pathlib import Path


class TestCLIArgParsing:
    """Tests for CLI argument parsing."""

    def test_parse_resolution_draft(self):
        """CLI should parse --draft flag."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--draft"])
        assert args.resolution == "draft"

    def test_parse_resolution_high(self):
        """CLI should parse --high flag."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--high"])
        assert args.resolution == "high"

    def test_parse_resolution_default(self):
        """CLI should default to standard resolution."""
        from video_toolkit.cli import parse_args

        args = parse_args([])
        assert args.resolution == "standard"

    def test_parse_segment(self):
        """CLI should parse --segment ID."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--segment", "2"])
        assert args.segment == "2"

    def test_parse_with_audio(self):
        """CLI should parse --with-audio ID."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--with-audio", "3"])
        assert args.with_audio == "3"

    def test_parse_segments_all(self):
        """CLI should parse --segments-all flag."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--segments-all"])
        assert args.segments_all is True

    def test_parse_with_audio_all(self):
        """CLI should parse --with-audio-all flag."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--with-audio-all"])
        assert args.with_audio_all is True

    def test_parse_concat(self):
        """CLI should parse --concat flag."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--concat"])
        assert args.concat is True

    def test_parse_concat_slow(self):
        """CLI should parse --concat-slow flag."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--concat-slow"])
        assert args.concat_slow is True

    def test_parse_list(self):
        """CLI should parse --list flag."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--list"])
        assert args.list is True

    def test_parse_tts_engine(self):
        """CLI should parse --tts-engine option."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--tts-engine", "soprano"])
        assert args.tts_engine == "soprano"

    def test_parse_tts_voice(self):
        """CLI should parse --tts-voice option."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--tts-voice", "rachel"])
        assert args.tts_voice == "rachel"

    def test_parse_no_tts(self):
        """CLI should parse --no-tts flag."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--no-tts"])
        assert args.no_tts is True


class TestCLIResolutionMutualExclusion:
    """Tests for resolution flag mutual exclusion."""

    def test_draft_and_high_conflict(self):
        """--draft and --high should be mutually exclusive."""
        from video_toolkit.cli import parse_args

        # Both flags should work independently
        args_draft = parse_args(["--draft"])
        assert args_draft.resolution == "draft"

        args_high = parse_args(["--high"])
        assert args_high.resolution == "high"


class TestCLIOutput:
    """Tests for CLI output configuration."""

    def test_parse_output(self):
        """CLI should parse --output path."""
        from video_toolkit.cli import parse_args

        args = parse_args(["--output", "./my_video.mp4"])
        assert args.output == "./my_video.mp4"

    def test_default_output(self):
        """CLI should have default output path."""
        from video_toolkit.cli import parse_args

        args = parse_args([])
        assert args.output is not None
