"""RemotionGenerator - ContentSource that renders a Remotion composition."""

from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

from video_toolkit.sources.generators.base import Generator
from video_toolkit.sources.base import generate_cache_key

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig
    from .renderer import RemotionRenderer


class RemotionGenerator(Generator):
    """A ContentSource that renders a Remotion composition to a video file.

    Use this within existing segment types (ImageSegment, VideoSegment)
    to insert Remotion-rendered content.

    Example::

        gen = RemotionGenerator(
            composition_id="ImageReveal",
            input_props={"imagePath": "./assets/teaser.png", "effect": "zoom"},
            duration=5.0,
            key="teaser_reveal",
        )
        project.add_segment(VideoSegment(
            id="teaser", source=gen, narration="Our teaser result.",
        ))
    """

    def __init__(
        self,
        composition_id: str,
        input_props: Dict[str, Any],
        duration: float,
        key: str,
        renderer: Optional["RemotionRenderer"] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: int = 30,
        cache_dir: str | Path = "./cache/remotion",
    ):
        super().__init__(key=key, cache_dir=cache_dir)
        self.composition_id = composition_id
        self.input_props = input_props
        self.duration = duration
        self.renderer = renderer
        self._width = width
        self._height = height
        self._fps = fps

    def generate(self, output_path: Path, config: "ProjectConfig") -> Path:
        if self.renderer is None:
            raise RuntimeError(
                "RemotionGenerator has no renderer set. "
                "Pass renderer= to the constructor or set it after creation."
            )

        width = self._width or config.width
        height = self._height or config.height
        fps = self._fps or config.fps
        duration_in_frames = round(self.duration * fps)

        props = {
            **self.input_props,
            "width": width,
            "height": height,
        }

        self.renderer.render(
            composition_id=self.composition_id,
            input_props=props,
            output_path=str(output_path),
            duration_in_frames=duration_in_frames,
            width=width,
            height=height,
            fps=fps,
        )
        return output_path

    def cache_key(self) -> str:
        return generate_cache_key({
            "type": "remotion_generator",
            "key": self.key,
            "composition_id": self.composition_id,
            "input_props": str(sorted(self.input_props.items())),
            "duration": self.duration,
        })
