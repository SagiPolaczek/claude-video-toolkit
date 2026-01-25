# Claude Video Toolkit

A toolkit for generating narrated presentation videos from websites, codebases, and research papers using Claude Code.
* Generate the video using XX and YY
* Support various TTS engines for dev and production
* Designed to work in segments for faster interactive dev via caching mechanism.

## Quick Start

```bash
git clone https://github.com/anthropics/claude-video-toolkit
cd claude-video-toolkit
pip install -e .
claude
```

## Example - NeuralSVG

```
Generate a project video for NeuralSVG: https://sagipolaczek.github.io/NeuralSVG/
```

This will:
1. Fetch and analyze the project website
2. Download all assets (images, diagrams)
3. Create a narrated video with title, method, results, and conclusion
4. Export to `projects/neural_svg/output/`