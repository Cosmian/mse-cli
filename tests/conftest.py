import io
import logging
import time

import pytest

from mse_cli.log import LOGGER as LOG
from mse_cli.log import setup_logging


@pytest.fixture(scope="session")
def cmd_log() -> io.StringIO:
    """Initialize the log capturing."""
    cmd_log_str = io.StringIO()
    ch = logging.StreamHandler(cmd_log_str)
    ch.setLevel(logging.DEBUG)
    setup_logging()
    LOG.addHandler(ch)
    yield cmd_log_str


def capture_logs(f: io.StringIO) -> str:
    """Get the logs stacked until now."""
    log_contents = f.getvalue()
    f.truncate(0)
    return log_contents


@pytest.fixture(autouse=True)
def slow_down_tests():
    """We sleep 1 sec between tests due to API limitation in dev env."""
    yield
    time.sleep(1)
