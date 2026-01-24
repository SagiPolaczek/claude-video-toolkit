"""
Tests for content sources module.
"""

import hashlib
import pytest
from pathlib import Path


class TestContentSource:
    """Tests for ContentSource abstract base class."""

    def test_content_source_is_abstract(self):
        """ContentSource should be abstract and not directly instantiable."""
        from video_toolkit.sources import ContentSource

        with pytest.raises(TypeError):
            ContentSource()

    def test_content_source_requires_get_clip(self):
        """ContentSource subclasses must implement get_clip."""
        from video_toolkit.sources import ContentSource

        # Incomplete subclass without get_clip
        class Incomplete(ContentSource):
            def cache_key(self):
                return "key"

        with pytest.raises(TypeError):
            Incomplete()

    def test_content_source_requires_cache_key(self):
        """ContentSource subclasses must implement cache_key."""
        from video_toolkit.sources import ContentSource

        class Incomplete(ContentSource):
            def get_clip(self, config):
                return None

        with pytest.raises(TypeError):
            Incomplete()


class TestAsset:
    """Tests for Asset content source."""

    def test_asset_creation(self):
        """Asset should be creatable with a path."""
        from video_toolkit.sources import Asset

        asset = Asset("./videos/test.mp4")
        assert asset.path == Path("./videos/test.mp4")

    def test_asset_path_normalization(self):
        """Asset should normalize paths."""
        from video_toolkit.sources import Asset

        asset = Asset(Path("./videos/test.mp4"))
        assert isinstance(asset.path, Path)

    def test_asset_cache_key_based_on_path(self):
        """Asset cache key should be based on file path."""
        from video_toolkit.sources import Asset

        asset1 = Asset("./video1.mp4")
        asset2 = Asset("./video2.mp4")
        asset3 = Asset("./video1.mp4")

        assert asset1.cache_key() != asset2.cache_key()
        assert asset1.cache_key() == asset3.cache_key()

    def test_asset_cache_key_is_deterministic(self):
        """Asset cache key should be deterministic."""
        from video_toolkit.sources import Asset

        asset = Asset("./test.mp4")
        key1 = asset.cache_key()
        key2 = asset.cache_key()

        assert key1 == key2

    def test_asset_str_representation(self):
        """Asset should have meaningful string representation."""
        from video_toolkit.sources import Asset

        asset = Asset("./test.mp4")
        assert "test.mp4" in str(asset)


class TestPlaceholder:
    """Tests for Placeholder content source."""

    def test_placeholder_creation(self):
        """Placeholder should be creatable with text and duration."""
        from video_toolkit.sources import Placeholder

        placeholder = Placeholder("Test Content", duration=5.0)
        assert placeholder.text == "Test Content"
        assert placeholder.duration == 5.0

    def test_placeholder_default_duration(self):
        """Placeholder should have default duration."""
        from video_toolkit.sources import Placeholder

        placeholder = Placeholder("Test")
        assert placeholder.duration > 0

    def test_placeholder_cache_key(self):
        """Placeholder cache key should include text."""
        from video_toolkit.sources import Placeholder

        p1 = Placeholder("Text A")
        p2 = Placeholder("Text B")
        p3 = Placeholder("Text A")

        assert p1.cache_key() != p2.cache_key()
        assert p1.cache_key() == p3.cache_key()

    def test_placeholder_cache_key_includes_duration(self):
        """Placeholder cache key should differ with different durations."""
        from video_toolkit.sources import Placeholder

        p1 = Placeholder("Text", duration=3.0)
        p2 = Placeholder("Text", duration=5.0)

        assert p1.cache_key() != p2.cache_key()


class TestGenerator:
    """Tests for Generator abstract base class."""

    def test_generator_is_abstract(self):
        """Generator should be abstract."""
        from video_toolkit.sources.generators import Generator

        with pytest.raises(TypeError):
            Generator(key="test")

    def test_generator_requires_generate(self):
        """Generator subclasses must implement generate."""
        from video_toolkit.sources.generators import Generator

        class Incomplete(Generator):
            pass

        with pytest.raises(TypeError):
            Incomplete(key="test")


class TestFunctionGenerator:
    """Tests for FunctionGenerator."""

    def test_function_generator_creation(self):
        """FunctionGenerator should accept function and key."""
        from video_toolkit.sources.generators import FunctionGenerator

        def my_render(output_path, config):
            return output_path

        gen = FunctionGenerator(my_render, key="my_render_v1")
        assert gen.func == my_render
        assert gen.key == "my_render_v1"

    def test_function_generator_kwargs(self):
        """FunctionGenerator should store additional kwargs."""
        from video_toolkit.sources.generators import FunctionGenerator

        def render(output_path, config, color="red", size=100):
            return output_path

        gen = FunctionGenerator(render, key="test", color="blue", size=200)
        assert gen.kwargs == {"color": "blue", "size": 200}

    def test_function_generator_cache_key_includes_kwargs(self):
        """FunctionGenerator cache key should include kwargs."""
        from video_toolkit.sources.generators import FunctionGenerator

        def render(output_path, config, value=0):
            return output_path

        gen1 = FunctionGenerator(render, key="test", value=1)
        gen2 = FunctionGenerator(render, key="test", value=2)
        gen3 = FunctionGenerator(render, key="test", value=1)

        assert gen1.cache_key() != gen2.cache_key()
        assert gen1.cache_key() == gen3.cache_key()

    def test_function_generator_cache_key_includes_key(self):
        """FunctionGenerator cache key should include the key parameter."""
        from video_toolkit.sources.generators import FunctionGenerator

        def render(output_path, config):
            return output_path

        gen1 = FunctionGenerator(render, key="v1")
        gen2 = FunctionGenerator(render, key="v2")

        assert gen1.cache_key() != gen2.cache_key()

    def test_function_generator_call(self, temp_dir):
        """FunctionGenerator.generate should call function with correct args."""
        from video_toolkit.sources.generators import FunctionGenerator
        from video_toolkit.config import ProjectConfig

        calls = []

        def capture_render(output_path, config, extra="default"):
            calls.append((output_path, config, extra))
            # Create the output file
            Path(output_path).touch()
            return output_path

        gen = FunctionGenerator(capture_render, key="test", extra="custom")
        config = ProjectConfig()
        output_path = temp_dir / "output.mp4"

        gen.generate(output_path, config)

        assert len(calls) == 1
        assert calls[0][0] == output_path
        assert calls[0][1] == config
        assert calls[0][2] == "custom"


class TestScriptGenerator:
    """Tests for ScriptGenerator."""

    def test_script_generator_creation(self):
        """ScriptGenerator should accept command and key."""
        from video_toolkit.sources.generators import ScriptGenerator

        gen = ScriptGenerator(
            command="python render.py {output_path}",
            key="render_v1"
        )
        assert "python render.py" in gen.command
        assert gen.key == "render_v1"

    def test_script_generator_command_template(self):
        """ScriptGenerator command should support template variables."""
        from video_toolkit.sources.generators import ScriptGenerator

        gen = ScriptGenerator(
            command="ffmpeg -i {input} -o {output_path}",
            key="ffmpeg_convert",
            input="source.mp4"
        )
        assert gen.kwargs["input"] == "source.mp4"

    def test_script_generator_cache_key(self):
        """ScriptGenerator cache key should include command and key."""
        from video_toolkit.sources.generators import ScriptGenerator

        gen1 = ScriptGenerator(command="cmd1", key="v1")
        gen2 = ScriptGenerator(command="cmd1", key="v2")
        gen3 = ScriptGenerator(command="cmd2", key="v1")

        assert gen1.cache_key() != gen2.cache_key()
        assert gen1.cache_key() != gen3.cache_key()


class TestCacheKeyGeneration:
    """Tests for cache key generation utilities."""

    def test_cache_key_length(self):
        """Cache keys should have consistent length."""
        from video_toolkit.sources import Asset, Placeholder

        asset = Asset("./test.mp4")
        placeholder = Placeholder("Test")

        # Cache keys should be hex strings of consistent length
        assert len(asset.cache_key()) == 16
        assert len(placeholder.cache_key()) == 16

    def test_cache_key_hex_format(self):
        """Cache keys should be valid hex strings."""
        from video_toolkit.sources import Asset

        asset = Asset("./test.mp4")
        key = asset.cache_key()

        # Should be valid hex
        int(key, 16)  # Raises ValueError if not valid hex
