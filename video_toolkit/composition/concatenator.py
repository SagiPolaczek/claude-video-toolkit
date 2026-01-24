"""
Video concatenation utilities.
"""

import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


class Concatenator(ABC):
    """Abstract base class for video concatenators."""

    @abstractmethod
    def concatenate(
        self,
        files: List[Path],
        output: Path,
        config: Optional["ProjectConfig"] = None,
    ) -> Path:
        """
        Concatenate video files.

        Args:
            files: List of video file paths
            output: Output file path
            config: Optional project configuration

        Returns:
            Path to concatenated video
        """
        pass


@dataclass
class FFmpegConcatenator(Concatenator):
    """
    Fast concatenation using FFmpeg stream copy.

    This method is fast because it doesn't re-encode the video,
    but requires all input files to have the same codec settings.
    """

    ffmpeg_path: str = "ffmpeg"
    overwrite: bool = True

    def concatenate(
        self,
        files: List[Path],
        output: Path,
        config: Optional["ProjectConfig"] = None,
    ) -> Path:
        """
        Concatenate videos using FFmpeg concat demuxer.

        Args:
            files: List of video file paths
            output: Output file path
            config: Optional project configuration

        Returns:
            Path to concatenated video
        """
        cmd = self.build_command(files, output)

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")

        return output

    def build_command(
        self,
        files: List[Path],
        output: Path,
    ) -> str:
        """
        Build FFmpeg concat command.

        Args:
            files: List of video file paths
            output: Output file path

        Returns:
            FFmpeg command string
        """
        # Create concat list file content
        file_list = "|".join(f"file '{f}'" for f in files)

        # Build command
        overwrite_flag = "-y" if self.overwrite else ""

        # Use concat protocol for simple concatenation
        cmd = (
            f'{self.ffmpeg_path} {overwrite_flag} '
            f'-f concat -safe 0 -protocol_whitelist file,pipe '
            f'-i <(echo -e "{file_list}") '
            f'-c copy "{output}"'
        )

        return cmd

    def concatenate_with_list_file(
        self,
        files: List[Path],
        output: Path,
    ) -> Path:
        """
        Concatenate using a temporary list file.

        More compatible approach that works in all shells.
        """
        # Create temporary file list
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
        ) as f:
            for file_path in files:
                f.write(f"file '{file_path}'\n")
            list_file = Path(f.name)

        try:
            overwrite_flag = "-y" if self.overwrite else ""
            cmd = [
                self.ffmpeg_path,
                "-y" if self.overwrite else "",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_file),
                "-c", "copy",
                str(output),
            ]
            cmd = [c for c in cmd if c]  # Remove empty strings

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")

            return output

        finally:
            list_file.unlink()


@dataclass
class MoviePyConcatenator(Concatenator):
    """
    Concatenation using MoviePy.

    This method re-encodes the video, which is slower but more flexible.
    Use when input files have different codecs or settings.
    """

    fps: int = 30
    codec: str = "libx264"
    audio_codec: str = "aac"
    preset: str = "medium"

    def concatenate(
        self,
        files: List[Path],
        output: Path,
        config: Optional["ProjectConfig"] = None,
    ) -> Path:
        """
        Concatenate videos using MoviePy.

        Args:
            files: List of video file paths
            output: Output file path
            config: Optional project configuration

        Returns:
            Path to concatenated video
        """
        from moviepy import VideoFileClip, concatenate_videoclips

        # Load all clips
        clips = [VideoFileClip(str(f)) for f in files]

        try:
            # Concatenate
            final = concatenate_videoclips(clips, method="compose")

            # Get settings from config or use defaults
            fps = config.fps if config else self.fps
            codec = config.codec if config else self.codec
            audio_codec = config.audio_codec if config else self.audio_codec

            # Write output
            final.write_videofile(
                str(output),
                fps=fps,
                codec=codec,
                audio_codec=audio_codec,
                preset=self.preset,
            )

            return output

        finally:
            # Clean up
            for clip in clips:
                clip.close()
            if "final" in locals():
                final.close()
