"""
Tests for segments module.
"""

import pytest
from pathlib import Path


class TestSegmentBase:
    """Tests for Segment abstract base class."""

    def test_segment_is_abstract(self):
        """Segment should be abstract and not directly instantiable."""
        from video_toolkit.segments import Segment

        with pytest.raises(TypeError):
            Segment(id="0")

    def test_segment_requires_render(self):
        """Segment subclasses must implement render."""
        from video_toolkit.segments import Segment

        class Incomplete(Segment):
            pass

        with pytest.raises(TypeError):
            Incomplete(id="0")


class TestVideoSegment:
    """Tests for VideoSegment."""

    def test_video_segment_creation(self):
        """VideoSegment should be creatable with source."""
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        seg = VideoSegment(
            id="1",
            source=Placeholder("Test"),
        )
        assert seg.id == "1"
        assert seg.source is not None

    def test_video_segment_with_narration(self):
        """VideoSegment should accept narration text."""
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        seg = VideoSegment(
            id="1",
            source=Placeholder("Test"),
            narration="This is the narration.",
        )
        assert seg.narration == "This is the narration."

    def test_video_segment_with_section(self):
        """VideoSegment should accept section name."""
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        seg = VideoSegment(
            id="1",
            source=Placeholder("Test"),
            section="Introduction",
        )
        assert seg.section == "Introduction"

    def test_video_segment_overlay_control(self):
        """VideoSegment should support overlay enable/disable."""
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        seg = VideoSegment(
            id="1",
            source=Placeholder("Test"),
            overlays={"subtitle": False, "title_bar": True},
        )
        assert seg.overlays["subtitle"] is False
        assert seg.overlays["title_bar"] is True

    def test_video_segment_default_overlays_inherit(self):
        """VideoSegment with overlays={} should use project defaults."""
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        seg = VideoSegment(
            id="1",
            source=Placeholder("Test"),
            overlays={},  # Empty dict = use defaults
        )
        assert seg.overlays == {}

    def test_video_segment_no_overlays(self):
        """VideoSegment with overlays=None should disable all overlays."""
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        seg = VideoSegment(
            id="1",
            source=Placeholder("Test"),
            overlays=None,  # None = no overlays
        )
        assert seg.overlays is None


class TestImageSegment:
    """Tests for ImageSegment."""

    def test_image_segment_creation(self):
        """ImageSegment should be creatable with source and duration."""
        from video_toolkit.segments import ImageSegment
        from video_toolkit.sources import Asset

        seg = ImageSegment(
            id="2",
            source=Asset("./image.png"),
            duration=5.0,
        )
        assert seg.id == "2"
        assert seg.duration == 5.0

    def test_image_segment_requires_duration(self):
        """ImageSegment should require explicit duration."""
        from video_toolkit.segments import ImageSegment
        from video_toolkit.sources import Asset

        seg = ImageSegment(
            id="2",
            source=Asset("./image.png"),
            duration=3.0,
        )
        assert seg.duration == 3.0

    def test_image_segment_zoom_pan(self):
        """ImageSegment should support zoom and pan effects."""
        from video_toolkit.segments import ImageSegment
        from video_toolkit.sources import Asset

        seg = ImageSegment(
            id="2",
            source=Asset("./image.png"),
            duration=5.0,
            zoom=1.1,
            pan="left_to_right",
        )
        assert seg.zoom == 1.1
        assert seg.pan == "left_to_right"


class TestTitleSegment:
    """Tests for TitleSegment."""

    def test_title_segment_creation(self):
        """TitleSegment should be creatable with title and duration."""
        from video_toolkit.segments import TitleSegment

        seg = TitleSegment(
            id="0",
            title="My Presentation",
            duration=5.0,
        )
        assert seg.id == "0"
        assert seg.title == "My Presentation"
        assert seg.duration == 5.0

    def test_title_segment_with_subtitle(self):
        """TitleSegment should accept optional subtitle."""
        from video_toolkit.segments import TitleSegment

        seg = TitleSegment(
            id="0",
            title="Main Title",
            subtitle="Subtitle Here",
            duration=4.0,
        )
        assert seg.subtitle == "Subtitle Here"

    def test_title_segment_no_source_required(self):
        """TitleSegment should not require a source."""
        from video_toolkit.segments import TitleSegment

        seg = TitleSegment(
            id="0",
            title="Title",
            duration=3.0,
        )
        # Should work without source
        assert seg.title == "Title"


class TestGridSegment:
    """Tests for GridSegment and related classes."""

    def test_grid_cell_creation(self):
        """GridCell should be creatable with source."""
        from video_toolkit.segments import GridCell
        from video_toolkit.sources import Placeholder

        cell = GridCell(
            source=Placeholder("Cell 1"),
            label="Test Label",
        )
        assert cell.source is not None
        assert cell.label == "Test Label"

    def test_grid_cell_position(self):
        """GridCell should support explicit position."""
        from video_toolkit.segments import GridCell
        from video_toolkit.sources import Placeholder

        cell = GridCell(
            source=Placeholder("Cell"),
            position=(0, 1),
        )
        assert cell.position == (0, 1)

    def test_grid_cell_span(self):
        """GridCell should support row/col spanning."""
        from video_toolkit.segments import GridCell
        from video_toolkit.sources import Placeholder

        cell = GridCell(
            source=Placeholder("Cell"),
            span=(2, 1),  # Spans 2 rows, 1 col
        )
        assert cell.span == (2, 1)

    def test_grid_layout_creation(self):
        """GridLayout should define rows and columns."""
        from video_toolkit.segments import GridLayout

        layout = GridLayout(rows=2, cols=3)
        assert layout.rows == 2
        assert layout.cols == 3

    def test_grid_layout_aspect_ratio(self):
        """GridLayout should have configurable cell aspect ratio."""
        from video_toolkit.segments import GridLayout

        layout = GridLayout(rows=2, cols=2, cell_aspect_ratio=16/9)
        assert layout.cell_aspect_ratio == pytest.approx(16/9)

    def test_grid_segment_creation(self):
        """GridSegment should be creatable with cells and layout."""
        from video_toolkit.segments import GridSegment, GridCell, GridLayout
        from video_toolkit.sources import Placeholder

        seg = GridSegment(
            id="grid",
            layout=GridLayout(rows=1, cols=2),
            cells=[
                GridCell(source=Placeholder("A"), label="Left"),
                GridCell(source=Placeholder("B"), label="Right"),
            ],
        )
        assert seg.id == "grid"
        assert len(seg.cells) == 2

    def test_grid_segment_gap(self):
        """GridSegment should support gap between cells."""
        from video_toolkit.segments import GridSegment, GridCell, GridLayout
        from video_toolkit.sources import Placeholder

        seg = GridSegment(
            id="grid",
            layout=GridLayout(rows=1, cols=2),
            cells=[
                GridCell(source=Placeholder("A")),
                GridCell(source=Placeholder("B")),
            ],
            gap=10,
        )
        assert seg.gap == 10

    def test_grid_segment_without_layout(self):
        """GridSegment should work with explicit cell positions."""
        from video_toolkit.segments import GridSegment, GridCell
        from video_toolkit.sources import Placeholder

        seg = GridSegment(
            id="grid",
            cells=[
                GridCell(source=Placeholder("A"), position=(0, 0)),
                GridCell(source=Placeholder("B"), position=(0, 1)),
            ],
        )
        assert seg.layout is None
        assert len(seg.cells) == 2


class TestSegmentOverlayMerging:
    """Tests for overlay inheritance and merging."""

    def test_merge_overlays_with_defaults(self):
        """Segment should merge overlays with project defaults."""
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        seg = VideoSegment(
            id="1",
            source=Placeholder("Test"),
            overlays={"subtitle": False},
        )

        defaults = {"title_bar": True, "subtitle": True}
        merged = seg.get_effective_overlays(defaults)

        assert merged["title_bar"] is True  # From defaults
        assert merged["subtitle"] is False  # Overridden

    def test_merge_overlays_empty_uses_defaults(self):
        """Empty overlays dict should use all defaults."""
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        seg = VideoSegment(
            id="1",
            source=Placeholder("Test"),
            overlays={},
        )

        defaults = {"title_bar": True, "subtitle": True}
        merged = seg.get_effective_overlays(defaults)

        assert merged == defaults

    def test_merge_overlays_none_disables_all(self):
        """None overlays should disable all overlays."""
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        seg = VideoSegment(
            id="1",
            source=Placeholder("Test"),
            overlays=None,
        )

        defaults = {"title_bar": True, "subtitle": True}
        merged = seg.get_effective_overlays(defaults)

        assert merged == {}


class TestSegmentDuration:
    """Tests for segment duration handling."""

    def test_video_segment_duration_from_source(self):
        """VideoSegment duration should come from source if not specified."""
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        seg = VideoSegment(
            id="1",
            source=Placeholder("Test", duration=5.0),
        )
        # Duration should be determined by source at render time
        assert seg.duration is None

    def test_video_segment_explicit_duration(self):
        """VideoSegment should accept explicit duration."""
        from video_toolkit.segments import VideoSegment
        from video_toolkit.sources import Placeholder

        seg = VideoSegment(
            id="1",
            source=Placeholder("Test", duration=5.0),
            duration=3.0,  # Explicit override
        )
        assert seg.duration == 3.0

    def test_title_segment_duration_required(self):
        """TitleSegment should require explicit duration."""
        from video_toolkit.segments import TitleSegment

        seg = TitleSegment(
            id="0",
            title="Title",
            duration=5.0,
        )
        assert seg.duration == 5.0
