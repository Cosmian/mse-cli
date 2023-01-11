import logging
import pytest

import io
from mse_cli.log import setup_logging, LOGGER as LOG

# cmd_log_str should be shared between all tests (to not close by any tests)
cmd_log_str = None


@pytest.fixture(scope="module")
def cmd_log() -> io.StringIO:
    """Initialize the log capturing."""
    global cmd_log_str
    if not cmd_log_str:
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
