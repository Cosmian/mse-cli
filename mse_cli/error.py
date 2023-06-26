"""mse_home.error module."""


class AppContainerNotFound(Exception):
    """Application container not found."""


class AppContainerNotRunning(Exception):
    """Application container is not running."""
