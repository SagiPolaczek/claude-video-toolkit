"""
ElevenLabs TTS engine implementation.
"""

import os
from pathlib import Path

from .base import TTSEngine


class ElevenLabsTTSEngine(TTSEngine):
    """Cloud-based ElevenLabs TTS engine."""

    # Default voice IDs
    VOICES = {
        "rachel": "21m00Tcm4TlvDq8ikWAM",
        "adam": "pNInz6obpgDQGcFmaJgB",
        "bella": "EXAVITQu4vr4xnSDxMaL",
    }

    def __init__(
        self,
        api_key: str = None,
        voice_id: str = None,
        model_id: str = "eleven_monolingual_v1",
        cache_dir: str = "./tts_cache",
    ):
        super().__init__(cache_dir)

        # Get API key from parameter, env, or .env file
        self.api_key = api_key or self._load_api_key()
        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key required. Set ELEVENLABS_API_KEY env var "
                "or pass api_key parameter."
            )

        self.voice_id = voice_id or self.VOICES["rachel"]
        self.model_id = model_id
        self._client = None

    def _load_api_key(self) -> str:
        """Load API key from environment or .env file."""
        key = os.environ.get("ELEVENLABS_API_KEY")
        if key:
            return key

        # Try loading from .env
        env_path = Path(".env")
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("ELEVENLABS_API_KEY="):
                    return line.split("=", 1)[1].strip()

        return None

    def _get_client(self):
        """Lazy-load the ElevenLabs client."""
        if self._client is None:
            try:
                from elevenlabs.client import ElevenLabs
            except ImportError:
                raise ImportError(
                    "ElevenLabs not installed. Install with: pip install elevenlabs"
                )
            self._client = ElevenLabs(api_key=self.api_key)
        return self._client

    def synthesize(self, text: str, output_path: str) -> str:
        client = self._get_client()

        # Generate audio
        audio_generator = client.text_to_speech.convert(
            voice_id=self.voice_id,
            text=text,
            model_id=self.model_id,
        )

        # Save to file
        output_path = Path(output_path)

        # ElevenLabs returns MP3, convert to WAV if needed
        if output_path.suffix.lower() == ".wav":
            mp3_path = output_path.with_suffix(".mp3")
            with open(mp3_path, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)

            # Convert MP3 to WAV
            self._convert_to_wav(str(mp3_path), str(output_path))
            mp3_path.unlink()
        else:
            with open(output_path, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)

        return str(output_path)

    def _convert_to_wav(self, mp3_path: str, wav_path: str):
        """Convert MP3 to WAV using pydub or ffmpeg."""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(mp3_path)
            audio.export(wav_path, format="wav")
        except ImportError:
            import subprocess
            subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path, wav_path],
                capture_output=True,
                check=True,
            )

    def get_name(self) -> str:
        return "elevenlabs"

    def get_voice(self) -> str:
        return self.voice_id

    def get_cache_params(self) -> dict:
        return {"model_id": self.model_id}
