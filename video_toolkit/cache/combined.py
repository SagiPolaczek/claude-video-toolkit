"""
Combined video+audio cache (Layer 3).
"""

from pathlib import Path

from .base import CacheLayer


class CombinedCache(CacheLayer):
    """
    Cache for combined video segments with audio.

    This is Layer 3 of the cache system. It stores the final
    rendered segments with narration audio mixed in.

    Cache path is based on:
    - Segment ID
    - Resolution mode
    - TTS engine name
    - Voice identifier
    """

    def __init__(self, base_dir: Path = Path("./segments_with_audio")):
        super().__init__(base_dir)

    def get_path(
        self,
        segment_id: str = None,
        mode: str = "standard",
        engine: str = "none",
        voice: str = "default",
        key: str = None,
        **kwargs,
    ) -> Path:
        """
        Get cache path for a combined segment.

        Args:
            segment_id: Segment identifier
            mode: Resolution mode
            engine: TTS engine name
            voice: Voice identifier
            key: Alternative key (if segment_id not provided)

        Returns:
            Path to cached combined video
        """
        if segment_id is not None:
            filename = f"segment_{segment_id}_{mode}_{engine}.mp4"
        elif key is not None:
            filename = f"{key}.mp4"
        else:
            raise ValueError("Either segment_id or key must be provided")

        return self.base_dir / filename

    def exists_for_segment(
        self,
        segment_id: str,
        mode: str,
        engine: str,
        voice: str,
    ) -> bool:
        """Check if combined segment is cached."""
        return self.get_path(
            segment_id=segment_id,
            mode=mode,
            engine=engine,
            voice=voice,
        ).exists()

    def invalidate_segment(
        self,
        segment_id: str,
        mode: str,
        engine: str = None,
    ) -> int:
        """
        Invalidate combined cache for a segment.

        If engine is None, invalidates all engine variants.

        Returns:
            Number of files deleted
        """
        count = 0
        pattern = f"segment_{segment_id}_{mode}_*.mp4"

        if engine is not None:
            # Specific engine
            path = self.get_path(segment_id=segment_id, mode=mode, engine=engine)
            if path.exists():
                path.unlink()
                count = 1
        else:
            # All engines
            for path in self.base_dir.glob(pattern):
                path.unlink()
                count += 1

        return count
