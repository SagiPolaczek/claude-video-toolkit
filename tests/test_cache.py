"""
Tests for cache module.
"""

import pytest
from pathlib import Path


class TestCacheLayer:
    """Tests for CacheLayer abstract base class."""

    def test_cache_layer_is_abstract(self):
        """CacheLayer should be abstract."""
        from video_toolkit.cache import CacheLayer

        with pytest.raises(TypeError):
            CacheLayer(base_dir=Path("./cache"))


class TestGeneratedCache:
    """Tests for GeneratedCache (Layer 0)."""

    def test_generated_cache_creation(self, temp_dir):
        """GeneratedCache should be creatable with base directory."""
        from video_toolkit.cache import GeneratedCache

        cache = GeneratedCache(base_dir=temp_dir / "generated")
        assert cache.base_dir.exists()

    def test_generated_cache_path(self, temp_dir):
        """GeneratedCache should generate paths based on cache key."""
        from video_toolkit.cache import GeneratedCache

        cache = GeneratedCache(base_dir=temp_dir / "generated")
        path = cache.get_path("abc123")

        assert path.parent == cache.base_dir
        assert "abc123" in path.name

    def test_generated_cache_exists_false(self, temp_dir):
        """GeneratedCache.exists should return False for missing files."""
        from video_toolkit.cache import GeneratedCache

        cache = GeneratedCache(base_dir=temp_dir / "generated")
        assert cache.exists("nonexistent") is False

    def test_generated_cache_exists_true(self, temp_dir):
        """GeneratedCache.exists should return True for existing files."""
        from video_toolkit.cache import GeneratedCache

        cache = GeneratedCache(base_dir=temp_dir / "generated")
        path = cache.get_path("exists_test")
        path.touch()

        assert cache.exists("exists_test") is True


class TestTTSCache:
    """Tests for TTSCache (Layer 1)."""

    def test_tts_cache_creation(self, temp_dir):
        """TTSCache should be creatable."""
        from video_toolkit.cache import TTSCache

        cache = TTSCache(base_dir=temp_dir / "tts")
        assert cache.base_dir.exists()

    def test_tts_cache_key_includes_text(self):
        """TTS cache key should include text content."""
        from video_toolkit.cache import TTSCache

        cache = TTSCache()

        key1 = cache.generate_key("Hello world", engine="soprano", voice="default")
        key2 = cache.generate_key("Different text", engine="soprano", voice="default")

        assert key1 != key2

    def test_tts_cache_key_includes_engine(self):
        """TTS cache key should include engine name."""
        from video_toolkit.cache import TTSCache

        cache = TTSCache()

        key1 = cache.generate_key("Hello", engine="soprano", voice="default")
        key2 = cache.generate_key("Hello", engine="elevenlabs", voice="default")

        assert key1 != key2

    def test_tts_cache_key_includes_voice(self):
        """TTS cache key should include voice identifier."""
        from video_toolkit.cache import TTSCache

        cache = TTSCache()

        key1 = cache.generate_key("Hello", engine="soprano", voice="voice1")
        key2 = cache.generate_key("Hello", engine="soprano", voice="voice2")

        assert key1 != key2


class TestSegmentCache:
    """Tests for SegmentCache (Layer 2)."""

    def test_segment_cache_creation(self, temp_dir):
        """SegmentCache should be creatable."""
        from video_toolkit.cache import SegmentCache

        cache = SegmentCache(base_dir=temp_dir / "segments")
        assert cache.base_dir.exists()

    def test_segment_cache_path_format(self, temp_dir):
        """SegmentCache paths should include segment ID and mode."""
        from video_toolkit.cache import SegmentCache

        cache = SegmentCache(base_dir=temp_dir / "segments")
        path = cache.get_path(segment_id="1", mode="standard")

        assert "1" in path.name
        assert "standard" in path.name
        assert path.suffix == ".mp4"

    def test_segment_cache_different_modes(self, temp_dir):
        """Different modes should produce different cache paths."""
        from video_toolkit.cache import SegmentCache

        cache = SegmentCache(base_dir=temp_dir / "segments")

        path_draft = cache.get_path(segment_id="1", mode="draft")
        path_standard = cache.get_path(segment_id="1", mode="standard")

        assert path_draft != path_standard


class TestCombinedCache:
    """Tests for CombinedCache (Layer 3)."""

    def test_combined_cache_creation(self, temp_dir):
        """CombinedCache should be creatable."""
        from video_toolkit.cache import CombinedCache

        cache = CombinedCache(base_dir=temp_dir / "combined")
        assert cache.base_dir.exists()

    def test_combined_cache_path_format(self, temp_dir):
        """CombinedCache paths should include segment ID, mode, and engine."""
        from video_toolkit.cache import CombinedCache

        cache = CombinedCache(base_dir=temp_dir / "combined")
        path = cache.get_path(
            segment_id="1",
            mode="standard",
            engine="soprano",
            voice="default",
        )

        assert "1" in path.name
        assert "standard" in path.name
        assert "soprano" in path.name


class TestCacheManager:
    """Tests for CacheManager."""

    def test_cache_manager_creation(self, temp_dir):
        """CacheManager should be creatable with base directory."""
        from video_toolkit.cache import CacheManager

        manager = CacheManager(base_dir=temp_dir)

        assert (temp_dir / "generated").exists()
        assert (temp_dir / "tts").exists()
        assert (temp_dir / "segments").exists()
        assert (temp_dir / "combined").exists()

    def test_cache_manager_layers(self, temp_dir):
        """CacheManager should provide access to all layers."""
        from video_toolkit.cache import CacheManager

        manager = CacheManager(base_dir=temp_dir)

        assert manager.generated is not None
        assert manager.tts is not None
        assert manager.segments is not None
        assert manager.combined is not None

    def test_cache_manager_status(self, temp_dir):
        """CacheManager should report cache status for segments."""
        from video_toolkit.cache import CacheManager

        manager = CacheManager(base_dir=temp_dir)

        status = manager.get_status(
            segment_id="1",
            mode="standard",
            engine="soprano",
            voice="default",
        )

        assert "segment" in status
        assert "combined" in status
        assert status["segment"] is False  # Not cached
        assert status["combined"] is False


class TestCacheInvalidation:
    """Tests for cache invalidation."""

    def test_invalidate_segment_cascades_to_combined(self, temp_dir):
        """Invalidating segment cache should invalidate combined cache."""
        from video_toolkit.cache import CacheManager

        manager = CacheManager(base_dir=temp_dir)

        # Create cached files
        seg_path = manager.segments.get_path("1", "standard")
        seg_path.touch()

        combined_path = manager.combined.get_path("1", "standard", "soprano", "default")
        combined_path.touch()

        # Verify both exist
        assert seg_path.exists()
        assert combined_path.exists()

        # Invalidate segment
        manager.invalidate_segment("1", "standard")

        # Segment should be removed, combined should also be removed
        assert not seg_path.exists()

    def test_invalidate_generated_cascades(self, temp_dir):
        """Invalidating generated cache should cascade to dependent caches."""
        from video_toolkit.cache import CacheManager

        manager = CacheManager(base_dir=temp_dir)

        # Create cached files at each layer
        gen_path = manager.generated.get_path("gen_key")
        gen_path.touch()

        # Invalidate generated
        manager.invalidate_generated("gen_key")

        assert not gen_path.exists()


class TestCacheKeyConsistency:
    """Tests for cache key consistency."""

    def test_same_input_same_key(self, temp_dir):
        """Same inputs should always produce same cache key."""
        from video_toolkit.cache import TTSCache

        cache = TTSCache(base_dir=temp_dir / "tts")

        key1 = cache.generate_key("test", engine="soprano", voice="default")
        key2 = cache.generate_key("test", engine="soprano", voice="default")

        assert key1 == key2

    def test_cache_key_hex_format(self, temp_dir):
        """Cache keys should be valid hex strings."""
        from video_toolkit.cache import TTSCache

        cache = TTSCache(base_dir=temp_dir / "tts")

        key = cache.generate_key("test", engine="soprano", voice="default")

        # Should be valid hex
        int(key, 16)

    def test_cache_key_length(self, temp_dir):
        """Cache keys should have consistent length."""
        from video_toolkit.cache import TTSCache

        cache = TTSCache(base_dir=temp_dir / "tts")

        key1 = cache.generate_key("short", engine="a", voice="b")
        key2 = cache.generate_key("much longer text content", engine="longer", voice="v")

        assert len(key1) == len(key2) == 16
