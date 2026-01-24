"""
Command-line interface for video toolkit.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: List of arguments (defaults to sys.argv[1:])

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        prog="video_toolkit",
        description="Video Toolkit - Generate narrated presentation videos",
    )

    # Resolution options
    resolution_group = parser.add_mutually_exclusive_group()
    resolution_group.add_argument(
        "--draft",
        action="store_const",
        const="draft",
        dest="resolution",
        help="Use draft resolution (480p) for fast debugging",
    )
    resolution_group.add_argument(
        "--high",
        action="store_const",
        const="high",
        dest="resolution",
        help="Use high resolution (2K)",
    )
    parser.set_defaults(resolution="standard")

    # Single segment operations
    parser.add_argument(
        "--segment",
        metavar="ID",
        help="Build a single segment by ID (Layer 2: video only)",
    )
    parser.add_argument(
        "--with-audio",
        metavar="ID",
        help="Build a single segment with audio by ID (Layer 3)",
    )

    # Batch operations
    parser.add_argument(
        "--segments-all",
        action="store_true",
        help="Build all segments (Layer 2)",
    )
    parser.add_argument(
        "--with-audio-all",
        action="store_true",
        help="Build all segments with audio (Layer 3)",
    )

    # Concatenation
    parser.add_argument(
        "--concat",
        action="store_true",
        help="Concatenate all segments using FFmpeg (fast, no re-encoding)",
    )
    parser.add_argument(
        "--concat-slow",
        action="store_true",
        help="Concatenate all segments using MoviePy (slow, re-encodes)",
    )

    # TTS options
    tts_group = parser.add_argument_group("TTS options")
    tts_group.add_argument(
        "--tts-engine",
        choices=["soprano", "elevenlabs", "dummy"],
        default="soprano",
        help="TTS engine to use (default: soprano)",
    )
    tts_group.add_argument(
        "--tts-voice",
        help="Voice identifier for TTS engine",
    )
    tts_group.add_argument(
        "--no-tts",
        action="store_true",
        help="Disable TTS (generate video without narration audio)",
    )

    # Output options
    parser.add_argument(
        "--output", "-o",
        default="./output/video.mp4",
        help="Output file path (default: ./output/video.mp4)",
    )

    # Utility options
    parser.add_argument(
        "--list",
        action="store_true",
        help="List cache status for all segments",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clear all caches",
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for CLI.

    Args:
        args: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success)
    """
    parsed_args = parse_args(args)

    try:
        return run_command(parsed_args)
    except KeyboardInterrupt:
        print("\nAborted by user")
        return 130
    except Exception as e:
        print(f"Error: {e}")
        return 1


def run_command(args: argparse.Namespace) -> int:
    """
    Execute the command based on parsed arguments.

    Args:
        args: Parsed arguments

    Returns:
        Exit code
    """
    # Import here to avoid circular imports
    from .project import VideoProject
    from .config import Resolution
    from .tts_engines import get_engine

    # Create project (would normally load from a script file)
    # For now, print a message about usage
    if not any([
        args.segment,
        args.with_audio,
        args.segments_all,
        args.with_audio_all,
        args.concat,
        args.concat_slow,
        args.list,
        args.clean,
    ]):
        print("Video Toolkit")
        print("=============")
        print()
        print("Usage: python -m video_toolkit [options]")
        print()
        print("This CLI expects a project script (my_video.py) that defines segments.")
        print("See the examples/ directory for sample project scripts.")
        print()
        print("Quick reference:")
        print("  --draft           Use 480p resolution for fast debugging")
        print("  --segment ID      Build a single segment (video only)")
        print("  --with-audio ID   Build a single segment with audio")
        print("  --segments-all    Build all segments (video only)")
        print("  --with-audio-all  Build all segments with audio")
        print("  --concat          Concatenate segments (FFmpeg, fast)")
        print("  --concat-slow     Concatenate segments (MoviePy, flexible)")
        print("  --list            Show cache status")
        print("  --clean           Clear all caches")
        return 0

    # Handle list command
    if args.list:
        print("Cache status listing requires a project script.")
        print("Run this command from a directory with a video project.")
        return 0

    # Handle clean command
    if args.clean:
        print("Clearing caches...")
        # Would clear caches here
        print("Done.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
