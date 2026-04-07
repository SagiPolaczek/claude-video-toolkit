# Using this skill inside claude-video-toolkit

This skill was imported verbatim from
[NousResearch/hermes-agent — skills/creative/manim-video](https://github.com/NousResearch/hermes-agent/tree/main/skills/creative/manim-video)
(version 1.0.0). `SKILL.md` and `references/*` are **unmodified** so they
can be diffed against upstream.

Read this file **before** following `SKILL.md`. It explains which parts of
the upstream pipeline apply here and which are replaced by the toolkit.

## What applies (use as-is)

Everything pedagogical. This is the reason we pulled the skill in:

- **Creative Standard** — the "every frame teaches / geometry before algebra / breathing room / opacity layering" philosophy
- **Color palettes** (Classic 3B1B, Warm academic, Neon tech, Monochrome)
- **Animation timing table** (run_time + self.wait durations)
- **Typography scale** (48/36/30/24/20)
- **Per-scene variation** rule (different dominant color, layout, entry animation)
- **Critical implementation notes** — raw LaTeX strings, `buff >= 0.5`, FadeOut-before-replace, never animate non-added mobjects
- **`references/animations.md`**, **`mobjects.md`**, **`visual-design.md`**, **`equations.md`**, **`graphs-and-data.md`**, **`camera-and-3d.md`**, **`scene-planning.md`**, **`troubleshooting.md`** — all apply

## What does NOT apply (replaced by video_toolkit)

The upstream skill is a standalone pipeline. This repo already owns the
stages after CODE, so ignore these sections of `SKILL.md`:

| Upstream section | Why it's replaced | Use instead |
|---|---|---|
| **Step 4: STITCH** (ffmpeg concat) | `VideoProject.export()` handles concatenation with crossfades and a consistent output codec | `project.export("./output/video.mp4")` |
| **Step 5: AUDIO** / voiceover workflow in `references/rendering.md` | TTS is per-segment via `SopranoTTSEngine` and composed by `VideoProject`, not muxed post-hoc | `narration="..."` on each segment |
| **`self.add_subcaption(...)` / `subcaption=` on `self.play()`** | Manim writes an SRT sidecar — the toolkit's subtitle overlay is driven by the segment narration and would **collide** with Manim's SRT | Do not call `add_subcaption`. Let the toolkit's `subtitle` overlay render captions from the segment's `narration` field. |
| **Step 3 rendering CLI** (manual `manim -ql script.py Scene1 ...`) | `ManimGenerator` invokes manim for you with the right `--media_dir` and cache paths | See the wiring example below |

## The one-line mental model

> **Write scenes the Hermes way. Render them through `ManimGenerator`.
> Narrate and stitch them through `VideoProject`.**

Each Hermes-style `Scene` class becomes the source for **one**
`VideoSegment`. This is the natural default because `ManimGenerator`
already takes `scene_class: str` as a constructor argument — no code
changes needed.

## Wiring example

Follow `SKILL.md` to write `projects/<name>/manim/script.py` with
`Scene1_Introduction`, `Scene2_CoreConcept`, etc. Then wire them into the
project:

```python
from video_toolkit import VideoProject
from video_toolkit.segments import VideoSegment
from video_toolkit.sources.generators.manim import ManimGenerator
from video_toolkit.tts_engines import SopranoTTSEngine
from video_toolkit.config import Resolution

SCRIPT = "./manim/script.py"

project = VideoProject(
    resolution=Resolution.HD_1080,
    tts_engine=SopranoTTSEngine(),
    default_overlays={"title_bar": True, "subtitle": True},
)

project.add_segment(VideoSegment(
    id="intro",
    source=ManimGenerator(
        scene_class="Scene1_Introduction",
        scene_file=SCRIPT,
        key="intro_v1",       # bump to force re-render
        quality="l",          # 'l' draft, 'h' production
    ),
    narration="Why does this work? Let's start with a picture.",
    section="Introduction",
))

project.add_segment(VideoSegment(
    id="core",
    source=ManimGenerator(
        scene_class="Scene2_CoreConcept",
        scene_file=SCRIPT,
        key="core_v1",
        quality="l",
    ),
    narration="Here is the key geometric intuition before any algebra.",
    section="Method",
))
```

`ManimGenerator` caches by `(key, quality)`, so iterate at `quality="l"`
and flip to `"h"` only for the final export.

## Things that WILL bite you

1. **LaTeX in narration, not MathTex.** Narration is TTS — write prose,
   not equations. Put the equation in the Manim scene; describe it in the
   narration.
2. **Narration length vs scene duration.** The toolkit stretches the
   video to fit narration (or vice versa). If a scene is 4 s of animation
   and narration takes 12 s, the scene freezes on its final frame. Match
   them, or accept the freeze.
3. **Do not call `self.add_subcaption(...)`.** See the table above.
4. **`font=MONO` from the skill uses `"Menlo"`.** That font must be
   installed on the render host. macOS has it; CI Linux often doesn't —
   fall back to `"DejaVu Sans Mono"` if rendering on Linux.
5. **The skill's `plan.md` convention is still valuable.** Write it under
   `projects/<name>/manim/plan.md` before touching `script.py`, even
   though the toolkit doesn't consume it — it's for you and Claude.

## TODO — design decision to make on your first Manim project

The wiring above assumes the **simplest** mapping: one `Scene` class →
one `VideoSegment`. There are two reasonable alternatives you may prefer
once you've tried it:

- **Grouped scenes.** One `VideoSegment` whose `ManimGenerator` renders
  multiple scene classes and concats them (would require extending
  `ManimGenerator` to accept `scene_classes: list[str]`).
- **Scene-as-generator-source for ImageSegment.** Render a Manim
  still frame (`-s` flag) and use it as an `ImageSegment` background,
  useful for "diagram with narration" moments.

**Pick after your first real project**, not before. Delete this TODO
section or replace it with whatever convention you settle on, and — if
you extend `ManimGenerator` — document the new pattern here so future
projects can copy it.
