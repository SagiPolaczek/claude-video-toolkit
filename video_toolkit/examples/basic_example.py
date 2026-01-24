#!/usr/bin/env python3
"""
Basic example demonstrating video toolkit usage.

This example creates a simple video with:
- Title card
- Video segment with narration
- Comparison grid
- End card
"""

from video_toolkit import VideoProject
from video_toolkit.segments import TitleSegment, VideoSegment, GridSegment, GridCell, GridLayout
from video_toolkit.sources import Asset, Placeholder
from video_toolkit.tts_engines import DummyTTSEngine
from video_toolkit.config import Resolution


def create_example_project():
    """Create an example video project."""

    # Create project with dummy TTS engine (for testing without real TTS)
    project = VideoProject(
        resolution=Resolution.HD_1080,
        tts_engine=DummyTTSEngine(),
        default_overlays={
            "title_bar": True,
            "subtitle": True,
        },
    )

    # Add title card
    project.add_segment(TitleSegment(
        id="0",
        title="Example Video",
        subtitle="Created with Video Toolkit",
        duration=4.0,
    ))

    # Add video segment with placeholder (replace with real Asset for production)
    project.add_segment(VideoSegment(
        id="1",
        source=Placeholder("Introduction", duration=5.0),
        narration="Welcome to this example video.",
        section="Introduction",
    ))

    # Add comparison grid
    project.add_segment(GridSegment(
        id="2",
        layout=GridLayout(rows=1, cols=2),
        cells=[
            GridCell(
                source=Placeholder("Before", duration=5.0),
                label="Before",
            ),
            GridCell(
                source=Placeholder("After", duration=5.0),
                label="After",
            ),
        ],
        narration="Here's a side-by-side comparison.",
        section="Comparison",
    ))

    # Add ending
    project.add_segment(TitleSegment(
        id="3",
        title="Thank You",
        subtitle="github.com/example/video-toolkit",
        duration=3.0,
    ))

    return project


if __name__ == "__main__":
    project = create_example_project()

    # List cache status
    print("Segments:")
    for seg in project.segments:
        print(f"  {seg.id}: {type(seg).__name__}")

    # To build the video:
    # project.build_all()
    # project.export("./output/example.mp4")

    print("\nTo build, uncomment the build lines in this script.")
