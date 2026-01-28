"""VideoProject - Main orchestrator for video generation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union, TYPE_CHECKING

from moviepy import VideoFileClip, AudioFileClip

from .config import ProjectConfig, Resolution
from .cache import CacheManager
from .composition import AudioSync, Compositor, FFmpegConcatenator
from .overlays import TitleBarOverlay, SubtitleOverlay

if TYPE_CHECKING:
    from .segments import Segment
    from .tts_engines import TTSEngine
    from .remotion.config import RemotionConfig
    from .remotion.renderer import RemotionRenderer

_USE_DEFAULT_TTS = object()  # Sentinel for default TTS engine


class VideoProject:
    """Main orchestrator for video generation projects."""

    def __init__(
        self,
        resolution: Union[Resolution, str] = Resolution.HD_1080,
        tts_engine: Optional["TTSEngine"] = _USE_DEFAULT_TTS,
        default_overlays: Optional[Dict[str, bool]] = None,
        overlay_styles: Optional[Dict[str, Dict]] = None,
        output_dir: Union[str, Path] = "./output",
        cache_dir: Union[str, Path] = "./cache",
        fps: int = 30,
        remotion_config: Optional["RemotionConfig"] = None,
    ):
        self.config = ProjectConfig(
            resolution=resolution,
            output_dir=Path(output_dir),
            cache_dir=Path(cache_dir),
            fps=fps,
        )

        if tts_engine is _USE_DEFAULT_TTS:
            from .tts_engines import SopranoTTSEngine
            self.tts_engine = SopranoTTSEngine()
        else:
            self.tts_engine = tts_engine
        self.default_overlays = default_overlays or {}
        self.overlay_styles = overlay_styles or {}
        self.segments: List["Segment"] = []

        self.cache_manager = CacheManager(base_dir=self.config.cache_dir)
        self.audio_sync = AudioSync()
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Remotion support (lazy-initialized)
        self._remotion_config = remotion_config
        self._remotion_renderer: Optional["RemotionRenderer"] = None

    @property
    def mode(self) -> str:
        """Get the resolution mode string."""
        mode_map = {
            Resolution.DRAFT: "draft",
            Resolution.HD_1080: "standard",
            Resolution.HD_2K: "high",
        }
        return mode_map.get(self.config.resolution, "standard")

    @property
    def remotion_renderer(self) -> "RemotionRenderer":
        """Get or create the Remotion renderer (lazy initialization).

        Only created when the first RemotionSegment is added, so projects
        that don't use Remotion pay zero overhead.
        """
        if self._remotion_renderer is None:
            from .remotion.config import RemotionConfig
            from .remotion.renderer import RemotionRenderer

            config = self._remotion_config or RemotionConfig()
            self._remotion_renderer = RemotionRenderer(config, self.config)
        return self._remotion_renderer

    def add_segment(self, segment: "Segment") -> None:
        """Add a segment to the project.

        If the segment is a RemotionSegment without a renderer, the project's
        shared RemotionRenderer is auto-injected.
        """
        from .remotion.segments import RemotionSegment

        if isinstance(segment, RemotionSegment) and segment.renderer is None:
            segment.renderer = self.remotion_renderer

        self.segments.append(segment)

    def get_segment(self, segment_id: str) -> "Segment":
        """Get a segment by ID."""
        for segment in self.segments:
            if segment.id == segment_id:
                return segment
        raise KeyError(f"Segment '{segment_id}' not found")

    def build_segment(self, segment_id: str) -> Path:
        """Build a single segment (Layer 2: video only, no audio)."""
        segment = self.get_segment(segment_id)

        cache_path = self.cache_manager.segments.get_path(
            segment_id=segment_id,
            mode=self.mode,
        )

        if cache_path.exists():
            print(f"  [Cache HIT] {segment_id}")
            return cache_path

        print(f"  [Building] {segment_id}...")

        clip = segment.render(self.config)

        effective_overlays = segment.get_effective_overlays(self.default_overlays)
        clip = self._apply_overlays(clip, segment, effective_overlays)

        clip.write_videofile(
            str(cache_path),
            fps=self.config.fps,
            codec=self.config.codec,
            audio=False,
        )

        clip.close()
        return cache_path

    def build_segment_with_audio(self, segment_id: str, force_audio: bool = True) -> Path:
        """Build a single segment with audio (Layer 3).

        Args:
            segment_id: ID of the segment to build
            force_audio: If True, add silent audio to segments without narration
        """
        from moviepy.audio.AudioClip import AudioClip
        import numpy as np

        segment = self.get_segment(segment_id)

        engine_name = self.tts_engine.get_name() if self.tts_engine else "none"
        voice = self.tts_engine.get_voice() if self.tts_engine else "none"

        cache_path = self.cache_manager.combined.get_path(
            segment_id=segment_id,
            mode=self.mode,
            engine=engine_name,
            voice=voice,
        )

        if cache_path.exists():
            print(f"  [Cache HIT] {segment_id} (with audio)")
            return cache_path

        video_path = self.build_segment(segment_id)

        print(f"  [Adding audio] {segment_id}...")

        video_clip = VideoFileClip(str(video_path))

        if segment.narration and self.tts_engine:
            audio_path = self.tts_engine.synthesize_cached(segment.narration)
            audio_clip = AudioFileClip(audio_path)

            final_clip = self.audio_sync.sync_clips(
                video_clip, audio_clip, self.config
            )
        elif force_audio:
            # Add silent audio track to ensure consistent streams for concatenation
            def make_silence(t):
                if isinstance(t, np.ndarray):
                    return np.zeros((len(t), 2))
                return np.zeros(2)

            silent_audio = AudioClip(make_silence, duration=video_clip.duration, fps=44100)
            final_clip = video_clip.with_audio(silent_audio)
        else:
            final_clip = video_clip

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
        """Build all segments with audio (Layer 3).

        All segments get audio tracks (silent if no narration) to ensure
        consistent streams for concatenation.

        For RemotionTransition segments, extracts frames from neighbouring
        segments before rendering the transition.
        """
        self._prepare_transitions()

        paths = []
        for segment in self.segments:
            path = self.build_segment_with_audio(segment.id)
            paths.append(path)
        return paths

    def _prepare_transitions(self) -> None:
        """Extract frames for any RemotionTransition segments that need them."""
        from .remotion.transitions import RemotionTransition

        for i, segment in enumerate(self.segments):
            if not isinstance(segment, RemotionTransition):
                continue
            if not segment.needs_frames:
                continue

            # Find previous and next non-transition segments
            prev_seg = None
            next_seg = None
            for j in range(i - 1, -1, -1):
                if not isinstance(self.segments[j], RemotionTransition):
                    prev_seg = self.segments[j]
                    break
            for j in range(i + 1, len(self.segments)):
                if not isinstance(self.segments[j], RemotionTransition):
                    next_seg = self.segments[j]
                    break

            if prev_seg is None or next_seg is None:
                print(
                    f"  [Warning] Transition '{segment.id}' has no "
                    f"{'previous' if prev_seg is None else 'next'} segment"
                )
                continue

            # Build the neighbouring segments (video only) so we can extract frames
            prev_path = self.build_segment(prev_seg.id)
            next_path = self.build_segment(next_seg.id)

            # Extract last frame of previous and first frame of next
            frames_dir = self.config.cache_dir / "transition_frames"
            frames_dir.mkdir(parents=True, exist_ok=True)

            from_frame = frames_dir / f"from_{segment.id}.png"
            to_frame = frames_dir / f"to_{segment.id}.png"

            self._extract_frame(prev_path, from_frame, position="last")
            self._extract_frame(next_path, to_frame, position="first")

            segment.set_frames(str(from_frame), str(to_frame))

    @staticmethod
    def _extract_frame(
        video_path: Path, output_path: Path, position: str = "first"
    ) -> None:
        """Extract a single frame from a video file.

        Args:
            video_path: Path to the source video.
            output_path: Where to save the extracted frame (PNG).
            position: "first" or "last".
        """
        import subprocess

        if position == "last":
            # Seek near end - use ffprobe to get duration, then seek
            probe = subprocess.run(
                [
                    "ffprobe", "-v", "error",
                    "-show_entries", "format=duration",
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    str(video_path),
                ],
                capture_output=True, text=True,
            )
            duration = float(probe.stdout.strip()) if probe.stdout.strip() else 1.0
            seek_time = max(0, duration - 0.1)
            cmd = [
                "ffmpeg", "-y", "-ss", str(seek_time),
                "-i", str(video_path),
                "-frames:v", "1", "-update", "1",
                str(output_path),
            ]
        else:
            cmd = [
                "ffmpeg", "-y", "-ss", "0.033",
                "-i", str(video_path),
                "-frames:v", "1", "-update", "1",
                str(output_path),
            ]

        subprocess.run(cmd, capture_output=True, timeout=30)

    def export(self, output_path: Union[str, Path]) -> Path:
        """Export final concatenated video."""
        output_path = Path(output_path)

        segment_paths = self.build_all()

        print(f"  [Concatenating] {len(segment_paths)} segments...")

        concatenator = FFmpegConcatenator()
        concatenator.concatenate_with_list_file(segment_paths, output_path)

        print(f"  [Done] {output_path}")
        return output_path

    def list_status(self) -> Dict[str, Dict[str, bool]]:
        """Get cache status for all segments."""
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

        if effective_overlays.get("title_bar") and segment.section:
            title_bar_style = self.overlay_styles.get("title_bar", {})
            compositor.add_overlay(TitleBarOverlay(text=segment.section, **title_bar_style))

        if effective_overlays.get("subtitle") and segment.narration:
            subtitle_style = self.overlay_styles.get("subtitle", {})
            compositor.add_overlay(SubtitleOverlay(text=segment.narration, **subtitle_style))

        return compositor.compose(clip, self.config)
