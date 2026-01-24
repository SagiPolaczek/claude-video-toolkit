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
