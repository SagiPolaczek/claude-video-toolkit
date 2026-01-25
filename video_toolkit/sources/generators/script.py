"""
Script-based content generator.
"""

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from .base import Generator
from ..base import generate_cache_key

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


class ScriptGenerator(Generator):
    """
    Generator that runs an external script/command to create content.

    The command is a template string that can include variables:
    - {output_path}: Path where the output should be saved
    - {width}, {height}: Video dimensions
    - {fps}: Frames per second
    - Any additional kwargs passed to the constructor

    Example:
        gen = ScriptGenerator(
            command="python render_scene.py --output {output_path} --scene {scene}",
            key="scene_v1",
            scene="intro"
        )
    """

    def __init__(
        self,
        command: str,
        key: str,
        cache_dir: str | Path = "./generated",
        timeout: int = 300,
        **kwargs,
    ):
        """
        Create a script generator.

        Args:
            command: Command template to execute
            key: Unique key for caching
            cache_dir: Directory for caching generated content
            timeout: Maximum execution time in seconds
            **kwargs: Variables to substitute in the command template
        """
        super().__init__(key=key, cache_dir=cache_dir)
        self.command = command
        self.timeout = timeout
        self.kwargs = kwargs

    def generate(self, output_path: Path, config: "ProjectConfig") -> Path:
        """
        Generate content by running the command.

        Args:
            output_path: Path to save the generated video
            config: Project configuration

        Returns:
            Path to the generated file

        Raises:
            subprocess.CalledProcessError: If command fails
            subprocess.TimeoutExpired: If command times out
        """
        # Build template variables
        template_vars = {
            "output_path": str(output_path),
            "width": config.width,
            "height": config.height,
            "fps": config.fps,
            **self.kwargs,
        }

        # Format the command
        cmd = self.command.format(**template_vars)

        # Execute
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=self.timeout,
            check=True,
        )

        return output_path

    def cache_key(self) -> str:
        """
        Generate cache key from command, key, and kwargs.
        """
        return generate_cache_key({
            "type": "script_generator",
            "key": self.key,
            "command": self.command,
            "kwargs": tuple(sorted(self.kwargs.items())),
        })

    def __str__(self) -> str:
        return f"ScriptGenerator(key={self.key!r})"

    def __repr__(self) -> str:
        return f"ScriptGenerator(command={self.command!r}, key={self.key!r})"
