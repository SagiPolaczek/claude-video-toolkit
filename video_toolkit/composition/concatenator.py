"""Video concatenation utilities."""

import subprocess
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

from moviepy import VideoFileClip, concatenate_videoclips

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
        """Concatenate video files."""
        pass


@dataclass
class FFmpegConcatenator(Concatenator):
    """Fast concatenation using FFmpeg stream copy."""

    ffmpeg_path: str = "ffmpeg"
    overwrite: bool = True

    def concatenate(
        self,
        files: List[Path],
        output: Path,
        config: Optional["ProjectConfig"] = None,
    ) -> Path:
        """Concatenate videos using FFmpeg concat demuxer."""
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

    def build_command(self, files: List[Path], output: Path) -> str:
        """Build FFmpeg concat command."""
        file_list = "|".join(f"file '{f}'" for f in files)
        overwrite_flag = "-y" if self.overwrite else ""

        cmd = (
            f'{self.ffmpeg_path} {overwrite_flag} '
            f'-f concat -safe 0 -protocol_whitelist file,pipe '
            f'-i <(echo -e "{file_list}") '
            f'-c copy "{output}"'
        )

        return cmd

    def concatenate_with_list_file(self, files: List[Path], output: Path) -> Path:
        """Concatenate using a temporary list file."""
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
        ) as f:
            for file_path in files:
                # Use absolute paths so ffmpeg can find files regardless of CWD
                abs_path = Path(file_path).resolve()
                f.write(f"file '{abs_path}'\n")
            list_file = Path(f.name)

        try:
            cmd = [
                self.ffmpeg_path,
                "-y" if self.overwrite else "",
                "-f", "concat",
                "-safe", "0",
                "-i", str(list_file),
                "-c", "copy",
                str(output),
            ]
            cmd = [c for c in cmd if c]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr}")

            return output

        finally:
            list_file.unlink()


@dataclass
class MoviePyConcatenator(Concatenator):
    """Concatenation using MoviePy."""

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
        """Concatenate videos using MoviePy."""
        clips = [VideoFileClip(str(f)) for f in files]

        try:
            final = concatenate_videoclips(clips, method="compose")

            fps = config.fps if config else self.fps
            codec = config.codec if config else self.codec
            audio_codec = config.audio_codec if config else self.audio_codec

            final.write_videofile(
                str(output),
                fps=fps,
                codec=codec,
                audio_codec=audio_codec,
                preset=self.preset,
            )

            return output

        finally:
            for clip in clips:
                clip.close()
            if "final" in locals():
                final.close()
