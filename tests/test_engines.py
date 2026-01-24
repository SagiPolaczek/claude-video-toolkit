"""
Tests for TTS engines module.
"""

import pytest
from pathlib import Path


class TestTTSEngine:
    """Tests for TTSEngine abstract base class."""

    def test_tts_engine_is_abstract(self):
        """TTSEngine should be abstract."""
        from video_toolkit.tts_engines import TTSEngine

        with pytest.raises(TypeError):
            TTSEngine()

    def test_tts_engine_requires_synthesize(self):
        """TTSEngine subclasses must implement synthesize."""
        from video_toolkit.tts_engines import TTSEngine

        class Incomplete(TTSEngine):
            def get_name(self):
                return "incomplete"

            def get_voice(self):
                return "default"

        with pytest.raises(TypeError):
            Incomplete()


class TestDummyEngine:
    """Tests for DummyTTSEngine."""

    def test_dummy_engine_creation(self, temp_dir):
        """DummyTTSEngine should be creatable."""
        from video_toolkit.tts_engines import DummyTTSEngine

        engine = DummyTTSEngine(cache_dir=str(temp_dir / "tts"))
        assert engine.get_name() == "dummy"
        assert engine.get_voice() == "none"

    def test_dummy_engine_synthesize(self, temp_dir):
        """DummyTTSEngine should create empty WAV file."""
        from video_toolkit.tts_engines import DummyTTSEngine

        engine = DummyTTSEngine(cache_dir=str(temp_dir / "tts"))
        output_path = temp_dir / "output.wav"

        result = engine.synthesize("Hello world", str(output_path))

        assert Path(result).exists()
        assert Path(result).suffix == ".wav"

    def test_dummy_engine_cache_key(self, temp_dir):
        """DummyTTSEngine should generate cache keys."""
        from video_toolkit.tts_engines import DummyTTSEngine

        engine = DummyTTSEngine(cache_dir=str(temp_dir / "tts"))

        key1 = engine.get_cache_key("Hello")
        key2 = engine.get_cache_key("World")
        key3 = engine.get_cache_key("Hello")

        assert key1 != key2
        assert key1 == key3
        assert len(key1) == 16

    def test_dummy_engine_cached_synthesis(self, temp_dir):
        """DummyTTSEngine should cache synthesized audio."""
        from video_toolkit.tts_engines import DummyTTSEngine

        engine = DummyTTSEngine(cache_dir=str(temp_dir / "tts"))

        # First call should create file
        path1 = engine.synthesize_cached("Test text")

        # Second call should return cached
        path2 = engine.synthesize_cached("Test text")

        assert path1 == path2
        assert Path(path1).exists()


class TestEngineFactory:
    """Tests for engine factory function."""

    def test_get_engine_dummy(self, temp_dir):
        """get_engine should return DummyTTSEngine for 'dummy'."""
        from video_toolkit.tts_engines import get_engine

        engine = get_engine("dummy", cache_dir=str(temp_dir / "tts"))
        assert engine.get_name() == "dummy"

    def test_get_engine_invalid(self):
        """get_engine should raise for unknown engine."""
        from video_toolkit.tts_engines import get_engine

        with pytest.raises(ValueError):
            get_engine("nonexistent")


class TestEngineCacheKey:
    """Tests for engine cache key generation."""

    def test_cache_key_includes_text(self, temp_dir):
        """Cache key should include text content."""
        from video_toolkit.tts_engines import DummyTTSEngine

        engine = DummyTTSEngine(cache_dir=str(temp_dir / "tts"))

        key1 = engine.get_cache_key("Text A")
        key2 = engine.get_cache_key("Text B")

        assert key1 != key2

    def test_cache_key_deterministic(self, temp_dir):
        """Cache key should be deterministic."""
        from video_toolkit.tts_engines import DummyTTSEngine

        engine = DummyTTSEngine(cache_dir=str(temp_dir / "tts"))

        key1 = engine.get_cache_key("Same text")
        key2 = engine.get_cache_key("Same text")

        assert key1 == key2

    def test_cache_key_hex_format(self, temp_dir):
        """Cache key should be valid hex."""
        from video_toolkit.tts_engines import DummyTTSEngine

        engine = DummyTTSEngine(cache_dir=str(temp_dir / "tts"))
        key = engine.get_cache_key("Test")

        # Should be valid hex
        int(key, 16)


class TestEngineInterface:
    """Tests for engine interface consistency."""

    def test_all_engines_have_required_methods(self, temp_dir):
        """All engines should implement required interface."""
        from video_toolkit.tts_engines import DummyTTSEngine

        engines = [
            DummyTTSEngine(cache_dir=str(temp_dir / "tts")),
        ]

        for engine in engines:
            assert hasattr(engine, "synthesize")
            assert hasattr(engine, "synthesize_cached")
            assert hasattr(engine, "get_name")
            assert hasattr(engine, "get_voice")
            assert hasattr(engine, "get_cache_key")
            assert hasattr(engine, "is_cached")
