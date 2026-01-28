"""Remotion configuration."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class RemotionConfig:
    """Configuration for the Remotion rendering backend.

    Attributes:
        node_executable: Path to Node.js binary (>= 18 required).
        npm_executable: Path to npm binary.
        custom_compositions_dir: Directory with user-provided .tsx compositions.
        bundle_cache_dir: Override directory for webpack bundle cache.
            Defaults to <project_cache_dir>/remotion_bundles/.
        concurrency: Number of parallel Remotion render threads.
        chromium_executable: Path to Chromium binary (auto-detected if None).
        timeout_per_segment: Max seconds for a single segment render.
        log_level: Remotion log level ("verbose", "info", "warn", "error").
    """

    node_executable: str = "node"
    npm_executable: str = "npm"
    custom_compositions_dir: Optional[Path] = None
    bundle_cache_dir: Optional[Path] = None
    concurrency: int = 1
    chromium_executable: Optional[str] = None
    timeout_per_segment: int = 120
    log_level: str = "warn"
