"""
Segment video cache (Layer 2).
"""

from pathlib import Path

from .base import CacheLayer


class SegmentCache(CacheLayer):
    """
    Cache for rendered video segments (without audio).

    This is Layer 2 of the cache system. It stores rendered
    video segments with overlays applied, but without narration audio.

    Cache path is based on:
    - Segment ID
    - Resolution mode (draft, standard, high)
    """

    def __init__(self, base_dir: Path = Path("./segments")):
        super().__init__(base_dir)

    def get_path(
        self,
        segment_id: str = None,
        mode: str = "standard",
        key: str = None,
        **kwargs,
    ) -> Path:
        """
        Get cache path for a segment video.

        Args:
            segment_id: Segment identifier (e.g., "1", "2_1")
            mode: Resolution mode
            key: Alternative key (if segment_id not provided)

        Returns:
            Path to cached segment video
        """
        if segment_id is not None:
            filename = f"segment_{segment_id}_{mode}.mp4"
        elif key is not None:
            filename = f"{key}.mp4"
        else:
            raise ValueError("Either segment_id or key must be provided")

        return self.base_dir / filename

    def exists_for_segment(self, segment_id: str, mode: str) -> bool:
        """Check if segment is cached."""
        return self.get_path(segment_id=segment_id, mode=mode).exists()

    def invalidate_segment(self, segment_id: str, mode: str) -> bool:
        """Invalidate segment cache."""
        path = self.get_path(segment_id=segment_id, mode=mode)
        if path.exists():
            path.unlink()
            return True
        return False
