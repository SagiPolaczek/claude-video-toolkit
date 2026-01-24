# Claude Video Toolkit

## What This Is

A toolkit for generating narrated presentation videos. You create video projects by defining segments (title cards, video clips, image slides, comparison grids) and the toolkit handles rendering, TTS narration, caching, and concatenation.

## Project Structure

```
video_toolkit/       # The package (don't modify unless extending)
tests/               # Unit tests (155 tests)
projects/            # User video projects go here
```

## Creating a Video Project

Create a Python file in `projects/` that defines your video:

```python
from video_toolkit import VideoProject
from video_toolkit.segments import TitleSegment, VideoSegment, ImageSegment, GridSegment, GridCell, GridLayout
from video_toolkit.sources import Asset, Placeholder, FunctionGenerator
from video_toolkit.tts_engines import DummyTTSEngine, SopranoTTSEngine
from video_toolkit.config import Resolution

# Create project
project = VideoProject(
    resolution=Resolution.HD_1080,  # or "draft" for 480p, "high" for 2K
    tts_engine=SopranoTTSEngine(),  # or DummyTTSEngine() for no audio
    default_overlays={"title_bar": True, "subtitle": True},
)

# Add segments
project.add_segment(TitleSegment(
    id="0",
    title="My Video",
    subtitle="Subtitle here",
    duration=4.0,
))

project.add_segment(VideoSegment(
    id="1",
    source=Asset("./assets/clip.mp4"),
    narration="This is what I'll say during this clip.",
    section="Introduction",
))

project.add_segment(ImageSegment(
    id="2",
    source=Asset("./figures/diagram.png"),
    duration=5.0,
    narration="Explaining the diagram.",
    section="Method",
))

project.add_segment(GridSegment(
    id="3",
    layout=GridLayout(rows=1, cols=2),
    cells=[
        GridCell(source=Asset("./results/before.mp4"), label="Before"),
        GridCell(source=Asset("./results/after.mp4"), label="After"),
    ],
    narration="Side by side comparison.",
    section="Results",
))

# Build and export
project.build_all()
project.export("./output/my_video.mp4")
```

## Segment Types

| Type | Use For |
|------|---------|
| `TitleSegment` | Title cards with text |
| `VideoSegment` | Video clips |
| `ImageSegment` | Static images (requires duration) |
| `GridSegment` | Multi-video layouts (comparisons, galleries) |

## Content Sources

| Source | Use For |
|--------|---------|
| `Asset("path")` | Existing video/image files |
| `Placeholder("text")` | Debug placeholders |
| `FunctionGenerator(func, key="v1")` | Programmatically generated content |

## 4-Layer Cache

The toolkit caches at each stage to avoid redundant work:
- Layer 0: Generated content
- Layer 1: TTS audio
- Layer 2: Rendered segments (no audio)
- Layer 3: Combined segments (with audio)

Changing narration only rebuilds Layer 1 and 3. Changing video only rebuilds Layer 2 and 3.

## CLI Commands

```bash
python -m video_toolkit --segment 2        # Build one segment
python -m video_toolkit --with-audio 2     # Build with audio
python -m video_toolkit --segments-all     # Build all
python -m video_toolkit --concat           # Concatenate final video
python -m video_toolkit --list             # Show cache status
python -m video_toolkit --draft            # Use 480p for fast iteration
```

## Running Tests

```bash
python -m pytest tests/ -v
```
