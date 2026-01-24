"""Manim generator for math visualizations."""

import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from .base import Generator

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


# Quality mapping from simple names to manim flags
QUALITY_MAP = {
    "l": "-ql",     # 480p15
    "m": "-qm",     # 720p30
    "h": "-qh",     # 1080p60
    "p": "-qp",     # 1440p60
    "k": "-qk",     # 4K60
}


class ManimGenerator(Generator):
    """
    Generator that renders Manim scenes to video.

    Uses the Manim library (either from submodule or pip install)
    to render mathematical animations.
    """

    def __init__(
        self,
        scene_class: str,
        scene_file: str | Path,
        key: str,
        quality: str = "l",
        cache_dir: str | Path = "./generated",
        use_submodule: bool = False,
    ):
        """
        Initialize ManimGenerator.

        Args:
            scene_class: Name of the Scene class to render
            scene_file: Path to the Python file containing the scene
            key: Unique cache key for this configuration
            quality: Rendering quality ('l', 'm', 'h', 'p', 'k')
            cache_dir: Directory for caching generated videos
            use_submodule: If True, use the external/manim submodule
        """
        super().__init__(key=key, cache_dir=cache_dir)
        self.scene_class = scene_class
        self.scene_file = Path(scene_file)
        self.quality = quality
        self.use_submodule = use_submodule

        if quality not in QUALITY_MAP:
            raise ValueError(f"Invalid quality '{quality}'. Use: {list(QUALITY_MAP.keys())}")

    def _get_manim_command(self) -> list[str]:
        """Get the manim command, preferring submodule if configured."""
        if self.use_submodule:
            submodule_path = Path(__file__).parent.parent.parent.parent / "external" / "manim"
            if submodule_path.exists():
                return [sys.executable, "-m", "manim"]
            else:
                raise RuntimeError(
                    "Manim submodule not found. Run: git submodule update --init"
                )

        return ["manim"]

    def generate(self, output_path: Path, config: "ProjectConfig") -> Path:
        """
        Generate video by rendering the Manim scene.

        Args:
            output_path: Path to save the generated video
            config: Project configuration

        Returns:
            Path to the generated video file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        quality_flag = QUALITY_MAP[self.quality]

        cmd = self._get_manim_command() + [
            "render",
            quality_flag,
            "--media_dir", str(output_path.parent / "_manim_media"),
            "-o", output_path.stem,
            str(self.scene_file),
            self.scene_class,
        ]

        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent.parent / "external" / "manim")

        try:
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                env=env,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Manim rendering failed:\n{e.stderr}")
        except FileNotFoundError:
            raise RuntimeError(
                "Manim not found. Install with: pip install manim\n"
                "Or use the submodule: git submodule update --init"
            )

        # Manim outputs to a nested directory structure, find the output
        media_dir = output_path.parent / "_manim_media" / "videos" / self.scene_file.stem

        # Find the rendered file (quality-dependent subdirectory)
        for quality_dir in media_dir.iterdir() if media_dir.exists() else []:
            rendered_file = quality_dir / f"{output_path.stem}.mp4"
            if rendered_file.exists():
                rendered_file.rename(output_path)
                return output_path

        # If not found in expected location, check for any mp4
        if media_dir.exists():
            for mp4_file in media_dir.rglob("*.mp4"):
                mp4_file.rename(output_path)
                return output_path

        raise RuntimeError(f"Manim rendered but output not found in {media_dir}")

    def cache_key(self) -> str:
        """Generate cache key including all render parameters."""
        return f"{self.key}_{self.quality}"
