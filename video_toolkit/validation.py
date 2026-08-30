"""Technical validation for final video exports."""

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
from typing import Optional, Union


class MediaValidationError(RuntimeError):
    """Raised when a rendered video fails technical validation."""


@dataclass(frozen=True)
class MediaValidationReport:
    """Technical stream and continuity measurements for a media file."""

    path: Path
    duration: float
    video_duration: float
    audio_duration: Optional[float]
    width: int
    height: int
    fps: float
    sample_rate: Optional[int]
    channels: Optional[int]
    audio_packets: int
    max_audio_gap: float
    max_audio_packet_duration: float


def _run(command: list[str]) -> str:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise MediaValidationError(result.stderr.strip() or "Media probe failed")
    return result.stdout


def _fraction(value: str) -> float:
    numerator, denominator = value.split("/", 1)
    return float(numerator) / float(denominator) if float(denominator) else 0.0


def validate_media(
    path: Union[str, Path],
    *,
    require_audio: bool = True,
    max_audio_gap: float = 0.05,
    duration_tolerance: float = 0.1,
    decode: bool = False,
) -> MediaValidationReport:
    """Validate streams, duration agreement, packet continuity, and decoding.

    ``decode=True`` performs a full decode and is appropriate for a final
    release check. The default probe is fast enough to run after every export.
    """
    path = Path(path)
    if not path.exists():
        raise MediaValidationError(f"Media file does not exist: {path}")

    probe = json.loads(_run([
        "ffprobe", "-v", "error",
        "-show_entries",
        "format=duration:stream=index,codec_type,width,height,r_frame_rate,"
        "sample_rate,channels,duration",
        "-of", "json",
        str(path),
    ]))
    streams = probe.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    if video is None:
        raise MediaValidationError(f"No video stream found in {path}")
    if require_audio and audio is None:
        raise MediaValidationError(f"No audio stream found in {path}")

    duration = float(probe.get("format", {}).get("duration") or 0.0)
    video_duration = float(video.get("duration") or duration)
    audio_duration = float(audio.get("duration") or duration) if audio else None

    audio_packets = 0
    largest_gap = 0.0
    largest_packet = 0.0
    if audio is not None:
        packets = json.loads(_run([
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_packets", "-show_entries", "packet=pts_time,duration_time",
            "-of", "json", str(path),
        ])).get("packets", [])
        previous_end = None
        for packet in packets:
            if "pts_time" not in packet or "duration_time" not in packet:
                continue
            pts = float(packet["pts_time"])
            packet_duration = float(packet["duration_time"])
            if previous_end is not None:
                largest_gap = max(largest_gap, pts - previous_end)
            previous_end = pts + packet_duration
            largest_packet = max(largest_packet, packet_duration)
            audio_packets += 1

        if largest_gap > max_audio_gap:
            raise MediaValidationError(
                f"Audio packet gap of {largest_gap:.3f}s exceeds the "
                f"{max_audio_gap:.3f}s limit in {path}"
            )
        if audio_packets == 0:
            raise MediaValidationError(f"Audio stream has no packets in {path}")

    if audio_duration is not None:
        difference = abs(video_duration - audio_duration)
        if difference > duration_tolerance:
            raise MediaValidationError(
                f"Audio/video durations differ by {difference:.3f}s in {path}"
            )

    if decode:
        _run([
            "ffmpeg", "-hide_banner", "-v", "error", "-i", str(path),
            "-f", "null", "-",
        ])

    return MediaValidationReport(
        path=path,
        duration=duration,
        video_duration=video_duration,
        audio_duration=audio_duration,
        width=int(video.get("width") or 0),
        height=int(video.get("height") or 0),
        fps=_fraction(video.get("r_frame_rate") or "0/1"),
        sample_rate=int(audio["sample_rate"]) if audio and audio.get("sample_rate") else None,
        channels=int(audio["channels"]) if audio and audio.get("channels") else None,
        audio_packets=audio_packets,
        max_audio_gap=max(0.0, largest_gap),
        max_audio_packet_duration=largest_packet,
    )
