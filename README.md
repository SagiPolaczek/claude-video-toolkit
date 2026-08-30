# Agentic Video Toolkit

A toolkit for generating polished narrated videos from websites, codebases, and
research papers with an agentic, segment-based workflow.

https://github.com/SagiPolaczek/agentic-video-toolkit/raw/main/projects/neural_svg/output/neural_svg.mp4

*Example: Auto-generated video for [NeuralSVG](https://sagipolaczek.github.io/NeuralSVG/) — created with a single prompt.*

## Features

- **Segment-based workflow** — title cards, images, videos, comparison grids
- **Automatic narration** — TTS engines for dev (fast) and production (high-quality)
- **Smart caching** — rebuild only what changed for fast iteration
- **Overlay system** — configurable title bars, subtitles, watermarks

## Quick Start

```bash
git clone https://github.com/SagiPolaczek/agentic-video-toolkit
cd agentic-video-toolkit
pip install -e .
claude
```

## Production audio workflow

Build visuals quickly with a local voice, lock the script, then synthesize the
production voice once. Preflight narration before the visual export so speech
is never clipped and a long voice does not silently freeze the last frame:

```python
from video_toolkit import VideoProject
from video_toolkit.composition import AudioSync
from video_toolkit.tts_engines import ElevenLabsTTSEngine

project = VideoProject(
    tts_engine=ElevenLabsTTSEngine(
        voice_id="your-voice-id",
        model_id="eleven_multilingual_v2",
    ),
    audio_sync=AudioSync(
        strategy="extend_audio",
        padding_start=0.25,
        padding_end=0.5,
        overflow_policy="error",
    ),
)

# Synthesizes cache misses and raises before rendering if a line is too long.
project.preflight_narration(raise_on_overflow=True)
project.export("output/final.mp4")
```

Set `ELEVENLABS_API_KEY` in the process environment. Do not commit API keys or
put them in project source. Combined A/V caches are keyed by both engine and
voice, so switching voices cannot accidentally reuse an old narration render.

### Keep a finished clip's soundtrack

Use `preserve_audio=True` for an authored opening, trailer, or other finished
clip. Its audio is normalized to the project's AAC sample rate and stereo
layout before concatenation:

```python
from video_toolkit.segments import VideoSegment
from video_toolkit.sources import Asset

project.add_segment(VideoSegment(
    id="intro",
    source=Asset("assets/finished_intro.mp4"),
    duration=22,
    preserve_audio=True,
    overlays=None,
))
```

Do not also set `narration` on that segment: source sound and TTS narration are
deliberately mutually exclusive.

## Release validation

`VideoProject.export()` now performs a fast stream and audio-packet continuity
check. For the final upload, also request a complete decode:

```python
from video_toolkit import validate_media

report = validate_media("output/final.mp4", decode=True)
print(report.duration, report.max_audio_gap)
```

Production review should also sample every visual state, not only one frame per
segment. For comparison layouts, center each label over its actual media column
and inspect transitions between different column counts. Keep decorative accent
rules attached to headings, use a pinned professional font, and verify QR codes
from compressed frames at the smallest expected playback size.

## Example - NeuralSVG

The video above was generated with a single prompt:

```
Generate a project video for NeuralSVG: https://sagipolaczek.github.io/NeuralSVG/
```

Claude Code will:
1. Fetch and analyze the project website
2. Download all assets (images, videos, diagrams)
3. Create a narrated video with title, method, results, and conclusion
4. Export to `projects/neural_svg/output/`

See the [project files](projects/neural_svg/) for the generated `video.py` and asset manifest.
