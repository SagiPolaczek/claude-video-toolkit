"""Soprano TTS engine implementation."""

import sys
from pathlib import Path

import torch
from soprano import SopranoTTS

from .base import TTSEngine


class SopranoTTSEngine(TTSEngine):
    """Local Soprano TTS engine (~80M params, fast inference)."""

    def __init__(
        self,
        backend: str = "auto",
        cache_dir: str = "./tts_cache",
        use_submodule: bool = False,
    ):
        """
        Initialize Soprano TTS engine.

        Args:
            backend: Device backend ('auto', 'cuda', 'cpu')
            cache_dir: Directory for caching synthesized audio
            use_submodule: If True, use external/soprano submodule
        """
        super().__init__(cache_dir)
        self.backend = backend
        self.use_submodule = use_submodule
        self._model = None

    def _setup_submodule_path(self):
        """Add submodule to Python path if using it."""
        if self.use_submodule:
            submodule_path = Path(__file__).parent.parent.parent / "external" / "soprano"
            if submodule_path.exists():
                path_str = str(submodule_path)
                if path_str not in sys.path:
                    sys.path.insert(0, path_str)
            else:
                raise RuntimeError(
                    "Soprano submodule not found. Run: git submodule update --init"
                )

    def _get_model(self):
        """Lazy-load the Soprano model."""
        if self._model is None:
            self._setup_submodule_path()

            if self.backend == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self._model = SopranoTTS(device=device)
            else:
                self._model = SopranoTTS(device=self.backend)

        return self._model

    def synthesize(self, text: str, output_path: str) -> str:
        model = self._get_model()
        model.infer(text, out_path=output_path)
        return output_path

    def get_name(self) -> str:
        return "soprano"

    def get_voice(self) -> str:
        return "default"

    def get_cache_params(self) -> dict:
        return {"backend": self.backend}
