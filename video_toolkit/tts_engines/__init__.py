"""TTS Engine implementations."""

from .base import TTSEngine, DummyTTSEngine
from .soprano import SopranoTTSEngine
from .qwen3 import Qwen3TTSEngine
from .elevenlabs import ElevenLabsTTSEngine

__all__ = [
    "TTSEngine",
    "DummyTTSEngine",
    "SopranoTTSEngine",
    "Qwen3TTSEngine",
    "ElevenLabsTTSEngine",
    "get_engine",
]

_ENGINES = {
    "dummy": DummyTTSEngine,
    "soprano": SopranoTTSEngine,
    "qwen3": Qwen3TTSEngine,
    "elevenlabs": ElevenLabsTTSEngine,
}


def get_engine(name: str, **kwargs) -> TTSEngine:
    """Get a TTS engine by name."""
    if name not in _ENGINES:
        raise ValueError(f"Unknown engine '{name}'. Available: {', '.join(_ENGINES.keys())}")
    return _ENGINES[name](**kwargs)
