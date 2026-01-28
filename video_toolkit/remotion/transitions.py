"""Remotion-based transitions between segments."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TYPE_CHECKING

from .segments import RemotionSegment

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


# Map transition types to Remotion composition IDs
_TRANSITION_COMPOSITIONS = {
    "crossfade": "TransitionFade",
    "slide_left": "TransitionSlide",
    "slide_right": "TransitionSlide",
    "slide_up": "TransitionSlide",
    "slide_down": "TransitionSlide",
    "wipe_right": "TransitionWipe",
    "wipe_left": "TransitionWipe",
    "wipe_up": "TransitionWipe",
    "wipe_down": "TransitionWipe",
}


@dataclass
class RemotionTransition(RemotionSegment):
    """Short transition segment that blends the last frame of the previous
    segment with the first frame of the next segment.

    During ``VideoProject.build_all()``, frames are extracted from neighbouring
    segments and injected into ``input_props`` as ``fromImagePath`` and
    ``toImagePath``.

    Attributes:
        transition_type: Type of transition. One of "crossfade", "slide_left",
            "slide_right", "slide_up", "slide_down", "wipe_right", "wipe_left",
            "wipe_up", "wipe_down".
        from_image: Path to the "from" frame (set automatically by build pipeline).
        to_image: Path to the "to" frame (set automatically by build pipeline).
    """

    transition_type: str = "crossfade"
    from_image: Optional[str] = None
    to_image: Optional[str] = None
    # Transitions have no overlays
    overlays: Optional[dict] = None

    def __post_init__(self):
        if self.duration is None:
            self.duration = 0.5  # Default transition duration

        comp_id = _TRANSITION_COMPOSITIONS.get(self.transition_type)
        if comp_id is None:
            raise ValueError(
                f"Unknown transition type: '{self.transition_type}'. "
                f"Available: {', '.join(_TRANSITION_COMPOSITIONS.keys())}"
            )
        self.composition_id = comp_id
        self.input_props = self._build_props()

    def _build_props(self) -> Dict[str, Any]:
        props: Dict[str, Any] = {}

        if self.from_image:
            props["fromImagePath"] = self.from_image
        if self.to_image:
            props["toImagePath"] = self.to_image

        # Extract direction for slide/wipe transitions
        if self.transition_type.startswith("slide_"):
            props["direction"] = self.transition_type.split("_", 1)[1]
        elif self.transition_type.startswith("wipe_"):
            props["direction"] = self.transition_type.split("_", 1)[1]

        return props

    def set_frames(self, from_image: str, to_image: str) -> None:
        """Set the transition frame images (called by build pipeline).

        Args:
            from_image: Path to the last frame of the previous segment.
            to_image: Path to the first frame of the next segment.
        """
        self.from_image = from_image
        self.to_image = to_image
        self.input_props = self._build_props()

    @property
    def needs_frames(self) -> bool:
        """Whether this transition still needs frame images to be set."""
        return self.from_image is None or self.to_image is None
