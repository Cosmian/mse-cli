"""mse_cli.log module."""

import logging
import sys

LOGGER = logging.getLogger("mse")


def setup_logging(debug: bool = False):
    """Configure basic logging."""
    logging.basicConfig(stream=sys.stdout, format="%(message)s")
    LOGGER.setLevel(logging.DEBUG if debug else logging.INFO)
