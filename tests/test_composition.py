"""
Tests for composition module.
"""

import pytest
from pathlib import Path


class TestAudioSync:
    """Tests for AudioSync."""

    def test_audio_sync_creation(self):
        """AudioSync should be creatable."""
        from video_toolkit.composition import AudioSync

        sync = AudioSync()
        assert sync is not None

    def test_audio_sync_strategies(self):
        """AudioSync should support different strategies."""
        from video_toolkit.composition import AudioSync

        strategies = ["extend_video", "extend_audio", "truncate", "speed_adjust"]
        for strategy in strategies:
            sync = AudioSync(strategy=strategy)
            assert sync.strategy == strategy

    def test_audio_sync_calculate_duration(self):
        """AudioSync should calculate final duration correctly."""
        from video_toolkit.composition import AudioSync

        # extend_video: use audio duration (with padding)
        sync = AudioSync(strategy="extend_video", padding_start=0, padding_end=0)
        assert sync.calculate_duration(video=5.0, audio=7.0) == 7.0

        # extend_audio: use video duration (with padding)
        sync = AudioSync(strategy="extend_audio", padding_start=0, padding_end=0)
        assert sync.calculate_duration(video=5.0, audio=3.0) == 5.0

        # truncate: use shorter (with padding)
        sync = AudioSync(strategy="truncate", padding_start=0, padding_end=0)
        assert sync.calculate_duration(video=5.0, audio=7.0) == 5.0

    def test_audio_sync_with_padding(self):
        """AudioSync should support padding."""
        from video_toolkit.composition import AudioSync

        sync = AudioSync(padding_start=0.5, padding_end=1.0)
        assert sync.padding_start == 0.5
        assert sync.padding_end == 1.0


class TestCompositor:
    """Tests for Compositor."""

    def test_compositor_creation(self):
        """Compositor should be creatable."""
        from video_toolkit.composition import Compositor

        compositor = Compositor()
        assert compositor is not None

    def test_compositor_overlay_application(self):
        """Compositor should track overlays to apply."""
        from video_toolkit.composition import Compositor
        from video_toolkit.overlays import TitleBarOverlay

        compositor = Compositor(overlays=[
            TitleBarOverlay(text="Section"),
        ])
        assert len(compositor.overlays) == 1


class TestConcatenator:
    """Tests for video concatenation."""

    def test_ffmpeg_concatenator_creation(self):
        """FFmpegConcatenator should be creatable."""
        from video_toolkit.composition import FFmpegConcatenator

        concat = FFmpegConcatenator()
        assert concat is not None

    def test_ffmpeg_concatenator_command(self, temp_dir):
        """FFmpegConcatenator should build correct command."""
        from video_toolkit.composition import FFmpegConcatenator

        concat = FFmpegConcatenator()
        files = [
            temp_dir / "seg1.mp4",
            temp_dir / "seg2.mp4",
        ]
        output = temp_dir / "output.mp4"

        cmd = concat.build_command(files, output)

        assert "ffmpeg" in cmd
        assert "-f" in cmd
        assert "concat" in cmd

    def test_moviepy_concatenator_creation(self):
        """MoviePyConcatenator should be creatable."""
        from video_toolkit.composition import MoviePyConcatenator

        concat = MoviePyConcatenator()
        assert concat is not None


class TestDurationMatching:
    """Tests for audio/video duration matching."""

    def test_extend_video_to_audio(self):
        """Video should be extendable to match audio duration."""
        from video_toolkit.composition import AudioSync

        sync = AudioSync(strategy="extend_video", padding_start=0, padding_end=0)

        result = sync.calculate_duration(video=3.0, audio=5.0)
        assert result == 5.0

    def test_extend_audio_to_video(self):
        """Audio should be extendable to match video duration."""
        from video_toolkit.composition import AudioSync

        sync = AudioSync(strategy="extend_audio", padding_start=0, padding_end=0)

        result = sync.calculate_duration(video=5.0, audio=3.0)
        assert result == 5.0

    def test_truncate_to_shorter(self):
        """Both should be truncatable to shorter duration."""
        from video_toolkit.composition import AudioSync

        sync = AudioSync(strategy="truncate", padding_start=0, padding_end=0)

        result = sync.calculate_duration(video=5.0, audio=3.0)
        assert result == 3.0

        result = sync.calculate_duration(video=3.0, audio=5.0)
        assert result == 3.0
