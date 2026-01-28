"""Remotion-based segment types."""

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from video_toolkit.segments.base import Segment

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig
    from .renderer import RemotionRenderer


def _remotion_cache_key(data: Dict[str, Any]) -> str:
    """Generate a deterministic cache key for Remotion render output."""
    key_string = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(key_string.encode()).hexdigest()[:16]


@dataclass
class RemotionSegment(Segment):
    """A segment rendered by the Remotion backend.

    Uses a Remotion composition (React component) to render video frames,
    which are output as an MP4. That MP4 is then loaded as a MoviePy clip
    and flows through the existing pipeline (overlays, audio sync, concat).

    Attributes:
        composition_id: Remotion composition ID (e.g., "AnimatedTitle").
        input_props: Props passed to the React component.
        renderer: RemotionRenderer instance (auto-injected by VideoProject).
    """

    composition_id: str = ""
    input_props: Dict[str, Any] = field(default_factory=dict)
    renderer: Optional["RemotionRenderer"] = field(default=None, repr=False)

    def render(self, config: "ProjectConfig") -> Any:
        """Render this segment via Remotion, returning a MoviePy clip.

        1. Compute cache key from composition_id + input_props + dimensions.
        2. If cached MP4 exists, load it directly.
        3. Otherwise, call the Remotion renderer to produce the MP4.
        4. Return a VideoFileClip for the existing pipeline.
        """
        from moviepy import VideoFileClip

        if self.renderer is None:
            raise RuntimeError(
                f"RemotionSegment '{self.id}' has no renderer. "
                "Add it to a VideoProject with remotion_config, or set "
                "segment.renderer manually."
            )

        if self.duration is None:
            raise ValueError(
                f"RemotionSegment '{self.id}' requires explicit duration"
            )

        fps = config.fps
        duration_in_frames = round(self.duration * fps)

        # Check Remotion cache
        cache_dir = config.cache_dir / "remotion"
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_key = _remotion_cache_key({
            "composition_id": self.composition_id,
            "input_props": self.input_props,
            "width": config.width,
            "height": config.height,
            "fps": fps,
            "duration_in_frames": duration_in_frames,
        })
        cached_path = cache_dir / f"{cache_key}.mp4"

        if cached_path.exists():
            print(f"  [Remotion Cache HIT] {self.id}")
            return VideoFileClip(str(cached_path))

        print(f"  [Remotion Rendering] {self.id} ({self.composition_id})...")

        # Inject width/height into props for the React component
        props = {
            **self.input_props,
            "width": config.width,
            "height": config.height,
        }

        self.renderer.render(
            composition_id=self.composition_id,
            input_props=props,
            output_path=str(cached_path),
            duration_in_frames=duration_in_frames,
            width=config.width,
            height=config.height,
            fps=fps,
        )

        return VideoFileClip(str(cached_path))

    def get_duration(self, config: "ProjectConfig") -> float:
        if self.duration is None:
            raise ValueError(
                f"RemotionSegment '{self.id}' requires explicit duration"
            )
        return self.duration


@dataclass
class RemotionTitleSegment(RemotionSegment):
    """Animated title card rendered by Remotion.

    Drop-in replacement for TitleSegment with animated text effects.
    Auto-sets composition_id="AnimatedTitle" and builds input_props.

    Attributes:
        title: Main title text.
        subtitle: Optional subtitle text.
        animation: Animation type ("fade_up", "slide_left", "typewriter", "scale").
        background_color: RGB background color.
        title_color: RGB title text color.
        subtitle_color: RGB subtitle text color.
        title_font: Font family for the title.
        subtitle_font: Font family for the subtitle.
    """

    title: str = ""
    subtitle: Optional[str] = None
    animation: str = "fade_up"
    background_color: Tuple[int, int, int] = (255, 255, 255)
    title_color: Tuple[int, int, int] = (30, 30, 40)
    subtitle_color: Tuple[int, int, int] = (100, 100, 100)
    title_font: str = "Arial"
    subtitle_font: str = "Arial"
    # Title cards typically have no overlays
    overlays: Optional[dict] = None

    def __post_init__(self):
        self.composition_id = "AnimatedTitle"
        self.input_props = self._build_props()

    def _build_props(self) -> Dict[str, Any]:
        """Build Remotion input props from segment attributes."""
        props: Dict[str, Any] = {
            "title": self.title,
            "animation": self.animation,
            "backgroundColor": list(self.background_color),
            "titleColor": list(self.title_color),
            "subtitleColor": list(self.subtitle_color),
            "titleFont": self.title_font,
            "subtitleFont": self.subtitle_font,
        }
        if self.subtitle:
            props["subtitle"] = self.subtitle
        return props


@dataclass
class RemotionImageSegment(RemotionSegment):
    """Image with a reveal effect, rendered by Remotion.

    Drop-in replacement for ImageSegment with animated reveal effects.
    Auto-sets composition_id="ImageReveal" and builds input_props.

    Attributes:
        image_path: Path to the image file.
        effect: Reveal effect ("fade", "wipe_right", "zoom", "blur").
        background_color: RGB background color.
    """

    image_path: str = ""
    effect: str = "fade"
    background_color: Tuple[int, int, int] = (255, 255, 255)

    def __post_init__(self):
        self.composition_id = "ImageReveal"
        self.input_props = self._build_props()

    def _build_props(self) -> Dict[str, Any]:
        props: Dict[str, Any] = {
            "imagePath": self.image_path,
            "effect": self.effect,
        }
        if self.background_color != (255, 255, 255):
            props["backgroundColor"] = list(self.background_color)
        return props


@dataclass
class RemotionKenBurnsSegment(RemotionSegment):
    """Ken Burns (slow pan/zoom) effect on a still image.

    Auto-sets composition_id="KenBurns" and builds input_props.

    Attributes:
        image_path: Path to the image file.
        start_scale: Initial zoom level (default 1.0).
        end_scale: Final zoom level (default 1.2).
        pan_x: Horizontal pan in pixels (default 0).
        pan_y: Vertical pan in pixels (default 0).
        background_color: RGB background color.
    """

    image_path: str = ""
    start_scale: float = 1.0
    end_scale: float = 1.2
    pan_x: float = 0
    pan_y: float = 0
    background_color: Tuple[int, int, int] = (255, 255, 255)

    def __post_init__(self):
        self.composition_id = "KenBurns"
        self.input_props = self._build_props()

    def _build_props(self) -> Dict[str, Any]:
        props: Dict[str, Any] = {
            "imagePath": self.image_path,
            "startScale": self.start_scale,
            "endScale": self.end_scale,
            "panX": self.pan_x,
            "panY": self.pan_y,
        }
        if self.background_color != (255, 255, 255):
            props["backgroundColor"] = list(self.background_color)
        return props


@dataclass
class RemotionSplitScreenSegment(RemotionSegment):
    """Side-by-side comparison with slide-in animation.

    Auto-sets composition_id="SplitScreen" and builds input_props.

    Attributes:
        left_image: Path to the left image.
        right_image: Path to the right image.
        left_label: Optional label for the left panel.
        right_label: Optional label for the right panel.
        background_color: RGB background color.
    """

    left_image: str = ""
    right_image: str = ""
    left_label: Optional[str] = None
    right_label: Optional[str] = None
    background_color: Tuple[int, int, int] = (255, 255, 255)

    def __post_init__(self):
        self.composition_id = "SplitScreen"
        self.input_props = self._build_props()

    def _build_props(self) -> Dict[str, Any]:
        props: Dict[str, Any] = {
            "leftImagePath": self.left_image,
            "rightImagePath": self.right_image,
        }
        if self.left_label:
            props["leftLabel"] = self.left_label
        if self.right_label:
            props["rightLabel"] = self.right_label
        if self.background_color != (255, 255, 255):
            props["backgroundColor"] = list(self.background_color)
        return props


@dataclass
class RemotionCarouselSegment(RemotionSegment):
    """Cycles through multiple images with transitions.

    Auto-sets composition_id="ImageCarousel" and builds input_props.

    Attributes:
        image_paths: List of paths to image files.
        transition: Transition type between images ("fade", "slide", "none").
        background_color: RGB background color.
    """

    image_paths: List[str] = field(default_factory=list)
    transition: str = "fade"
    background_color: Tuple[int, int, int] = (255, 255, 255)

    def __post_init__(self):
        self.composition_id = "ImageCarousel"
        self.input_props = self._build_props()

    def _build_props(self) -> Dict[str, Any]:
        props: Dict[str, Any] = {
            "imagePaths": list(self.image_paths),
            "transition": self.transition,
        }
        if self.background_color != (255, 255, 255):
            props["backgroundColor"] = list(self.background_color)
        return props
