"""Tests for final media validation."""

import shutil
import subprocess

import pytest


pytestmark = pytest.mark.skipif(
    not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
    reason="ffmpeg and ffprobe are required",
)


def test_validate_media_reports_continuous_audio(temp_dir):
    from video_toolkit import validate_media

    output = temp_dir / "valid.mp4"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=160x90:r=20:d=1",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
        "-t", "1", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "44100", "-ac", "2", str(output),
    ], check=True)

    report = validate_media(output, decode=True)

    assert report.width == 160
    assert report.height == 90
    assert report.fps == pytest.approx(20.0)
    assert report.sample_rate == 44100
    assert report.channels == 2
    assert report.audio_packets > 0
    assert report.max_audio_gap <= 0.05


def test_validate_media_rejects_missing_audio(temp_dir):
    from video_toolkit import MediaValidationError, validate_media

    output = temp_dir / "silent.mp4"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "lavfi", "-i", "color=c=black:s=160x90:r=20:d=0.2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(output),
    ], check=True)

    with pytest.raises(MediaValidationError, match="No audio stream"):
        validate_media(output)
