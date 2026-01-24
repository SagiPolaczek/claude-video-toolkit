"""
VideoProject - Main orchestrator for video generation.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union, TYPE_CHECKING

from .config import ProjectConfig, Resolution
from .cache import CacheManager
from .composition import AudioSync, Compositor, FFmpegConcatenator
from .overlays import TitleBarOverlay, SubtitleOverlay

if TYPE_CHECKING:
    from .segments import Segment
    from .tts_engines import TTSEngine


class VideoProject:
    """
    Main orchestrator for video generation projects.

    VideoProject manages:
    - Segment collection and ordering
    - Project-level configuration
    - Cache management
    - Build orchestration
    - Final export
    """

    def __init__(
        self,
        resolution: Union[Resolution, str] = Resolution.HD_1080,
        tts_engine: Optional["TTSEngine"] = None,
        default_overlays: Optional[Dict[str, bool]] = None,
        output_dir: Union[str, Path] = "./output",
        cache_dir: Union[str, Path] = "./cache",
        fps: int = 30,
    ):
        """
        Initialize a video project.

        Args:
            resolution: Video resolution (enum or string)
            tts_engine: TTS engine for narration
            default_overlays: Default overlay settings for all segments
            output_dir: Directory for output files
            cache_dir: Directory for cache files
            fps: Frames per second
        """
        self.config = ProjectConfig(
            resolution=resolution,
            output_dir=Path(output_dir),
            cache_dir=Path(cache_dir),
            fps=fps,
        )

        self.tts_engine = tts_engine
        self.default_overlays = default_overlays or {}
        self.segments: List["Segment"] = []

        # Initialize cache manager
        self.cache_manager = CacheManager(base_dir=self.config.cache_dir)

        # Audio sync settings
        self.audio_sync = AudioSync()

        # Ensure output directory exists
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def mode(self) -> str:
        """Get the resolution mode string."""
        mode_map = {
            Resolution.DRAFT: "draft",
            Resolution.HD_1080: "standard",
            Resolution.HD_2K: "high",
        }
        return mode_map.get(self.config.resolution, "standard")

    def add_segment(self, segment: "Segment") -> None:
        """
        Add a segment to the project.

        Args:
            segment: Segment to add
        """
        self.segments.append(segment)

    def get_segment(self, segment_id: str) -> "Segment":
        """
        Get a segment by ID.

        Args:
            segment_id: Segment identifier

        Returns:
            The segment with matching ID

        Raises:
            KeyError: If segment not found
        """
        for segment in self.segments:
            if segment.id == segment_id:
                return segment
        raise KeyError(f"Segment '{segment_id}' not found")

    def build_segment(self, segment_id: str) -> Path:
        """
        Build a single segment (Layer 2: video only, no audio).

        Args:
            segment_id: Segment identifier

        Returns:
            Path to built segment video
        """
        segment = self.get_segment(segment_id)

        # Check cache
        cache_path = self.cache_manager.segments.get_path(
            segment_id=segment_id,
            mode=self.mode,
        )

        if cache_path.exists():
            print(f"  [Cache HIT] {segment_id}")
            return cache_path

        print(f"  [Building] {segment_id}...")

        # Render segment
        clip = segment.render(self.config)

        # Apply overlays
        effective_overlays = segment.get_effective_overlays(self.default_overlays)
        clip = self._apply_overlays(clip, segment, effective_overlays)

        # Write to cache
        clip.write_videofile(
            str(cache_path),
            fps=self.config.fps,
            codec=self.config.codec,
            audio=False,  # No audio in Layer 2
        )

        clip.close()
        return cache_path

    def build_segment_with_audio(self, segment_id: str) -> Path:
        """
        Build a single segment with audio (Layer 3).

        Args:
            segment_id: Segment identifier

        Returns:
            Path to built segment with audio
        """
        segment = self.get_segment(segment_id)

        # Get engine info for cache key
        engine_name = self.tts_engine.get_name() if self.tts_engine else "none"
        voice = self.tts_engine.get_voice() if self.tts_engine else "none"

        # Check cache
        cache_path = self.cache_manager.combined.get_path(
            segment_id=segment_id,
            mode=self.mode,
            engine=engine_name,
            voice=voice,
        )

        if cache_path.exists():
            print(f"  [Cache HIT] {segment_id} (with audio)")
            return cache_path

        # First ensure Layer 2 is built
        video_path = self.build_segment(segment_id)

        print(f"  [Adding audio] {segment_id}...")

        # Load video
        from moviepy import VideoFileClip, AudioFileClip

        video_clip = VideoFileClip(str(video_path))

        # Generate/get audio if narration exists
        if segment.narration and self.tts_engine:
            audio_path = self.tts_engine.synthesize_cached(segment.narration)
            audio_clip = AudioFileClip(audio_path)

            # Sync audio with video
            final_clip = self.audio_sync.sync_clips(
                video_clip, audio_clip, self.config
            )
        else:
            final_clip = video_clip

        # Write to cache
        final_clip.write_videofile(
            str(cache_path),
            fps=self.config.fps,
            codec=self.config.codec,
            audio_codec=self.config.audio_codec,
        )

        final_clip.close()
        video_clip.close()

        return cache_path

    def build_all(self) -> List[Path]:
        """
        Build all segments (Layer 2 and Layer 3).

        Returns:
            List of paths to all built segments
        """
        paths = []
        for segment in self.segments:
            if segment.narration and self.tts_engine:
                path = self.build_segment_with_audio(segment.id)
            else:
                path = self.build_segment(segment.id)
            paths.append(path)
        return paths

    def export(self, output_path: Union[str, Path]) -> Path:
        """
        Export final concatenated video.

        Args:
            output_path: Output file path

        Returns:
            Path to exported video
        """
        output_path = Path(output_path)

        # Build all segments first
        segment_paths = self.build_all()

        # Concatenate
        print(f"  [Concatenating] {len(segment_paths)} segments...")

        concatenator = FFmpegConcatenator()
        concatenator.concatenate_with_list_file(segment_paths, output_path)

        print(f"  [Done] {output_path}")
        return output_path

    def list_status(self) -> Dict[str, Dict[str, bool]]:
        """
        Get cache status for all segments.

        Returns:
            Dict mapping segment_id -> cache status
        """
        engine_name = self.tts_engine.get_name() if self.tts_engine else "none"
        voice = self.tts_engine.get_voice() if self.tts_engine else "none"

        return self.cache_manager.list_all_status(
            segment_ids=[s.id for s in self.segments],
            mode=self.mode,
            engine=engine_name,
            voice=voice,
        )

    def _apply_overlays(
        self,
        clip,
        segment: "Segment",
        effective_overlays: Dict[str, bool],
    ):
        """Apply overlays to a clip based on settings."""
        compositor = Compositor()

        # Title bar
        if effective_overlays.get("title_bar") and segment.section:
            compositor.add_overlay(TitleBarOverlay(text=segment.section))

        # Subtitle
        if effective_overlays.get("subtitle") and segment.narration:
            compositor.add_overlay(SubtitleOverlay(text=segment.narration))

        return compositor.compose(clip, self.config)
