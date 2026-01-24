"""
Entry point for running video_toolkit as a module.

Usage:
    python -m video_toolkit [options]
"""

from .cli import main
import sys

if __name__ == "__main__":
    sys.exit(main())
