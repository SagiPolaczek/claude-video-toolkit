"""Remotion-specific exceptions."""


class RemotionError(Exception):
    """Base exception for Remotion-related errors."""

    pass


class BundleError(RemotionError):
    """Error during Remotion webpack bundling."""

    pass


class RenderError(RemotionError):
    """Error during Remotion rendering."""

    pass


class DependencyError(RemotionError):
    """Error when required dependencies (Node.js, npm) are missing."""

    pass
