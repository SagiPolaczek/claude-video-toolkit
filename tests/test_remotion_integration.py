"""Integration tests for Remotion rendering (requires Node.js >= 18).

These tests actually call the Remotion renderer and produce real MP4 output.
They are skipped if Node.js is not available or if npm dependencies are not
installed.
"""

import shutil
import subprocess

import pytest

# Check if Node.js >= 18 is available
def _node_available() -> bool:
    try:
        result = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return False
        version = result.stdout.strip().lstrip("v")
        return int(version.split(".")[0]) >= 18
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


requires_node = pytest.mark.skipif(
    not _node_available(),
    reason="Node.js >= 18 not available",
)


@requires_node
class TestRemotionRendererIntegration:
    """Integration tests for RemotionRenderer."""

    def test_ensure_dependencies(self):
        from video_toolkit.remotion.renderer import RemotionRenderer

        renderer = RemotionRenderer()
        # Should not raise
        renderer.ensure_dependencies()
        assert renderer._deps_checked is True

    def test_bundle(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer
        from video_toolkit.remotion.config import RemotionConfig

        config = RemotionConfig(bundle_cache_dir=temp_dir / "bundles")
        renderer = RemotionRenderer(config)

        serve_url = renderer.bundle()
        assert serve_url is not None
        assert "index.html" in str(serve_url) or (
            (temp_dir / "bundles").exists()
        )

    def test_render_animated_title(self, temp_dir):
        from video_toolkit.remotion.renderer import RemotionRenderer
        from video_toolkit.remotion.config import RemotionConfig

        config = RemotionConfig(bundle_cache_dir=temp_dir / "bundles")
        renderer = RemotionRenderer(config)

        output = temp_dir / "title.mp4"
        renderer.render(
            composition_id="AnimatedTitle",
            input_props={
                "title": "Integration Test",
                "subtitle": "Works!",
                "animation": "fade_up",
            },
            output_path=str(output),
            duration_in_frames=30,  # 1 second
            width=854,
            height=480,
            fps=30,
        )

        assert output.exists()
        assert output.stat().st_size > 0

    def test_remotion_segment_end_to_end(self, temp_dir):
        from video_toolkit.remotion.segments import RemotionTitleSegment
        from video_toolkit.remotion.renderer import RemotionRenderer
        from video_toolkit.remotion.config import RemotionConfig
        from video_toolkit.config import ProjectConfig, Resolution

        config = RemotionConfig(bundle_cache_dir=temp_dir / "bundles")
        renderer = RemotionRenderer(config)

        seg = RemotionTitleSegment(
            id="test_title",
            title="End-to-End Test",
            subtitle="Remotion + MoviePy",
            animation="scale",
            duration=1.0,
            renderer=renderer,
        )

        project_config = ProjectConfig(
            resolution=Resolution.DRAFT,
            cache_dir=temp_dir / "cache",
        )

        clip = seg.render(project_config)
        assert clip is not None
        assert clip.duration > 0
        clip.close()
