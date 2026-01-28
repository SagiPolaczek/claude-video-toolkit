"""Unit tests for the Remotion integration (mocked subprocess)."""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestRemotionConfig:
    """Tests for RemotionConfig dataclass."""

    def test_default_config(self):
        from video_toolkit.remotion.config import RemotionConfig

        config = RemotionConfig()
        assert config.node_executable == "node"
        assert config.npm_executable == "npm"
        assert config.concurrency == 1
        assert config.timeout_per_segment == 120
        assert config.log_level == "warn"
        assert config.custom_compositions_dir is None
        assert config.chromium_executable is None

    def test_custom_config(self):
        from video_toolkit.remotion.config import RemotionConfig

        config = RemotionConfig(
            node_executable="/usr/local/bin/node",
            concurrency=4,
            timeout_per_segment=300,
            log_level="verbose",
        )
        assert config.node_executable == "/usr/local/bin/node"
        assert config.concurrency == 4
        assert config.timeout_per_segment == 300


class TestRemotionExceptions:
    """Tests for Remotion exception hierarchy."""

    def test_exception_hierarchy(self):
        from video_toolkit.remotion.exceptions import (
            RemotionError,
            BundleError,
            RenderError,
            DependencyError,
        )

        assert issubclass(BundleError, RemotionError)
        assert issubclass(RenderError, RemotionError)
        assert issubclass(DependencyError, RemotionError)

    def test_exceptions_are_catchable(self):
        from video_toolkit.remotion.exceptions import (
            RemotionError,
            BundleError,
        )

        with pytest.raises(RemotionError):
            raise BundleError("test")


class TestRemotionRenderer:
    """Tests for RemotionRenderer with mocked subprocess."""

    def test_ensure_dependencies_node_missing(self):
        from video_toolkit.remotion.renderer import RemotionRenderer
        from video_toolkit.remotion.exceptions import DependencyError

        renderer = RemotionRenderer()
        with patch("subprocess.run", side_effect=FileNotFoundError):
            with pytest.raises(DependencyError, match="Node.js not found"):
                renderer.ensure_dependencies()

    def test_ensure_dependencies_node_too_old(self):
        from video_toolkit.remotion.renderer import RemotionRenderer
        from video_toolkit.remotion.exceptions import DependencyError

        renderer = RemotionRenderer()
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "v16.0.0\n"

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(DependencyError, match="Node.js >= 18"):
                renderer.ensure_dependencies()

    def test_ensure_dependencies_success(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer
        from video_toolkit.remotion.config import RemotionConfig

        renderer = RemotionRenderer(RemotionConfig())

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "v20.0.0\n"

        # Patch node_modules to exist
        with patch("subprocess.run", return_value=mock_result):
            with patch.object(Path, "exists", return_value=True):
                renderer.ensure_dependencies()
                assert renderer._deps_checked is True

    def test_bundle_returns_serve_url(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer
        from video_toolkit.remotion.config import RemotionConfig

        renderer = RemotionRenderer(RemotionConfig())
        renderer._deps_checked = True

        bundle_output = json.dumps({"serveUrl": "/tmp/bundle_abc123"})
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = bundle_output

        with patch("subprocess.run", return_value=mock_result):
            url = renderer.bundle(force=True)
            assert url == "/tmp/bundle_abc123"

    def test_render_calls_node(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer
        from video_toolkit.remotion.config import RemotionConfig

        renderer = RemotionRenderer(RemotionConfig())
        renderer._deps_checked = True
        renderer._serve_url = "/tmp/bundle"

        output_file = temp_dir / "output.mp4"
        # Create the output file to satisfy the existence check
        output_file.write_bytes(b"fake mp4")

        render_output = json.dumps({"success": True, "outputPath": str(output_file)})
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = render_output

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = renderer.render(
                composition_id="AnimatedTitle",
                input_props={"title": "Hello"},
                output_path=str(output_file),
                duration_in_frames=150,
                width=1920,
                height=1080,
                fps=30,
            )
            assert result.resolve() == output_file.resolve()
            # Verify subprocess was called
            assert mock_run.called

    def test_render_error_on_failure(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer
        from video_toolkit.remotion.exceptions import RenderError

        renderer = RemotionRenderer()
        renderer._deps_checked = True
        renderer._serve_url = "/tmp/bundle"

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Composition not found"

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RenderError, match="Composition not found"):
                renderer.render(
                    composition_id="NonExistent",
                    input_props={},
                    output_path=str(temp_dir / "out.mp4"),
                    duration_in_frames=30,
                    width=1920,
                    height=1080,
                )

    def test_render_timeout(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer
        from video_toolkit.remotion.config import RemotionConfig
        from video_toolkit.remotion.exceptions import RenderError

        renderer = RemotionRenderer(RemotionConfig(timeout_per_segment=1))
        renderer._deps_checked = True
        renderer._serve_url = "/tmp/bundle"

        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired("node", 1),
        ):
            with pytest.raises(RenderError, match="timed out"):
                renderer.render(
                    composition_id="AnimatedTitle",
                    input_props={},
                    output_path=str(temp_dir / "out.mp4"),
                    duration_in_frames=30,
                    width=1920,
                    height=1080,
                )

    def test_resolve_assets_copies_local_files(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer

        renderer = RemotionRenderer()

        # Create a fake local asset
        asset = temp_dir / "teaser.png"
        asset.write_bytes(b"fake png data")

        # Create a fake bundle dir for _resolve_assets
        bundle_dir = temp_dir / "bundle"
        bundle_dir.mkdir()

        props = {"imagePath": str(asset), "title": "Hello"}
        resolved = renderer._resolve_assets(props, str(bundle_dir))

        # imagePath should be rewritten to relative path
        assert resolved["imagePath"] == "assets/teaser.png"
        # title should be unchanged (not a path key)
        assert resolved["title"] == "Hello"

    def test_resolve_assets_ignores_nonexistent(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer

        renderer = RemotionRenderer()
        bundle_dir = temp_dir / "bundle"
        bundle_dir.mkdir()

        props = {"imagePath": "/nonexistent/image.png"}
        resolved = renderer._resolve_assets(props, str(bundle_dir))
        assert resolved["imagePath"] == "/nonexistent/image.png"

    def test_bundle_hash_deterministic(self):
        from video_toolkit.remotion.renderer import RemotionRenderer

        renderer = RemotionRenderer()
        hash1 = renderer._compute_bundle_hash()
        hash2 = renderer._compute_bundle_hash()
        assert hash1 == hash2
        assert len(hash1) == 16


class TestRemotionSegment:
    """Tests for RemotionSegment."""

    def test_remotion_segment_requires_renderer(self):
        from video_toolkit.remotion.segments import RemotionSegment
        from video_toolkit.config import ProjectConfig

        seg = RemotionSegment(
            id="test",
            composition_id="AnimatedTitle",
            input_props={"title": "Hello"},
            duration=3.0,
        )

        config = ProjectConfig()
        with pytest.raises(RuntimeError, match="no renderer"):
            seg.render(config)

    def test_remotion_segment_requires_duration(self):
        from video_toolkit.remotion.segments import RemotionSegment
        from video_toolkit.config import ProjectConfig

        seg = RemotionSegment(
            id="test",
            composition_id="AnimatedTitle",
            renderer=MagicMock(),
        )

        config = ProjectConfig()
        with pytest.raises(ValueError, match="requires explicit duration"):
            seg.render(config)

    def test_remotion_segment_get_duration(self):
        from video_toolkit.remotion.segments import RemotionSegment
        from video_toolkit.config import ProjectConfig

        seg = RemotionSegment(id="test", duration=5.0)
        assert seg.get_duration(ProjectConfig()) == 5.0

    def test_remotion_segment_get_duration_missing(self):
        from video_toolkit.remotion.segments import RemotionSegment
        from video_toolkit.config import ProjectConfig

        seg = RemotionSegment(id="test")
        with pytest.raises(ValueError):
            seg.get_duration(ProjectConfig())


class TestRemotionTitleSegment:
    """Tests for RemotionTitleSegment."""

    def test_title_segment_sets_composition_id(self):
        from video_toolkit.remotion.segments import RemotionTitleSegment

        seg = RemotionTitleSegment(
            id="title",
            title="Hello World",
            subtitle="Subtitle",
            duration=5.0,
        )

        assert seg.composition_id == "AnimatedTitle"
        assert seg.input_props["title"] == "Hello World"
        assert seg.input_props["subtitle"] == "Subtitle"
        assert seg.input_props["animation"] == "fade_up"

    def test_title_segment_animation_types(self):
        from video_toolkit.remotion.segments import RemotionTitleSegment

        for anim in ["fade_up", "slide_left", "typewriter", "scale"]:
            seg = RemotionTitleSegment(
                id=f"title_{anim}",
                title="Test",
                animation=anim,
                duration=3.0,
            )
            assert seg.input_props["animation"] == anim

    def test_title_segment_no_overlays_by_default(self):
        from video_toolkit.remotion.segments import RemotionTitleSegment

        seg = RemotionTitleSegment(id="title", title="Test", duration=3.0)
        assert seg.overlays is None

    def test_title_segment_colors_as_lists(self):
        from video_toolkit.remotion.segments import RemotionTitleSegment

        seg = RemotionTitleSegment(
            id="title",
            title="Test",
            background_color=(10, 20, 30),
            title_color=(40, 50, 60),
            duration=3.0,
        )
        assert seg.input_props["backgroundColor"] == [10, 20, 30]
        assert seg.input_props["titleColor"] == [40, 50, 60]


class TestRemotionImageSegment:
    """Tests for RemotionImageSegment."""

    def test_sets_composition_id(self):
        from video_toolkit.remotion.segments import RemotionImageSegment

        seg = RemotionImageSegment(
            id="img", image_path="/tmp/test.png", effect="zoom", duration=5.0
        )
        assert seg.composition_id == "ImageReveal"
        assert seg.input_props["imagePath"] == "/tmp/test.png"
        assert seg.input_props["effect"] == "zoom"

    def test_default_effect(self):
        from video_toolkit.remotion.segments import RemotionImageSegment

        seg = RemotionImageSegment(id="img", duration=3.0)
        assert seg.input_props["effect"] == "fade"

    def test_custom_background(self):
        from video_toolkit.remotion.segments import RemotionImageSegment

        seg = RemotionImageSegment(
            id="img", background_color=(0, 0, 0), duration=3.0
        )
        assert seg.input_props["backgroundColor"] == [0, 0, 0]

    def test_default_background_not_in_props(self):
        from video_toolkit.remotion.segments import RemotionImageSegment

        seg = RemotionImageSegment(id="img", duration=3.0)
        assert "backgroundColor" not in seg.input_props


class TestRemotionKenBurnsSegment:
    """Tests for RemotionKenBurnsSegment."""

    def test_sets_composition_id(self):
        from video_toolkit.remotion.segments import RemotionKenBurnsSegment

        seg = RemotionKenBurnsSegment(
            id="kb", image_path="/tmp/test.png", end_scale=1.3, duration=8.0
        )
        assert seg.composition_id == "KenBurns"
        assert seg.input_props["imagePath"] == "/tmp/test.png"
        assert seg.input_props["endScale"] == 1.3

    def test_default_scale_values(self):
        from video_toolkit.remotion.segments import RemotionKenBurnsSegment

        seg = RemotionKenBurnsSegment(id="kb", duration=5.0)
        assert seg.input_props["startScale"] == 1.0
        assert seg.input_props["endScale"] == 1.2
        assert seg.input_props["panX"] == 0
        assert seg.input_props["panY"] == 0


class TestRemotionSplitScreenSegment:
    """Tests for RemotionSplitScreenSegment."""

    def test_sets_composition_id(self):
        from video_toolkit.remotion.segments import RemotionSplitScreenSegment

        seg = RemotionSplitScreenSegment(
            id="ss", left_image="/tmp/a.png", right_image="/tmp/b.png",
            left_label="A", right_label="B", duration=6.0
        )
        assert seg.composition_id == "SplitScreen"
        assert seg.input_props["leftImagePath"] == "/tmp/a.png"
        assert seg.input_props["rightImagePath"] == "/tmp/b.png"
        assert seg.input_props["leftLabel"] == "A"
        assert seg.input_props["rightLabel"] == "B"

    def test_labels_optional(self):
        from video_toolkit.remotion.segments import RemotionSplitScreenSegment

        seg = RemotionSplitScreenSegment(
            id="ss", left_image="/tmp/a.png", right_image="/tmp/b.png",
            duration=6.0
        )
        assert "leftLabel" not in seg.input_props
        assert "rightLabel" not in seg.input_props


class TestRemotionCarouselSegment:
    """Tests for RemotionCarouselSegment."""

    def test_sets_composition_id(self):
        from video_toolkit.remotion.segments import RemotionCarouselSegment

        seg = RemotionCarouselSegment(
            id="car", image_paths=["/tmp/1.png", "/tmp/2.png"], duration=10.0
        )
        assert seg.composition_id == "ImageCarousel"
        assert seg.input_props["imagePaths"] == ["/tmp/1.png", "/tmp/2.png"]
        assert seg.input_props["transition"] == "fade"

    def test_custom_transition(self):
        from video_toolkit.remotion.segments import RemotionCarouselSegment

        seg = RemotionCarouselSegment(
            id="car", image_paths=[], transition="slide", duration=5.0
        )
        assert seg.input_props["transition"] == "slide"


class TestResolveAssetsWithLists:
    """Tests for _resolve_assets handling list values."""

    def test_resolve_list_of_paths(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer

        renderer = RemotionRenderer()

        img1 = temp_dir / "a.png"
        img2 = temp_dir / "b.png"
        img1.write_bytes(b"fake1")
        img2.write_bytes(b"fake2")

        bundle_dir = temp_dir / "bundle"
        bundle_dir.mkdir()

        props = {"imagePaths": [str(img1), str(img2)]}
        resolved = renderer._resolve_assets(props, str(bundle_dir))
        assert resolved["imagePaths"] == ["assets/a.png", "assets/b.png"]

    def test_non_asset_key_list_unchanged(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer

        renderer = RemotionRenderer()
        bundle_dir = temp_dir / "bundle"
        bundle_dir.mkdir()

        props = {"labels": ["A", "B", "C"]}
        resolved = renderer._resolve_assets(props, str(bundle_dir))
        assert resolved["labels"] == ["A", "B", "C"]

    def test_mixed_list_with_nonexistent(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer

        renderer = RemotionRenderer()

        img1 = temp_dir / "exists.png"
        img1.write_bytes(b"fake")

        bundle_dir = temp_dir / "bundle"
        bundle_dir.mkdir()

        props = {"imagePaths": [str(img1), "/nonexistent/missing.png"]}
        resolved = renderer._resolve_assets(props, str(bundle_dir))
        assert resolved["imagePaths"] == ["assets/exists.png", "/nonexistent/missing.png"]


class TestRemotionTransition:
    """Tests for RemotionTransition."""

    def test_transition_default_duration(self):
        from video_toolkit.remotion.transitions import RemotionTransition

        t = RemotionTransition(id="t1")
        assert t.duration == 0.5

    def test_transition_types(self):
        from video_toolkit.remotion.transitions import RemotionTransition

        t = RemotionTransition(id="t1", transition_type="crossfade")
        assert t.composition_id == "TransitionFade"

        t = RemotionTransition(id="t2", transition_type="slide_left")
        assert t.composition_id == "TransitionSlide"
        assert t.input_props["direction"] == "left"

        t = RemotionTransition(id="t3", transition_type="wipe_right")
        assert t.composition_id == "TransitionWipe"
        assert t.input_props["direction"] == "right"

    def test_transition_invalid_type(self):
        from video_toolkit.remotion.transitions import RemotionTransition

        with pytest.raises(ValueError, match="Unknown transition type"):
            RemotionTransition(id="t1", transition_type="invalid")

    def test_transition_needs_frames(self):
        from video_toolkit.remotion.transitions import RemotionTransition

        t = RemotionTransition(id="t1")
        assert t.needs_frames is True

        t.set_frames("/tmp/from.png", "/tmp/to.png")
        assert t.needs_frames is False
        assert t.input_props["fromImagePath"] == "/tmp/from.png"
        assert t.input_props["toImagePath"] == "/tmp/to.png"

    def test_transition_no_overlays(self):
        from video_toolkit.remotion.transitions import RemotionTransition

        t = RemotionTransition(id="t1")
        assert t.overlays is None


class TestRemotionGenerator:
    """Tests for RemotionGenerator."""

    def test_generator_cache_key(self):
        from video_toolkit.remotion.generator import RemotionGenerator

        gen = RemotionGenerator(
            composition_id="ImageReveal",
            input_props={"effect": "fade"},
            duration=5.0,
            key="test_v1",
        )
        key1 = gen.cache_key()
        key2 = gen.cache_key()
        assert key1 == key2
        assert len(key1) == 16

    def test_generator_requires_renderer(self, temp_dir):
        from video_toolkit.remotion.generator import RemotionGenerator
        from video_toolkit.config import ProjectConfig

        gen = RemotionGenerator(
            composition_id="ImageReveal",
            input_props={},
            duration=5.0,
            key="test",
        )

        config = ProjectConfig()
        with pytest.raises(RuntimeError, match="no renderer"):
            gen.generate(temp_dir / "out.mp4", config)


class TestVideoProjectRemotionIntegration:
    """Tests for Remotion integration in VideoProject."""

    def test_project_accepts_remotion_config(self, temp_dir):
        from video_toolkit import VideoProject
        from video_toolkit.remotion.config import RemotionConfig

        project = VideoProject(
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
            remotion_config=RemotionConfig(concurrency=4),
        )
        assert project._remotion_config is not None
        assert project._remotion_config.concurrency == 4

    def test_remotion_renderer_lazy_init(self, temp_dir):
        from video_toolkit import VideoProject
        from video_toolkit.remotion.config import RemotionConfig

        project = VideoProject(
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
            remotion_config=RemotionConfig(),
        )
        # Renderer not created yet
        assert project._remotion_renderer is None

        # Accessing property creates it
        renderer = project.remotion_renderer
        assert renderer is not None
        assert project._remotion_renderer is renderer

    def test_add_remotion_segment_injects_renderer(self, temp_dir):
        from video_toolkit import VideoProject
        from video_toolkit.remotion.config import RemotionConfig
        from video_toolkit.remotion.segments import RemotionSegment

        project = VideoProject(
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
            remotion_config=RemotionConfig(),
        )

        seg = RemotionSegment(
            id="test",
            composition_id="AnimatedTitle",
            input_props={"title": "Hello"},
            duration=3.0,
        )
        assert seg.renderer is None

        project.add_segment(seg)
        assert seg.renderer is not None
        assert seg.renderer is project.remotion_renderer

    def test_add_regular_segment_no_renderer(self, temp_dir):
        from video_toolkit import VideoProject
        from video_toolkit.segments import TitleSegment

        project = VideoProject(
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )

        seg = TitleSegment(id="title", title="Test", duration=3.0)
        project.add_segment(seg)

        # No renderer should have been created
        assert project._remotion_renderer is None

    def test_project_no_remotion_config(self, temp_dir):
        from video_toolkit import VideoProject
        from video_toolkit.remotion.segments import RemotionSegment

        project = VideoProject(
            output_dir=temp_dir / "output",
            cache_dir=temp_dir / "cache",
        )

        seg = RemotionSegment(id="test", duration=3.0)
        project.add_segment(seg)

        # Should still create a renderer with default config
        assert seg.renderer is not None


class TestCacheManagerRemotionLayer:
    """Tests for the remotion cache layer in CacheManager."""

    def test_remotion_cache_layer_exists(self, temp_dir):
        from video_toolkit.cache import CacheManager

        cm = CacheManager(base_dir=temp_dir / "cache")
        assert cm.remotion is not None
        assert (temp_dir / "cache" / "remotion").exists()

    def test_clear_all_includes_remotion(self, temp_dir):
        from video_toolkit.cache import CacheManager

        cm = CacheManager(base_dir=temp_dir / "cache")
        # Create a fake cached file
        (temp_dir / "cache" / "remotion" / "test.mp4").write_bytes(b"fake")

        result = cm.clear_all()
        assert "remotion" in result
        assert result["remotion"] == 1
