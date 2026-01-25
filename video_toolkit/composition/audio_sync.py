"""Audio synchronization utilities."""

from dataclasses import dataclass
from typing import Any, Literal, TYPE_CHECKING

from moviepy import CompositeVideoClip, concatenate_videoclips, AudioClip, concatenate_audioclips

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig


SyncStrategy = Literal["extend_video", "extend_audio", "truncate", "speed_adjust"]


@dataclass
class AudioSync:
    """Handles audio/video duration synchronization."""

    strategy: SyncStrategy = "extend_video"
    padding_start: float = 0.0
    padding_end: float = 0.5
    speed_tolerance: float = 0.1

    def calculate_duration(self, video: float, audio: float) -> float:
        """Calculate the final duration based on strategy."""
        total_audio = self.padding_start + audio + self.padding_end

        if self.strategy == "extend_video":
            return max(video, total_audio)
        elif self.strategy == "extend_audio":
            return max(video, total_audio)
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
            return self._extend_video(video_clip, audio_clip, audio_duration)
        elif self.strategy == "extend_audio":
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

        if self.padding_start > 0 or self.padding_end > 0:
            audio_clip = self._pad_audio(audio_clip)

        return video_clip.with_audio(audio_clip)

    def _extend_audio(
        self,
        video_clip: Any,
        audio_clip: Any,
        target_duration: float,
    ) -> Any:
        """Extend audio with silence."""
        audio_clip = self._pad_audio(audio_clip)
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

    def _pad_audio(self, audio_clip: Any) -> Any:
        """Add silence padding to audio."""
        clips = []

        if self.padding_start > 0:
            silence_start = AudioClip(
                lambda t: 0,
                duration=self.padding_start,
            )
            clips.append(silence_start)

        clips.append(audio_clip)

        if self.padding_end > 0:
            silence_end = AudioClip(
                lambda t: 0,
                duration=self.padding_end,
            )
            clips.append(silence_end)

        if len(clips) > 1:
            return concatenate_audioclips(clips)
        return audio_clip
