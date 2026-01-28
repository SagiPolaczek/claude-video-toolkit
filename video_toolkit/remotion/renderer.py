"""RemotionRenderer - Python-to-Node.js bridge for Remotion rendering."""

import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

from .config import RemotionConfig
from .exceptions import BundleError, DependencyError, RenderError, RemotionError

if TYPE_CHECKING:
    from video_toolkit.config import ProjectConfig

# Path to the _node/ project shipped with this package
_NODE_PROJECT_DIR = Path(__file__).parent / "_node"


class RemotionRenderer:
    """Python-to-Node.js bridge for Remotion rendering.

    Manages the lifecycle of the Remotion rendering backend:
    - Dependency checking (Node.js >= 18, npm install)
    - Webpack bundling with caching
    - Rendering compositions to MP4 via headless Chromium
    - Asset path resolution for browser access
    """

    def __init__(
        self,
        remotion_config: Optional[RemotionConfig] = None,
        project_config: Optional["ProjectConfig"] = None,
    ):
        self._config = remotion_config or RemotionConfig()
        self._project_config = project_config
        self._serve_url: Optional[str] = None
        self._deps_checked = False

        # Determine bundle cache directory (must be absolute for webpack)
        if self._config.bundle_cache_dir:
            self._bundle_cache_dir = Path(self._config.bundle_cache_dir).resolve()
        elif project_config:
            self._bundle_cache_dir = (project_config.cache_dir / "remotion_bundles").resolve()
        else:
            self._bundle_cache_dir = (_NODE_PROJECT_DIR / "dist").resolve()

    @property
    def node_project_dir(self) -> Path:
        """Path to the Node.js Remotion project."""
        return _NODE_PROJECT_DIR

    def ensure_dependencies(self) -> None:
        """Check that Node.js >= 18 is installed and npm packages are available.

        Raises:
            DependencyError: If Node.js is missing or version is too old.
        """
        if self._deps_checked:
            return

        # Check Node.js
        try:
            result = subprocess.run(
                [self._config.node_executable, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                raise DependencyError(
                    f"Node.js check failed: {result.stderr.strip()}"
                )
            version_str = result.stdout.strip().lstrip("v")
            major = int(version_str.split(".")[0])
            if major < 18:
                raise DependencyError(
                    f"Node.js >= 18 required, found v{version_str}. "
                    "Install from https://nodejs.org/"
                )
        except FileNotFoundError:
            raise DependencyError(
                f"Node.js not found at '{self._config.node_executable}'. "
                "Install from https://nodejs.org/"
            )

        # Check if node_modules exists, run npm install if not
        node_modules = _NODE_PROJECT_DIR / "node_modules"
        if not node_modules.exists():
            print("  [Remotion] Installing npm dependencies...")
            try:
                result = subprocess.run(
                    [self._config.npm_executable, "install"],
                    cwd=str(_NODE_PROJECT_DIR),
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if result.returncode != 0:
                    raise DependencyError(
                        f"npm install failed:\n{result.stderr.strip()}"
                    )
            except FileNotFoundError:
                raise DependencyError(
                    f"npm not found at '{self._config.npm_executable}'. "
                    "Install Node.js from https://nodejs.org/"
                )

        self._deps_checked = True

    def bundle(self, force: bool = False) -> str:
        """Bundle the Remotion project with webpack.

        Returns:
            The serve URL (path to the bundled output).

        Raises:
            BundleError: If bundling fails.
        """
        self.ensure_dependencies()

        if not force and self._serve_url:
            return self._serve_url

        bundle_hash = self._compute_bundle_hash()
        cached_bundle = self._bundle_cache_dir / f"bundle_{bundle_hash}"

        if not force and cached_bundle.exists():
            if (cached_bundle / "index.html").exists():
                self._serve_url = str(cached_bundle)
                return self._serve_url

        print("  [Remotion] Bundling project...")
        self._bundle_cache_dir.mkdir(parents=True, exist_ok=True)

        if self._config.custom_compositions_dir:
            self._copy_custom_compositions()

        result = self._call_node("bundle", {
            "entryPoint": str(_NODE_PROJECT_DIR / "src" / "index.tsx"),
            "outDir": str(cached_bundle),
        })

        if "serveUrl" not in result:
            raise BundleError(f"Bundle did not return serveUrl: {result}")

        self._serve_url = result["serveUrl"]
        return self._serve_url

    def render(
        self,
        composition_id: str,
        input_props: Dict[str, Any],
        output_path: str,
        duration_in_frames: int,
        width: int,
        height: int,
        fps: int = 30,
    ) -> Path:
        """Render a Remotion composition to an MP4 file.

        Returns:
            Path to the rendered MP4 file.

        Raises:
            RenderError: If rendering fails.
        """
        serve_url = self.bundle()

        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Resolve local file paths in props so Chromium can access them
        resolved_props = self._resolve_assets(input_props, serve_url)

        args = {
            "serveUrl": serve_url,
            "compositionId": composition_id,
            "outputPath": str(output_path),
            "inputProps": resolved_props,
            "durationInFrames": duration_in_frames,
            "fps": fps,
            "width": width,
            "height": height,
            "logLevel": self._config.log_level,
        }

        if self._config.concurrency > 1:
            args["concurrency"] = self._config.concurrency
        if self._config.chromium_executable:
            args["chromiumExecutable"] = self._config.chromium_executable

        self._call_node("render", args)

        if not output_path.exists():
            raise RenderError(
                f"Render completed but output file not found: {output_path}"
            )

        return output_path

    def cleanup(self) -> None:
        """Remove cached bundles."""
        if self._bundle_cache_dir.exists():
            shutil.rmtree(self._bundle_cache_dir)
        self._serve_url = None

    def _call_node(self, action: str, args: Dict[str, Any]) -> Any:
        """Call render.mjs via subprocess, passing JSON on stdin.

        Returns:
            Parsed JSON from stdout.

        Raises:
            RemotionError: If the subprocess fails.
        """
        self.ensure_dependencies()

        render_script = _NODE_PROJECT_DIR / "render.mjs"

        try:
            result = subprocess.run(
                [self._config.node_executable, str(render_script), action],
                input=json.dumps(args),
                capture_output=True,
                text=True,
                cwd=str(_NODE_PROJECT_DIR),
                timeout=self._config.timeout_per_segment,
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip() or "Unknown error"
                error_cls = {
                    "bundle": BundleError,
                    "render": RenderError,
                }.get(action, RemotionError)
                raise error_cls(f"Remotion {action} failed:\n{error_msg}")

            stdout = result.stdout.strip()
            if not stdout:
                raise RemotionError(
                    f"Remotion {action} produced no output.\n"
                    f"stderr: {result.stderr.strip()}"
                )

            # Find last JSON line (Remotion may print warnings before)
            for line in reversed(stdout.splitlines()):
                line = line.strip()
                if line.startswith("{") or line.startswith("["):
                    return json.loads(line)

            raise RemotionError(
                f"Remotion {action} output is not valid JSON:\n{stdout}"
            )

        except subprocess.TimeoutExpired:
            raise RenderError(
                f"Remotion {action} timed out after "
                f"{self._config.timeout_per_segment}s"
            )

    def _resolve_assets(
        self, props: Dict[str, Any], serve_url: str
    ) -> Dict[str, Any]:
        """Resolve local file paths in props for Chromium access.

        Props with keys containing 'path', 'image', 'source', 'src', 'asset',
        or 'background' are checked. Local files are copied to both
        _node/public/assets/ and the bundle's public/assets/ directory, then
        prop values are rewritten to staticFile-relative paths.
        """
        asset_keys = {"path", "image", "source", "src", "asset", "background"}
        resolved = {}
        public_assets = _NODE_PROJECT_DIR / "public" / "assets"
        bundle_assets = Path(serve_url) / "public" / "assets"

        for key, value in props.items():
            if isinstance(value, str) and any(
                ak in key.lower() for ak in asset_keys
            ):
                candidate = Path(value)
                if candidate.exists() and candidate.is_file():
                    # Copy to both source public/ and bundle public/
                    for dest_dir in (public_assets, bundle_assets):
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        dest = dest_dir / candidate.name
                        if not dest.exists() or dest.stat().st_mtime < candidate.stat().st_mtime:
                            shutil.copy2(str(candidate), str(dest))
                    resolved[key] = f"assets/{candidate.name}"
                else:
                    resolved[key] = value
            elif isinstance(value, list):
                resolved[key] = self._resolve_asset_list(value, serve_url, key)
            elif isinstance(value, dict):
                resolved[key] = self._resolve_assets(value, serve_url)
            else:
                resolved[key] = value

        return resolved

    def _resolve_asset_list(
        self, items: list, serve_url: str, key: str
    ) -> list:
        """Resolve local file paths within a list prop."""
        asset_keys = {"path", "image", "source", "src", "asset", "background"}
        is_asset_key = any(ak in key.lower() for ak in asset_keys)

        resolved = []
        for item in items:
            if isinstance(item, str) and is_asset_key:
                candidate = Path(item)
                if candidate.exists() and candidate.is_file():
                    public_assets = _NODE_PROJECT_DIR / "public" / "assets"
                    bundle_assets = Path(serve_url) / "public" / "assets"
                    for dest_dir in (public_assets, bundle_assets):
                        dest_dir.mkdir(parents=True, exist_ok=True)
                        dest = dest_dir / candidate.name
                        if not dest.exists() or dest.stat().st_mtime < candidate.stat().st_mtime:
                            shutil.copy2(str(candidate), str(dest))
                    resolved.append(f"assets/{candidate.name}")
                else:
                    resolved.append(item)
            elif isinstance(item, dict):
                resolved.append(self._resolve_assets(item, serve_url))
            else:
                resolved.append(item)
        return resolved

    def _compute_bundle_hash(self) -> str:
        """Compute a hash for bundle cache invalidation."""
        hasher = hashlib.sha256()

        pkg_json = _NODE_PROJECT_DIR / "package.json"
        if pkg_json.exists():
            hasher.update(pkg_json.read_bytes())

        src_dir = _NODE_PROJECT_DIR / "src"
        if src_dir.exists():
            for f in sorted(src_dir.rglob("*")):
                if f.is_file():
                    hasher.update(f.name.encode())
                    hasher.update(str(f.stat().st_mtime_ns).encode())

        if self._config.custom_compositions_dir:
            custom_dir = Path(self._config.custom_compositions_dir)
            if custom_dir.exists():
                for f in sorted(custom_dir.rglob("*.tsx")):
                    hasher.update(f.name.encode())
                    hasher.update(str(f.stat().st_mtime_ns).encode())

        return hasher.hexdigest()[:16]

    def _copy_custom_compositions(self) -> None:
        """Copy user-provided .tsx compositions into _node/src/custom/."""
        custom_dir = Path(self._config.custom_compositions_dir)
        if not custom_dir.exists():
            return

        target = _NODE_PROJECT_DIR / "src" / "custom"
        target.mkdir(parents=True, exist_ok=True)

        for tsx_file in custom_dir.glob("*.tsx"):
            dest = target / tsx_file.name
            shutil.copy2(str(tsx_file), str(dest))
