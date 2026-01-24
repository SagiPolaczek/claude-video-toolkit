"""Qwen3-TTS engine implementation."""

import sys
from pathlib import Path

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

from .base import TTSEngine


# Available speakers for CustomVoice models
SPEAKERS = {
    "Vivian": {"language": "Chinese", "description": "Bright, slightly edgy young female voice"},
    "Serena": {"language": "Chinese", "description": "Warm, gentle young female voice"},
    "Uncle_Fu": {"language": "Chinese", "description": "Seasoned male voice with a low, mellow timbre"},
    "Dylan": {"language": "Chinese", "description": "Youthful Beijing male voice"},
    "Eric": {"language": "Chinese", "description": "Lively Chengdu male voice"},
    "Ryan": {"language": "English", "description": "Dynamic male voice with strong rhythmic drive"},
    "Aiden": {"language": "English", "description": "Sunny American male voice"},
    "Ono_Anna": {"language": "Japanese", "description": "Playful Japanese female voice"},
    "Sohee": {"language": "Korean", "description": "Warm Korean female voice"},
}

# Model variants
MODEL_VARIANTS = {
    "0.6b": "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
    "1.7b": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    "1.7b-design": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    "1.7b-base": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
}

# Dtype mapping
DTYPE_MAP = {
    "float16": torch.float16,
    "bfloat16": torch.bfloat16,
    "float32": torch.float32,
}


class Qwen3TTSEngine(TTSEngine):
    """
    Qwen3-TTS engine for high-quality text-to-speech.

    Uses the Qwen3-TTS model series for multi-language TTS with
    voice cloning and design capabilities.
    """

    def __init__(
        self,
        model_variant: str = "0.6b",
        model_path: str | None = None,
        device: str = "auto",
        speaker: str = "Ryan",
        language: str = "Auto",
        instruct: str = "",
        cache_dir: str = "./tts_cache",
        use_submodule: bool = False,
        dtype: str = "bfloat16",
    ):
        """
        Initialize Qwen3-TTS engine.

        Args:
            model_variant: Model variant ('0.6b', '1.7b', '1.7b-design', '1.7b-base')
            model_path: Override path to model weights (uses HF download if None)
            device: Device to use ('auto', 'cuda', 'cpu', 'mps', 'cuda:0', etc.)
            speaker: Speaker name (see SPEAKERS dict for options)
            language: Language ('Auto', 'Chinese', 'English', 'Japanese', 'Korean', etc.)
            instruct: Optional instruction for voice style (e.g., "Speak happily")
            cache_dir: Directory for caching synthesized audio
            use_submodule: If True, use external/qwen3-tts submodule
            dtype: Model dtype ('float16', 'bfloat16', 'float32')
        """
        super().__init__(cache_dir)
        self.model_variant = model_variant
        self.model_path = model_path or MODEL_VARIANTS.get(model_variant, model_variant)
        self.device = device
        self.speaker = speaker
        self.language = language
        self.instruct = instruct
        self.use_submodule = use_submodule
        self.dtype = dtype
        self._model = None

    def _setup_submodule_path(self):
        """Add submodule to Python path if using it."""
        if self.use_submodule:
            submodule_path = Path(__file__).parent.parent.parent / "external" / "qwen3-tts"
            if submodule_path.exists():
                path_str = str(submodule_path)
                if path_str not in sys.path:
                    sys.path.insert(0, path_str)
            else:
                raise RuntimeError(
                    "Qwen3-TTS submodule not found. Run: git submodule update --init"
                )

    def _get_device(self) -> str:
        """Determine the device to use."""
        if self.device != "auto":
            return self.device

        if torch.cuda.is_available():
            return "cuda:0"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _get_dtype(self):
        """Get the torch dtype."""
        return DTYPE_MAP.get(self.dtype, torch.bfloat16)

    def _get_model(self):
        """Lazy-load the Qwen3-TTS model."""
        if self._model is not None:
            return self._model

        self._setup_submodule_path()

        device = self._get_device()
        dtype = self._get_dtype()

        print(f"Loading Qwen3-TTS model '{self.model_path}' on {device}...")

        load_kwargs = {
            "device_map": device,
            "torch_dtype": dtype,
        }

        self._model = Qwen3TTSModel.from_pretrained(self.model_path, **load_kwargs)

        return self._model

    def synthesize(self, text: str, output_path: str) -> str:
        """
        Synthesize speech from text using Qwen3-TTS.

        Args:
            text: Text to synthesize
            output_path: Path to save the audio file

        Returns:
            Path to the generated audio file
        """
        model = self._get_model()

        wavs, sr = model.generate_custom_voice(
            text=text,
            language=self.language,
            speaker=self.speaker,
            instruct=self.instruct if self.instruct else None,
        )

        sf.write(output_path, wavs[0], sr)

        return output_path

    def get_name(self) -> str:
        return "qwen3"

    def get_voice(self) -> str:
        return self.speaker

    def get_cache_params(self) -> dict:
        return {
            "model": self.model_variant,
            "speaker": self.speaker,
            "language": self.language,
            "instruct": self.instruct,
        }

    @classmethod
    def list_speakers(cls) -> dict:
        """Return available speakers and their descriptions."""
        return SPEAKERS.copy()

    @classmethod
    def list_models(cls) -> dict:
        """Return available model variants."""
        return MODEL_VARIANTS.copy()
