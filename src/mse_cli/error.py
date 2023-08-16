"""mse_cli.error module."""


class AppContainerNotFound(Exception):
    """Application container not found."""


class AppContainerNotRunning(Exception):
    """Application container is not running."""


class DockerBuildError(Exception):
    """Docker build failed."""


class AppContainerAlreadyRunning(Exception):
    """Application container is already running."""


class PortBusy(Exception):
    """Application port is already busy."""


class AppContainerError(Exception):
    """Application failed to start."""


class AppContainerBadState(Exception):
    """Application is not in the expecting state."""


class PackageMalformed(Exception):
    """Package is malformed."""


class Timeout(Exception):
    """Timeout occurs."""


class UnexpectedResponse(Exception):
    """Unexpected response when querying a server."""


class RatlsVerificationFailure(Exception):
    """The remote attestion failed."""


class RatlsVerificationNotSupported(Exception):
    """Proceed the remote attestion is impossible."""


class BadApplicationInput(Exception):
    """The application configuration is wrong."""


class WrongMREnclave(Exception):
    """MR enclave does not match with the expected value."""


class WrongMRSigner(Exception):
    """MR signer does not match with the expected value."""
