"""
Tests for VideoProject orchestrator.
"""

import pytest
from pathlib import Path


class TestVideoProjectCreation:
    """Tests for VideoProject creation."""

    def test_video_project_creation(self, temp_dir):
        """VideoProject should be creatable with minimal config."""
        from video_toolkit import VideoProject

        project = VideoProject(
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )
        assert project is not None

    def test_video_project_with_resolution(self, temp_dir):
        """VideoProject should accept resolution."""
        from video_toolkit import VideoProject
        from video_toolkit.config import Resolution

        project = VideoProject(
            resolution=Resolution.DRAFT,
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )
        assert project.config.resolution == Resolution.DRAFT

    def test_video_project_with_resolution_string(self, temp_dir):
        """VideoProject should accept resolution as string."""
        from video_toolkit import VideoProject
        from video_toolkit.config import Resolution

        project = VideoProject(
            resolution="draft",
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )
        assert project.config.resolution == Resolution.DRAFT

    def test_video_project_with_tts_engine(self, temp_dir):
        """VideoProject should accept TTS engine."""
        from video_toolkit import VideoProject
        from video_toolkit.tts_engines import DummyTTSEngine

        engine = DummyTTSEngine(cache_dir=str(temp_dir / "tts"))
        project = VideoProject(
            tts_engine=engine,
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )
        assert project.tts_engine == engine


class TestVideoProjectSegments:
    """Tests for segment management."""

    def test_add_segment(self, temp_dir):
        """VideoProject should support adding segments."""
        from video_toolkit import VideoProject
        from video_toolkit.segments import TitleSegment

        project = VideoProject(
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )

        project.add_segment(TitleSegment(
            id="0",
            title="Test",
            duration=3.0,
        ))

        assert len(project.segments) == 1
        assert project.segments[0].id == "0"

    def test_get_segment_by_id(self, temp_dir):
        """VideoProject should support getting segment by ID."""
        from video_toolkit import VideoProject
        from video_toolkit.segments import TitleSegment

        project = VideoProject(
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )

        project.add_segment(TitleSegment(id="0", title="First", duration=3.0))
        project.add_segment(TitleSegment(id="1", title="Second", duration=3.0))

        seg = project.get_segment("1")
        assert seg.title == "Second"

    def test_get_segment_not_found(self, temp_dir):
        """VideoProject should raise for unknown segment ID."""
        from video_toolkit import VideoProject

        project = VideoProject(
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )

        with pytest.raises(KeyError):
            project.get_segment("nonexistent")


class TestVideoProjectOverlays:
    """Tests for overlay configuration."""

    def test_default_overlays(self, temp_dir):
        """VideoProject should support default overlays."""
        from video_toolkit import VideoProject

        project = VideoProject(
            default_overlays={
                "title_bar": True,
                "subtitle": True,
            },
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )

        assert project.default_overlays["title_bar"] is True
        assert project.default_overlays["subtitle"] is True


class TestVideoProjectCaching:
    """Tests for project caching."""

    def test_cache_manager_initialized(self, temp_dir):
        """VideoProject should initialize cache manager."""
        from video_toolkit import VideoProject

        project = VideoProject(
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )

        assert project.cache_manager is not None

    def test_list_status(self, temp_dir):
        """VideoProject should report cache status."""
        from video_toolkit import VideoProject
        from video_toolkit.segments import TitleSegment

        project = VideoProject(
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )

        project.add_segment(TitleSegment(id="0", title="Test", duration=3.0))

        status = project.list_status()
        assert "0" in status


class TestVideoProjectModeString:
    """Tests for resolution mode string."""

    def test_mode_string_draft(self, temp_dir):
        """Mode string should be 'draft' for DRAFT resolution."""
        from video_toolkit import VideoProject
        from video_toolkit.config import Resolution

        project = VideoProject(
            resolution=Resolution.DRAFT,
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )

        assert project.mode == "draft"

    def test_mode_string_standard(self, temp_dir):
        """Mode string should be 'standard' for HD_1080."""
        from video_toolkit import VideoProject
        from video_toolkit.config import Resolution

        project = VideoProject(
            resolution=Resolution.HD_1080,
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )

        assert project.mode == "standard"


class TestProductionAudioWorkflow:
    """Regression tests from production research-video rendering."""

    def test_preserved_audio_cannot_be_mixed_with_narration(self, temp_dir):
        from video_toolkit import VideoProject
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        project = VideoProject(
            tts_engine=None,
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )
        project.add_segment(VideoSegment(
            id="intro",
            source=Placeholder("intro"),
            narration="Do not mix this with source sound.",
            preserve_audio=True,
        ))

        with pytest.raises(ValueError, match="cannot use narration and preserve_audio"):
            project.build_segment_with_audio("intro")

    def test_preserved_audio_status_uses_source_cache_identity(self, temp_dir):
        from video_toolkit import VideoProject
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        project = VideoProject(
            tts_engine=None,
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )
        project.add_segment(VideoSegment(
            id="intro",
            source=Placeholder("intro"),
            preserve_audio=True,
        ))
        project.cache_manager.combined.get_path(
            "intro", project.mode, "source", "original"
        ).touch()

        assert project.list_status()["intro"]["combined"] is True

    def test_preflight_can_fail_before_visual_render(self, temp_dir):
        import wave
        from video_toolkit import VideoProject
        from video_toolkit.composition import AudioSync, NarrationOverflowError
        from video_toolkit.segments import TitleSegment
        from video_toolkit.tts_engines import TTSEngine

        class FixedDurationEngine(TTSEngine):
            def synthesize(self, text, output_path):
                with wave.open(output_path, "wb") as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(44100)
                    wav.writeframes(b"\0\0" * 88200)
                return output_path

            def get_name(self):
                return "fixed"

            def get_voice(self):
                return "two-seconds"

        project = VideoProject(
            tts_engine=FixedDurationEngine(str(temp_dir / "tts")),
            audio_sync=AudioSync(
                strategy="extend_audio",
                padding_end=0.5,
                overflow_policy="error",
            ),
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )
        project.add_segment(TitleSegment(
            id="short",
            title="Short",
            duration=1.0,
            narration="This is deliberately too long.",
        ))

        with pytest.raises(NarrationOverflowError, match="Segment 'short'"):
            project.preflight_narration(raise_on_overflow=True)

    def test_preserved_source_audio_is_normalized(self, temp_dir):
        import shutil
        import subprocess

        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            pytest.skip("ffmpeg and ffprobe are required")

        from video_toolkit import VideoProject, validate_media
        from video_toolkit.config import Resolution
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Asset

        source = temp_dir / "intro.mp4"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "color=c=black:s=160x90:r=24:d=0.5",
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
            "-t", "0.5", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-ar", "48000", "-ac", "1", str(source),
        ], check=True)

        project = VideoProject(
            resolution=Resolution.DRAFT,
            fps=20,
            tts_engine=None,
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )
        project.add_segment(VideoSegment(
            id="intro",
            source=Asset(source),
            duration=0.5,
            scale="stretch",
            preserve_audio=True,
            overlays=None,
        ))

        rendered = project.build_segment_with_audio("intro")
        report = validate_media(rendered, duration_tolerance=0.15)

        assert report.sample_rate == 44100
        assert report.channels == 2
        assert report.fps == pytest.approx(20.0)
