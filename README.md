# Claude Video Toolkit

A toolkit for generating narrated presentation videos from websites, codebases, and research papers using Claude Code.

https://github.com/anthropics/claude-video-toolkit/raw/main/projects/neural_svg/output/neural_svg.mp4

*Example: Auto-generated video for [NeuralSVG](https://sagipolaczek.github.io/NeuralSVG/) — created with a single prompt.*

## Features

- **Segment-based workflow** — title cards, images, videos, comparison grids
- **Automatic narration** — TTS engines for dev (fast) and production (high-quality)
- **Smart caching** — rebuild only what changed for fast iteration
- **Overlay system** — configurable title bars, subtitles, watermarks

## Quick Start

```bash
git clone https://github.com/anthropics/claude-video-toolkit
cd claude-video-toolkit
pip install -e .
claude
```

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