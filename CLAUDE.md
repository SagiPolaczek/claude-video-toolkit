# Claude Video Toolkit

## What This Is

A toolkit for generating narrated presentation videos from any source: websites, codebases, research papers, or raw data. Define segments (title cards, video clips, images, comparison grids) and the toolkit handles rendering, TTS narration, caching, and concatenation.

## Critical Rules (READ FIRST)

1. **EVERY segment MUST have narration** - including title and conclusion segments
2. **ALWAYS use real assets** - download from source, NEVER use Placeholder in final videos
3. **ALWAYS use SopranoTTSEngine** - not DummyTTSEngine
4. **ALWAYS create project CLAUDE.md** - with source URL, asset manifest, video plan
5. **ALWAYS add CLI with --force flag** - to rebuild cached segments
6. **ALWAYS validate after building** - extract frames, check audio with ffprobe
7. **ALWAYS verify final video has audio** - `ffprobe output.mp4 | grep Audio`

## Creating a Video from a Website or Codebase

**Always download and use the actual graphics, images, and videos from the source.**

### Step 1: Fetch and Analyze the Source

```bash
# For websites - fetch and understand the content
curl -s "https://example.com/project" | ...
```

Identify all available media:
- Teaser/hero images
- Method diagrams
- Result images and videos
- Comparison grids
- Figures and charts

### Step 2: Download Assets

**Use the actual media from the source.** Options:

1. **Clone the repository** (best for GitHub Pages sites):
```bash
# Clone to get all assets at once
git clone https://github.com/username/project.git /tmp/project-source
cp -r /tmp/project-source/static/figures/* projects/my_project/assets/
```

2. **Download directly** from the website:
```bash
mkdir -p projects/my_project/assets
curl -o assets/teaser.png "https://example.com/static/teaser.png"
curl -o assets/method.png "https://example.com/static/method.png"
```

3. **Batch download** multiple assets:
```bash
BASE_URL="https://example.com/static/figures"
for img in teaser method result_1 result_2; do
  curl -s -o "assets/${img}.png" "$BASE_URL/${img}.png" &
done
wait
```

**Label assets clearly:**
- `teaser.png` - Main hero/teaser image
- `method.png` - Architecture or method figure
- `result_*.mp4` - Result videos with descriptive suffixes
- `comparison_before.png`, `comparison_after.png` - Side-by-side pairs
- `dropout_*.png` - Progressive/ablation examples
- `control_*.png` - Control/conditioning examples

### Step 3: Create the Video Project

```python
from video_toolkit import VideoProject
from video_toolkit.segments import TitleSegment, ImageSegment, VideoSegment, GridSegment, GridCell, GridLayout
from video_toolkit.sources import Asset
from video_toolkit.tts_engines import SopranoTTSEngine
from video_toolkit.config import Resolution

project = VideoProject(
    resolution=Resolution.HD_1080,
    tts_engine=SopranoTTSEngine(),  # Always use real TTS for production
    default_overlays={"title_bar": True, "subtitle": True},
)

# Use actual downloaded assets
project.add_segment(ImageSegment(
    id="teaser",
    source=Asset("./assets/teaser.png"),  # Real asset, not placeholder
    duration=5.0,
    narration="...",
    section="Introduction",
))
```

### Step 4: Build and Export

```python
project.build_all()
project.export("./output/video.mp4")
```

## Project Structure

```
projects/
  my_project/
    CLAUDE.md        # Project documentation (plan, asset manifest, notes)
    video.py         # Project definition
    assets/          # Downloaded images/videos (labeled descriptively)
      teaser.png
      method_diagram.png
      result_before.mp4
      result_after.mp4
    output/          # Generated video
    cache/           # Build cache (auto-managed)
```

### Project CLAUDE.md

**Always create a `CLAUDE.md` file in each project directory** with:

1. **Source URL** - Where the content came from
2. **Asset Manifest** - List of downloaded assets with descriptions
3. **Video Plan** - Segment structure and narration outline
4. **Notes** - Any special considerations or TODOs

Example `projects/my_project/CLAUDE.md`:

```markdown
# My Project Video

## Source
https://example.com/project-page

## Assets
| File | Description | Source URL |
|------|-------------|------------|
| teaser.png | Hero image | https://example.com/teaser.png |
| method.png | Architecture diagram | https://example.com/method.png |
| result_ours.mp4 | Our method result | https://example.com/ours.mp4 |

## Video Plan
1. Title (4s) - "Project Name" / "Conference 2025"
2. Teaser (6s) - Hook with main result
3. Motivation (5s) - Problem statement
4. Method (8s) - How it works
5. Results (6s) - Side-by-side comparison
6. Conclusion (4s) - Links and credits

## Notes
- Use 1x2 grid for before/after comparisons
- Keep narration under 15 words per segment
```

## Defaults

- **Background color:** White `(255, 255, 255)` for all segments
- **TTS engine:** SopranoTTSEngine (fast, high-quality)
- **Resolution:** 1080p (1920x1080)
- **Title bar:** Semi-transparent black with white text (configurable via `overlay_styles`)

## Important: Configuration Over Code Changes

**Never modify source code to customize a project.** All customization should be done through:

1. **`overlay_styles`** - Customize overlay appearance (colors, sizes, fonts)
2. **`background_color`** - Per-segment background color
3. **Constructor parameters** - Resolution, TTS engine, defaults

If you need behavior that isn't configurable, add a configuration option to the source code that future projects can use - don't hardcode project-specific values.

## API Reference

### VideoProject

```python
project = VideoProject(
    resolution=Resolution.HD_1080,  # DRAFT (480p), HD_1080 (1080p), HD_2K (2K)
    tts_engine=SopranoTTSEngine(),  # Real narration (preferred)
    default_overlays={"title_bar": True, "subtitle": True},
    overlay_styles={},  # Optional: customize overlay appearance
)

project.add_segment(segment)
project.build_all()
project.export("./output/video.mp4")
```

### Overlay Styles (Configuration)

Customize overlay appearance **via configuration**, not source code changes:

```python
project = VideoProject(
    # ... other settings ...
    overlay_styles={
        "title_bar": {
            "background_color": (255, 255, 255, 200),  # White semi-transparent
            "text_color": (30, 30, 40),  # Dark text
            "height": 50,
            "font_size": 24,
        },
        "subtitle": {
            "background_color": (255, 255, 255, 180),  # White semi-transparent
            "text_color": (30, 30, 40),  # Dark text
            "font_size": 24,
        },
    },
)
```

Available options for `title_bar`:
- `background_color`: RGBA tuple, default `(255, 255, 255, 0)` (transparent)
- `text_color`: RGB tuple, default `(30, 30, 40)` (dark)
- `height`: pixels at 1080p, default `50`
- `font_size`: pixels at 1080p, default `24`
- `position`: `"top"` or `"bottom"`, default `"top"`
- `font`: font name, default `"Arial"`

Available options for `subtitle`:
- `text_color`: RGB tuple, default `(30, 30, 40)` (dark)
- `stroke_width`: default `0` (no outline)
- `font_size`: pixels at 1080p, default `28`
- `margin_bottom`: pixels at 1080p, default `50`
- `font`: font name, default `"Arial"`

### Segment Types

| Type | Use For | Required Fields |
|------|---------|-----------------|
| `TitleSegment` | Title cards | `id`, `title`, `duration` |
| `ImageSegment` | Static images | `id`, `source`, `duration` |
| `VideoSegment` | Video clips | `id`, `source` |
| `GridSegment` | Comparisons/galleries | `id`, `layout`, `cells` |

#### TitleSegment
```python
TitleSegment(
    id="intro",
    title="Title",
    subtitle="Subtitle",
    duration=5.0,
    narration="Title: Subtitle.",  # Always add narration!
)
```

**Important**: Always add narration to title segments. The narration should read the title and subtitle aloud.

#### ImageSegment
```python
ImageSegment(
    id="method",
    source=Asset("./assets/method_diagram.png"),
    duration=8.0,
    narration="This diagram shows our approach...",
    section="Method",
)
```

#### VideoSegment
```python
VideoSegment(
    id="demo",
    source=Asset("./assets/demo.mp4"),
    narration="Watch the demonstration...",
    section="Results",
)
```

#### GridSegment
```python
GridSegment(
    id="comparison",
    layout=GridLayout(rows=1, cols=2),
    cells=[
        GridCell(source=Asset("./assets/before.mp4"), label="Before"),
        GridCell(source=Asset("./assets/after.mp4"), label="After"),
    ],
    narration="Side by side comparison.",
    section="Results",
)
```

### Content Sources

| Source | When to Use |
|--------|-------------|
| `Asset("path")` | **Always preferred** - use real downloaded files |
| `Placeholder("text")` | Only for initial prototyping before assets are ready |
| `FunctionGenerator(fn, key)` | For programmatically generated content |

### TTS Engines

| Engine | Use Case |
|--------|----------|
| `SopranoTTSEngine()` | **Default** - fast, high-quality narration |
| `DummyTTSEngine()` | Silent video (debugging only) |

## Workflow Summary

1. **Fetch source** (website, codebase, paper)
2. **Identify all media** (images, videos, diagrams, comparisons)
3. **Download assets** with descriptive labels
4. **Create video.py** using `Asset()` sources pointing to downloaded files
5. **Write narration** for each segment
6. **Build and validate** - extract first frames to verify segments look correct
7. **Suggest improvements** - propose enhancements to the user
8. **Export final video**

### Suggesting Improvements

After building a working video, **proactively suggest improvements**:

1. **Additional content**: "The source website has 3 more result videos we could add as a comparison grid"
2. **Missing sections**: "Consider adding a limitations segment or ablation study"
3. **Better assets**: "The method diagram is low-res - is there a higher quality version?"
4. **Narration refinements**: "The introduction could mention the key contribution more clearly"
5. **Pacing adjustments**: "The method segment might need more time for the complex diagram"

**Ask the user for content when helpful:**
- "Would you like to add author photos or affiliations?"
- "Is there a video demo we could include?"
- "Should we add a comparison with baseline methods?"

### Validating Segments (REQUIRED)

**Always validate segments after building.** Extract and check first frames:

```bash
# Extract first frame from a segment
ffmpeg -y -ss 0.5 -i cache/segments/segment_NAME_standard.mp4 -frames:v 1 -update 1 /tmp/check_NAME.png

# View the frame (iTerm2)
imgcat /tmp/check_NAME.png

# Check corner pixels for background color verification
python3 -c "
from PIL import Image
img = Image.open('/tmp/check_NAME.png')
w, h = img.size
corners = [img.getpixel((10, 10)), img.getpixel((w-10, 10)),
           img.getpixel((10, h-10)), img.getpixel((w-10, h-10))]
print('Corner pixels:', corners)
"
```

**Validation checklist:**
- [ ] Image centered and proportionally sized
- [ ] White background visible (corners should be white or overlay color)
- [ ] Text overlays readable and properly positioned
- [ ] No clipping, stretching, or aspect ratio issues
- [ ] Colors match expectations (check RGB values of corners)

## Example: Research Paper Video

Given a paper website with teaser, method figure, and result comparisons:

```python
# After downloading:
# assets/teaser.png, assets/method.png, assets/result_*.mp4

project.add_segment(TitleSegment(
    id="title", title="Paper Title", subtitle="Conference 2025", duration=5.0,
    narration="Paper Title, presented at Conference 2025.",
))

project.add_segment(ImageSegment(
    id="teaser", source=Asset("./assets/teaser.png"), duration=6.0,
    narration="We present a novel approach to...",
    section="Introduction",
))

project.add_segment(ImageSegment(
    id="method", source=Asset("./assets/method.png"), duration=8.0,
    narration="Our method works by...",
    section="Method",
))

project.add_segment(GridSegment(
    id="results",
    layout=GridLayout(rows=1, cols=2),
    cells=[
        GridCell(source=Asset("./assets/result_baseline.mp4"), label="Baseline"),
        GridCell(source=Asset("./assets/result_ours.mp4"), label="Ours"),
    ],
    narration="Compared to the baseline, our method...",
    section="Results",
))

project.add_segment(TitleSegment(
    id="conclusion", title="Paper Title", subtitle="github.com/...", duration=5.0,
    narration="Thank you for watching. Visit the project on GitHub for code and examples.",
))
```

## CLI Commands

Each video.py should support these CLI arguments:

```bash
python video.py                    # Build all and export (default)
python video.py --list             # List all segment IDs
python video.py --status           # Show cache status
python video.py --build SEGMENT    # Build a specific segment
python video.py --build SEGMENT --force  # Rebuild segment (ignore cache)
python video.py --force            # Rebuild everything
python video.py --export           # Export final video
python video.py -o OUTPUT_PATH     # Specify output file path
```

### CLI Template for video.py

Add this at the end of every video.py:

```python
if __name__ == "__main__":
    import argparse
    import os
    import glob

    parser = argparse.ArgumentParser(description="Project Video")
    parser.add_argument("--build", metavar="SEGMENT", help="Build a specific segment")
    parser.add_argument("--build-all", action="store_true", help="Build all segments")
    parser.add_argument("--export", action="store_true", help="Export final video")
    parser.add_argument("--status", action="store_true", help="Show cache status")
    parser.add_argument("--list", action="store_true", help="List all segment IDs")
    parser.add_argument("--force", action="store_true", help="Force rebuild (ignore cache)")
    parser.add_argument("-o", "--output", default="./output/video.mp4",
                        help="Output file path")

    args = parser.parse_args()

    def clear_cache_for_segment(seg_id):
        """Clear cached files for a segment to force rebuild."""
        for pattern in [f"cache/segments/segment_{seg_id}_*.mp4",
                        f"cache/combined/segment_{seg_id}_*.mp4"]:
            for f in glob.glob(pattern):
                os.remove(f)
                print(f"  [Removed] {f}")

    if args.list:
        print("Segments:")
        for seg in project.segments:
            print(f"  - {seg.id}")
    elif args.status:
        status = project.list_status()
        print("Cache status:")
        for seg_id, info in status.items():
            cached = "✓" if info.get("segment") else "✗"
            audio = "✓" if info.get("combined") else "✗"
            print(f"  {seg_id}: segment={cached} audio={audio}")
    elif args.build:
        if args.force:
            clear_cache_for_segment(args.build)
        project.build_segment_with_audio(args.build)
    elif args.build_all:
        if args.force:
            for seg in project.segments:
                clear_cache_for_segment(seg.id)
        project.build_all()
    elif args.export:
        if args.force:
            for seg in project.segments:
                clear_cache_for_segment(seg.id)
        project.export(args.output)
    else:
        if args.force:
            for seg in project.segments:
                clear_cache_for_segment(seg.id)
        project.export(args.output)
```

## Final Verification Checklist

Before considering a video project complete:

```bash
# 1. Check video has audio stream
ffprobe output/video.mp4 2>&1 | grep -E "Stream|Audio"
# Should show: Stream #0:1... Audio: aac

# 2. Check video duration is reasonable
ffprobe output/video.mp4 2>&1 | grep Duration

# 3. Extract and view first frame (title)
ffmpeg -y -ss 0.5 -i output/video.mp4 -frames:v 1 /tmp/check_title.png 2>/dev/null
imgcat /tmp/check_title.png

# 4. Extract frame from a content segment
ffmpeg -y -ss 10 -i output/video.mp4 -frames:v 1 /tmp/check_content.png 2>/dev/null
imgcat /tmp/check_content.png
```

**Checklist:**
- [ ] Video has audio stream (not just video)
- [ ] Title text is fully visible (not clipped)
- [ ] Section labels (Introduction, Method, etc.) are readable
- [ ] Images are centered with white background
- [ ] Narration plays throughout the video
- [ ] All segments included in final video

## Running Tests

```bash
python -m pytest tests/ -v
```
