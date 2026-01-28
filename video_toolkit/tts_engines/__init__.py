"""TTS Engine implementations."""

from .base import TTSEngine, DummyTTSEngine

# Lazy imports for engines with heavy/optional dependencies.
# Each engine is imported on first access to avoid requiring all
# TTS backends to be installed.

def __getattr__(name):
    if name == "SopranoTTSEngine":
        from .soprano import SopranoTTSEngine
        return SopranoTTSEngine
    if name == "Qwen3TTSEngine":
        from .qwen3 import Qwen3TTSEngine
        return Qwen3TTSEngine
    if name == "ElevenLabsTTSEngine":
        from .elevenlabs import ElevenLabsTTSEngine
        return ElevenLabsTTSEngine
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "TTSEngine",
    "DummyTTSEngine",
    "SopranoTTSEngine",
    "Qwen3TTSEngine",
    "ElevenLabsTTSEngine",
    "get_engine",
]

_ENGINE_MODULES = {
    "dummy": ("base", "DummyTTSEngine"),
    "soprano": ("soprano", "SopranoTTSEngine"),
    "qwen3": ("qwen3", "Qwen3TTSEngine"),
    "elevenlabs": ("elevenlabs", "ElevenLabsTTSEngine"),
}


def get_engine(name: str, **kwargs) -> TTSEngine:
    """Get a TTS engine by name."""
    if name not in _ENGINE_MODULES:
        raise ValueError(f"Unknown engine '{name}'. Available: {', '.join(_ENGINE_MODULES.keys())}")
    module_name, class_name = _ENGINE_MODULES[name]
    import importlib
    module = importlib.import_module(f".{module_name}", package=__name__)
    cls = getattr(module, class_name)
    return cls(**kwargs)
