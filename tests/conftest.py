"""
Pytest fixtures for video toolkit tests.
"""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_video_path(temp_dir):
    """Path for a sample video file (doesn't create the file)."""
    return temp_dir / "sample_video.mp4"


@pytest.fixture
def sample_image_path(temp_dir):
    """Path for a sample image file (doesn't create the file)."""
    return temp_dir / "sample_image.png"


@pytest.fixture
def sample_audio_path(temp_dir):
    """Path for a sample audio file (doesn't create the file)."""
    return temp_dir / "sample_audio.wav"


@pytest.fixture
def cache_dir(temp_dir):
    """Create a temporary cache directory."""
    cache = temp_dir / "cache"
    cache.mkdir()
    return cache


@pytest.fixture
def output_dir(temp_dir):
    """Create a temporary output directory."""
    output = temp_dir / "output"
    output.mkdir()
    return output


@pytest.fixture
def project_config():
    """Default project configuration for tests."""
    from video_toolkit.config import Resolution
    return {
        "resolution": Resolution.HD_1080,
        "fps": 30,
    }
