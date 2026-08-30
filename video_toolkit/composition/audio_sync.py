"""Audio synchronization utilities."""

from dataclasses import dataclass
from typing import Any, Literal, Optional, TYPE_CHECKING

import numpy as np
from moviepy import AudioClip, concatenate_audioclips, concatenate_videoclips

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


SyncStrategy = Literal["extend_video", "extend_audio", "truncate", "speed_adjust"]
OverflowPolicy = Literal["extend_video", "truncate", "error"]


class NarrationOverflowError(ValueError):
    """Raised when narration cannot fit an authored scene duration."""


@dataclass(frozen=True)
class NarrationTiming:
    """Measured narration timing for one visual segment."""

    video_duration: float
    narration_duration: float
    padding_start: float = 0.0
    padding_end: float = 0.0
    segment_id: Optional[str] = None

    @property
    def padded_audio_duration(self) -> float:
        return self.padding_start + self.narration_duration + self.padding_end

    @property
    def overflow_seconds(self) -> float:
        return max(0.0, self.padded_audio_duration - self.video_duration)

    @property
    def fits(self) -> bool:
        return self.overflow_seconds <= 1e-6


@dataclass
class AudioSync:
    """Handles audio/video duration synchronization."""

    strategy: SyncStrategy = "extend_video"
    padding_start: float = 0.0
    padding_end: float = 0.5
    speed_tolerance: float = 0.1
    overflow_policy: OverflowPolicy = "extend_video"

    def timing(
        self,
        video: float,
        audio: float,
        segment_id: Optional[str] = None,
    ) -> NarrationTiming:
        """Return a reusable fit report without modifying either clip."""
        return NarrationTiming(
            video_duration=video,
            narration_duration=audio,
            padding_start=self.padding_start,
            padding_end=self.padding_end,
            segment_id=segment_id,
        )

    def assert_fits(
        self,
        video: float,
        audio: float,
        segment_id: Optional[str] = None,
    ) -> NarrationTiming:
        """Raise a descriptive error when narration exceeds the visual slot."""
        timing = self.timing(video, audio, segment_id)
        if not timing.fits:
            label = f"Segment '{segment_id}'" if segment_id else "Narration"
            raise NarrationOverflowError(
                f"{label} exceeds its visual duration by "
                f"{timing.overflow_seconds:.2f}s "
                f"({timing.padded_audio_duration:.2f}s audio including padding "
                f"for {video:.2f}s video). Shorten the script, lengthen the "
                "scene, or use overflow_policy='extend_video'."
            )
        return timing

    def calculate_duration(self, video: float, audio: float) -> float:
        """Calculate the final duration based on strategy."""
        timing = self.timing(video, audio)
        total_audio = timing.padded_audio_duration

        if self.strategy == "extend_video":
            return max(video, total_audio)
        elif self.strategy == "extend_audio":
            if timing.fits:
                return video
            if self.overflow_policy == "extend_video":
                return total_audio
            if self.overflow_policy == "error":
                self.assert_fits(video, audio)
            return video
        elif self.strategy == "truncate":
            return min(video, total_audio)
        elif self.strategy == "speed_adjust":
            return video
        else:
            return max(video, total_audio)

    def sync_clips(
        self,
        video_clip: Any,
        audio_clip: Any,
        config: "ProjectConfig",
    ) -> Any:
        """Synchronize video and audio clips."""
        audio_duration = audio_clip.duration + self.padding_start + self.padding_end

        if self.strategy == "extend_video":
            target_duration = max(video_clip.duration, audio_duration)
            return self._extend_video(video_clip, audio_clip, target_duration)
        elif self.strategy == "extend_audio":
            timing = self.timing(video_clip.duration, audio_clip.duration)
            if not timing.fits:
                if self.overflow_policy == "error":
                    self.assert_fits(video_clip.duration, audio_clip.duration)
                if self.overflow_policy == "extend_video":
                    return self._extend_video(
                        video_clip, audio_clip, timing.padded_audio_duration
                    )
                # Explicit truncation is the only policy that may cut speech.
                padded_audio = self._pad_audio(audio_clip)
                return video_clip.with_audio(
                    padded_audio.with_duration(video_clip.duration)
                )
            return self._extend_audio(video_clip, audio_clip, video_clip.duration)
        elif self.strategy == "truncate":
            return self._truncate(video_clip, audio_clip)
        elif self.strategy == "speed_adjust":
            return self._speed_adjust(video_clip, audio_clip, video_clip.duration)
        else:
            return self._extend_video(video_clip, audio_clip, audio_duration)

    def _extend_video(
        self,
        video_clip: Any,
        audio_clip: Any,
        target_duration: float,
    ) -> Any:
        """Extend video by freezing last frame."""
        if video_clip.duration < target_duration:
            freeze_duration = target_duration - video_clip.duration
            last_frame = video_clip.to_ImageClip(t=video_clip.duration - 0.01)
            last_frame = last_frame.with_duration(freeze_duration)

            video_clip = concatenate_videoclips([video_clip, last_frame])

        video_clip = video_clip.with_duration(target_duration)

        audio_clip = self._pad_audio(audio_clip, target_duration=target_duration)

        return video_clip.with_audio(audio_clip)

    def _extend_audio(
        self,
        video_clip: Any,
        audio_clip: Any,
        target_duration: float,
    ) -> Any:
        """Extend audio with silence."""
        audio_clip = self._pad_audio(audio_clip, target_duration=target_duration)
        video_clip = video_clip.with_duration(target_duration)
        return video_clip.with_audio(audio_clip)

    def _truncate(self, video_clip: Any, audio_clip: Any) -> Any:
        """Truncate to shorter duration."""
        audio_with_padding = self._pad_audio(audio_clip)
        target = min(video_clip.duration, audio_with_padding.duration)

        video_clip = video_clip.with_duration(target)
        audio_clip = audio_with_padding.with_duration(target)

        return video_clip.with_audio(audio_clip)

    def _speed_adjust(
        self,
        video_clip: Any,
        audio_clip: Any,
        target_duration: float,
    ) -> Any:
        """Adjust audio speed to match video."""
        audio_with_padding = self._pad_audio(audio_clip)
        speed_factor = audio_with_padding.duration / target_duration

        if abs(speed_factor - 1.0) > self.speed_tolerance:
            return self._extend_video(video_clip, audio_clip, audio_with_padding.duration)

        audio_clip = audio_with_padding.with_effects([
            lambda gf, t: gf(t * speed_factor)
        ])
        audio_clip = audio_clip.with_duration(target_duration)

        video_clip = video_clip.with_duration(target_duration)
        return video_clip.with_audio(audio_clip)

    def _make_silence(self, duration: float, audio_clip: Any) -> Any:
        """Create silence matching the narration's channels and sample rate."""
        channels = max(1, int(getattr(audio_clip, "nchannels", 2)))
        fps = int(getattr(audio_clip, "fps", 44100) or 44100)

        def make_frame(t):
            if isinstance(t, np.ndarray):
                if channels == 1:
                    return np.zeros(len(t))
                return np.zeros((len(t), channels))
            if channels == 1:
                return 0.0
            return np.zeros(channels)

        return AudioClip(make_frame, duration=duration, fps=fps)

    def _pad_audio(
        self,
        audio_clip: Any,
        target_duration: Optional[float] = None,
    ) -> Any:
        """Pad narration and, when requested, fill the complete visual slot."""
        clips = []

        if self.padding_start > 0:
            clips.append(self._make_silence(self.padding_start, audio_clip))

        clips.append(audio_clip)

        trailing_silence = self.padding_end
        padded_duration = self.padding_start + audio_clip.duration + trailing_silence
        if target_duration is not None and target_duration > padded_duration:
            trailing_silence += target_duration - padded_duration

        if trailing_silence > 0:
            clips.append(self._make_silence(trailing_silence, audio_clip))

        if len(clips) > 1:
            padded = concatenate_audioclips(clips)
            if target_duration is not None:
                padded = padded.with_duration(target_duration)
            return padded
        return audio_clip
