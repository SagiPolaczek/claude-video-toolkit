"""
NeuralSVG: An Implicit Representation for Text-to-Vector Generation
ICCV 2025

Source: https://sagipolaczek.github.io/NeuralSVG/
"""

import sys
from pathlib import Path

# Add parent to path so we can import video_toolkit
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from video_toolkit import VideoProject, Resolution
from video_toolkit.segments import TitleSegment, ImageSegment
from video_toolkit.sources import Asset
from video_toolkit.tts_engines import Qwen3TTSEngine

# Create project
project = VideoProject(
    resolution=Resolution.HD_1080,
    tts_engine=Qwen3TTSEngine(speaker="Aiden"),  # English male voice
    default_overlays={"title_bar": True, "subtitle": True},
    output_dir="./output",
    cache_dir="./cache",
)

# ============================================================================
# SEGMENT 1: Title
# ============================================================================
project.add_segment(TitleSegment(
    id="title",
    title="NeuralSVG",
    subtitle="An Implicit Representation for Text-to-Vector Generation",
    duration=4.0,
    narration="NeuralSVG: An Implicit Representation for Text-to-Vector Generation. Presented at ICCV 2025.",
))

# ============================================================================
# SEGMENT 2: Teaser
# ============================================================================
project.add_segment(ImageSegment(
    id="teaser",
    source=Asset("./assets/teaser.png"),
    duration=5.0,
    narration="NeuralSVG generates high-quality vector graphics from text descriptions, producing clean, layered SVG structures ready for design applications.",
    section="Introduction",
))

# ============================================================================
# SEGMENT 3: Method
# ============================================================================
project.add_segment(ImageSegment(
    id="method",
    source=Asset("./assets/method.png"),
    duration=8.0,
    narration="We encode the entire scene into a small MLP network, inspired by NeRF. The network is optimized using Score Distillation Sampling, and dropout regularization encourages an ordered, layered structure.",
    section="Method",
))

# ============================================================================
# SEGMENT 4: Generation Examples
# ============================================================================
project.add_segment(ImageSegment(
    id="generation",
    source=Asset("./assets/generation_1.png"),
    duration=6.0,
    narration="Given a text prompt, NeuralSVG produces detailed vector graphics. Here we see examples ranging from animals to objects, each rendered as a clean SVG.",
    section="Results",
))

# ============================================================================
# SEGMENT 5: Dropout Regularization
# ============================================================================
project.add_segment(ImageSegment(
    id="dropout",
    source=Asset("./assets/dropout_rooster.png"),
    duration=6.0,
    narration="Our dropout-based regularization creates naturally layered outputs. As we decrease dropout probability, the SVG structure emerges progressively from coarse to fine details.",
    section="Results",
))

# ============================================================================
# SEGMENT 6: Color Control
# ============================================================================
project.add_segment(ImageSegment(
    id="color_control",
    source=Asset("./assets/control_color_spaceship.png"),
    duration=6.0,
    narration="A single learned representation enables runtime control over color palettes. The same generation can be conditioned on different color schemes without retraining.",
    section="Control",
))

# ============================================================================
# SEGMENT 7: Aspect Ratio
# ============================================================================
project.add_segment(ImageSegment(
    id="aspect_ratio",
    source=Asset("./assets/aspect_sportscar.png"),
    duration=6.0,
    narration="NeuralSVG supports dynamic aspect ratio adjustment at inference time, adapting the output to various canvas shapes while maintaining visual quality.",
    section="Control",
))

# ============================================================================
# SEGMENT 8: Sketches
# ============================================================================
project.add_segment(ImageSegment(
    id="sketches",
    source=Asset("./assets/sketch_ballerina.png"),
    duration=5.0,
    narration="The method can also generate black and white sketches, useful for line art and illustration workflows.",
    section="Control",
))

# ============================================================================
# SEGMENT 9: Conclusion
# ============================================================================
project.add_segment(TitleSegment(
    id="conclusion",
    title="NeuralSVG",
    subtitle="sagipolaczek.github.io/NeuralSVG/",
    duration=4.0,
    narration="Thank you for watching. Visit the project page for code, paper, and more examples.",
))


# ============================================================================
# CLI
# ============================================================================
if __name__ == "__main__":
    import argparse
    import os
    import glob

    parser = argparse.ArgumentParser(description="NeuralSVG Video")
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
            cached = "+" if info.get("segment") else "-"
            audio = "+" if info.get("combined") else "-"
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
        # Default: build all and export
        if args.force:
            for seg in project.segments:
                clear_cache_for_segment(seg.id)
        project.export(args.output)
