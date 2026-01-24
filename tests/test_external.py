"""
Integration tests for external dependencies.

These tests require the external submodules to be initialized:
    git submodule update --init --recursive

Run with: pytest tests/test_external.py -v
Skip in CI: pytest tests/ -m "not slow"
"""

import pytest
from pathlib import Path


@pytest.mark.slow
@pytest.mark.integration
class TestManimGenerator:
    """Integration tests for ManimGenerator."""

    @pytest.fixture
    def sample_manim_scene(self, temp_dir):
        """Create a minimal Manim scene file for testing."""
        scene_file = temp_dir / "test_scene.py"
        scene_file.write_text('''
from manim import *

class TestScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait(0.5)
''')
        return scene_file

    def test_manim_generator_initializes(self, temp_dir, sample_manim_scene):
        """Test ManimGenerator can be initialized."""
        from video_toolkit.sources.generators import ManimGenerator

        generator = ManimGenerator(
            scene_class="TestScene",
            scene_file=sample_manim_scene,
            key="test_scene",
            quality="l",
            cache_dir=temp_dir / "generated",
        )

        assert generator.scene_class == "TestScene"
        assert generator.quality == "l"

    def test_manim_generator_invalid_quality(self, temp_dir, sample_manim_scene):
        """Test ManimGenerator rejects invalid quality settings."""
        from video_toolkit.sources.generators import ManimGenerator

        with pytest.raises(ValueError, match="Invalid quality"):
            ManimGenerator(
                scene_class="TestScene",
                scene_file=sample_manim_scene,
                key="test_scene",
                quality="invalid",
            )

    def test_manim_generates_video(self, temp_dir, sample_manim_scene):
        """Test ManimGenerator produces a video file."""
        pytest.importorskip("manim")

        from video_toolkit.sources.generators import ManimGenerator
        from video_toolkit.config import ProjectConfig, Resolution

        generator = ManimGenerator(
            scene_class="TestScene",
            scene_file=sample_manim_scene,
            key="test_scene",
            quality="l",
            cache_dir=temp_dir / "generated",
        )

        config = ProjectConfig(resolution=Resolution.DRAFT)
        output_path = temp_dir / "output.mp4"

        result = generator.generate(output_path, config)

        assert result.exists()
        assert result.suffix == ".mp4"


@pytest.mark.slow
@pytest.mark.integration
class TestSopranoTTS:
    """Integration tests for SopranoTTSEngine."""

    def test_soprano_initializes(self, temp_dir):
        """Test SopranoTTSEngine can be initialized."""
        from video_toolkit.tts_engines import SopranoTTSEngine

        engine = SopranoTTSEngine(
            backend="cpu",
            cache_dir=str(temp_dir / "tts_cache"),
        )

        assert engine.get_name() == "soprano"
        assert engine.backend == "cpu"

    def test_soprano_with_submodule_flag(self, temp_dir):
        """Test SopranoTTSEngine with submodule flag."""
        from video_toolkit.tts_engines import SopranoTTSEngine

        engine = SopranoTTSEngine(
            backend="cpu",
            cache_dir=str(temp_dir / "tts_cache"),
            use_submodule=True,
        )

        assert engine.use_submodule is True

    def test_soprano_synthesizes(self, temp_dir):
        """Test SopranoTTSEngine produces audio."""
        pytest.importorskip("soprano")

        from video_toolkit.tts_engines import SopranoTTSEngine

        engine = SopranoTTSEngine(
            backend="cpu",
            cache_dir=str(temp_dir / "tts_cache"),
        )

        output_path = temp_dir / "test_audio.wav"
        result = engine.synthesize("Hello, this is a test.", str(output_path))

        assert Path(result).exists()

    def test_soprano_caching(self, temp_dir):
        """Test SopranoTTSEngine caching works."""
        pytest.importorskip("soprano")

        from video_toolkit.tts_engines import SopranoTTSEngine

        engine = SopranoTTSEngine(
            backend="cpu",
            cache_dir=str(temp_dir / "tts_cache"),
        )

        text = "Hello, this is a caching test."

        # First call should cache
        result1 = engine.synthesize_cached(text)
        assert Path(result1).exists()
        assert engine.is_cached(text)

        # Second call should hit cache
        result2 = engine.synthesize_cached(text)
        assert result1 == result2


@pytest.mark.slow
@pytest.mark.integration
class TestQwen3TTS:
    """Integration tests for Qwen3TTSEngine."""

    def test_qwen3_initializes(self, temp_dir):
        """Test Qwen3TTSEngine can be initialized."""
        from video_toolkit.tts_engines import Qwen3TTSEngine

        engine = Qwen3TTSEngine(
            device="cpu",
            cache_dir=str(temp_dir / "tts_cache"),
        )

        assert engine.get_name() == "qwen3"
        assert engine.device == "cpu"

    def test_qwen3_with_submodule_flag(self, temp_dir):
        """Test Qwen3TTSEngine with submodule flag."""
        from video_toolkit.tts_engines import Qwen3TTSEngine

        engine = Qwen3TTSEngine(
            device="cpu",
            cache_dir=str(temp_dir / "tts_cache"),
            use_submodule=True,
        )

        assert engine.use_submodule is True

    def test_qwen3_device_detection(self, temp_dir):
        """Test Qwen3TTSEngine auto device detection."""
        from video_toolkit.tts_engines import Qwen3TTSEngine

        engine = Qwen3TTSEngine(
            device="auto",
            cache_dir=str(temp_dir / "tts_cache"),
        )

        detected = engine._get_device()
        assert detected in ["cuda:0", "mps", "cpu"]

    def test_qwen3_list_speakers(self):
        """Test listing available speakers."""
        from video_toolkit.tts_engines import Qwen3TTSEngine

        speakers = Qwen3TTSEngine.list_speakers()
        assert "Ryan" in speakers
        assert "Vivian" in speakers
        assert speakers["Ryan"]["language"] == "English"

    def test_qwen3_list_models(self):
        """Test listing available model variants."""
        from video_toolkit.tts_engines import Qwen3TTSEngine

        models = Qwen3TTSEngine.list_models()
        assert "0.6b" in models
        assert "1.7b" in models

    def test_qwen3_synthesizes(self, temp_dir):
        """Test Qwen3TTSEngine produces audio."""
        pytest.importorskip("qwen_tts")

        from video_toolkit.tts_engines import Qwen3TTSEngine

        engine = Qwen3TTSEngine(
            model_variant="0.6b",
            device="auto",
            speaker="Ryan",
            language="English",
            cache_dir=str(temp_dir / "tts_cache"),
            dtype="float32",  # Use float32 for CPU/MPS compatibility
        )

        output_path = temp_dir / "test_audio.wav"
        result = engine.synthesize("Hello, this is a test.", str(output_path))

        assert Path(result).exists()
        # Verify it's a valid audio file
        import soundfile as sf
        data, sr = sf.read(result)
        assert len(data) > 0
        assert sr > 0


@pytest.mark.slow
@pytest.mark.integration
class TestEngineFactory:
    """Integration tests for the engine factory function."""

    def test_get_soprano_engine(self, temp_dir):
        """Test getting soprano engine via factory."""
        from video_toolkit.tts_engines import get_engine

        engine = get_engine("soprano", backend="cpu", cache_dir=str(temp_dir))
        assert engine.get_name() == "soprano"

    def test_get_qwen3_engine(self, temp_dir):
        """Test getting qwen3 engine via factory."""
        from video_toolkit.tts_engines import get_engine

        engine = get_engine("qwen3", device="cpu", cache_dir=str(temp_dir))
        assert engine.get_name() == "qwen3"

    def test_get_unknown_engine(self):
        """Test factory raises error for unknown engine."""
        from video_toolkit.tts_engines import get_engine

        with pytest.raises(ValueError, match="Unknown engine"):
            get_engine("nonexistent")
