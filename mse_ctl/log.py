"""mse_ctl.log module."""

import logging

LOGGER = logging.getLogger("mse")


def setup_logging(debug: bool = False):
    """Configure basic logging."""
    # logging.basicConfig(format="[%(asctime)s] [%(name)36s] => %(message)s")
    logging.basicConfig(format="%(message)s")
    LOGGER.setLevel(logging.DEBUG if debug else logging.INFO)
