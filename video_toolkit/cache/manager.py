"""
Cache manager that orchestrates all cache layers.
"""

from pathlib import Path
from typing import Dict, Optional

from .generated import GeneratedCache
from .tts import TTSCache
from .segments import SegmentCache
from .combined import CombinedCache


class CacheManager:
    """
    Orchestrates the 4-layer cache system.

    Manages cache invalidation cascades:
    - Layer 0 (generated) → Layer 2 → Layer 3
    - Layer 1 (TTS) → Layer 3
    - Layer 2 (segments) → Layer 3
    """

    def __init__(self, base_dir: Path = Path("./cache")):
        """
        Initialize cache manager.

        Args:
            base_dir: Base directory for all caches
        """
        self.base_dir = Path(base_dir)

        # Initialize all cache layers
        self.generated = GeneratedCache(base_dir=self.base_dir / "generated")
        self.tts = TTSCache(base_dir=self.base_dir / "tts")
        self.segments = SegmentCache(base_dir=self.base_dir / "segments")
        self.combined = CombinedCache(base_dir=self.base_dir / "combined")

    def get_status(
        self,
        segment_id: str,
        mode: str,
        engine: str,
        voice: str,
    ) -> Dict[str, bool]:
        """
        Get cache status for a segment.

        Args:
            segment_id: Segment identifier
            mode: Resolution mode
            engine: TTS engine name
            voice: Voice identifier

        Returns:
            Dict with cache layer status
        """
        return {
            "segment": self.segments.exists_for_segment(segment_id, mode),
            "combined": self.combined.exists_for_segment(
                segment_id, mode, engine, voice
            ),
        }

    def invalidate_segment(
        self,
        segment_id: str,
        mode: str,
        cascade: bool = True,
    ) -> Dict[str, int]:
        """
        Invalidate segment cache.

        Args:
            segment_id: Segment identifier
            mode: Resolution mode
            cascade: If True, also invalidate combined cache

        Returns:
            Dict with number of files deleted per layer
        """
        result = {"segments": 0, "combined": 0}

        # Invalidate segment
        if self.segments.invalidate_segment(segment_id, mode):
            result["segments"] = 1

        # Cascade to combined
        if cascade:
            result["combined"] = self.combined.invalidate_segment(
                segment_id, mode, engine=None
            )

        return result

    def invalidate_generated(
        self,
        key: str,
        cascade_segments: Optional[list] = None,
    ) -> Dict[str, int]:
        """
        Invalidate generated content cache.

        Args:
            key: Generator cache key
            cascade_segments: List of (segment_id, mode) tuples to cascade

        Returns:
            Dict with number of files deleted per layer
        """
        result = {"generated": 0, "segments": 0, "combined": 0}

        # Invalidate generated
        if self.generated.invalidate(key):
            result["generated"] = 1

        # Cascade to segments/combined if specified
        if cascade_segments:
            for segment_id, mode in cascade_segments:
                cascade_result = self.invalidate_segment(segment_id, mode)
                result["segments"] += cascade_result["segments"]
                result["combined"] += cascade_result["combined"]

        return result

    def invalidate_tts(
        self,
        key: str,
        cascade_segments: Optional[list] = None,
    ) -> Dict[str, int]:
        """
        Invalidate TTS cache.

        Args:
            key: TTS cache key
            cascade_segments: List of (segment_id, mode, engine) tuples to cascade

        Returns:
            Dict with number of files deleted per layer
        """
        result = {"tts": 0, "combined": 0}

        # Invalidate TTS
        if self.tts.invalidate(key):
            result["tts"] = 1

        # Cascade to combined if specified
        if cascade_segments:
            for segment_id, mode, engine in cascade_segments:
                result["combined"] += self.combined.invalidate_segment(
                    segment_id, mode, engine
                )

        return result

    def clear_all(self) -> Dict[str, int]:
        """
        Clear all caches.

        Returns:
            Dict with number of files deleted per layer
        """
        return {
            "generated": self.generated.clear(),
            "tts": self.tts.clear(),
            "segments": self.segments.clear(),
            "combined": self.combined.clear(),
        }

    def list_all_status(
        self,
        segment_ids: list,
        mode: str,
        engine: str,
        voice: str,
    ) -> Dict[str, Dict[str, bool]]:
        """
        Get cache status for multiple segments.

        Args:
            segment_ids: List of segment identifiers
            mode: Resolution mode
            engine: TTS engine name
            voice: Voice identifier

        Returns:
            Dict mapping segment_id -> status dict
        """
        return {
            sid: self.get_status(sid, mode, engine, voice)
            for sid in segment_ids
        }
