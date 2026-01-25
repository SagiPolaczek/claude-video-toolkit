"""
Function-based content generator.
"""

from pathlib import Path
from typing import Callable, Any, TYPE_CHECKING

from .base import Generator
from ..base import generate_cache_key

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


class FunctionGenerator(Generator):
    """
    Generator that calls a Python function to create content.

    The function should have the signature:
        def render(output_path: Path, config: ProjectConfig, **kwargs) -> Path

    Example:
        def render_chart(output_path, config, data_file, chart_type="bar"):
            # Create chart and save to output_path
            ...
            return output_path

        gen = FunctionGenerator(
            render_chart,
            key="chart_v1",
            data_file="./data.csv",
            chart_type="line"
        )
    """

    def __init__(
        self,
        func: Callable,
        key: str,
        cache_dir: str | Path = "./generated",
        **kwargs,
    ):
        """
        Create a function generator.

        Args:
            func: Function to call for generating content
            key: Unique key for caching (change when logic changes)
            cache_dir: Directory for caching generated content
            **kwargs: Additional arguments passed to the function
        """
        super().__init__(key=key, cache_dir=cache_dir)
        self.func = func
        self.kwargs = kwargs

    def generate(self, output_path: Path, config: "ProjectConfig") -> Path:
        """
        Generate content by calling the function.

        Args:
            output_path: Path to save the generated video
            config: Project configuration

        Returns:
            Path to the generated file
        """
        result = self.func(output_path, config, **self.kwargs)
        return Path(result) if result else output_path

    def cache_key(self) -> str:
        """
        Generate cache key from key and kwargs.

        The cache key includes:
        - The generator key (version identifier)
        - All kwargs (parameters that affect output)
        """
        return generate_cache_key({
            "type": "function_generator",
            "key": self.key,
            "kwargs": tuple(sorted(self.kwargs.items())),
        })

    def __str__(self) -> str:
        return f"FunctionGenerator({self.func.__name__}, key={self.key!r})"

    def __repr__(self) -> str:
        return f"FunctionGenerator(func={self.func}, key={self.key!r}, kwargs={self.kwargs})"
