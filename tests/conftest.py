"""conftest file."""

import io
import logging
import os
import time
from argparse import Namespace
from pathlib import Path
from uuid import UUID

import pytest
from docker.errors import NotFound

from mse_cli.cloud.command.stop import run as run_stop
from mse_cli.home.command.helpers import get_client_docker
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


@pytest.fixture(scope="session")
def workspace(tmp_path_factory) -> Path:
    """Create a workspace for the test session."""
    return tmp_path_factory.mktemp("workspace")


@pytest.fixture(scope="session")
def app_name() -> str:
    """Define the name of the application to spawn."""
    return f"app_{time.time_ns()}"


@pytest.fixture(scope="session")
def port() -> int:
    """Define the port of the app docker to spawn."""
    return 5555


@pytest.fixture(scope="session")
def port2() -> int:
    """Define another usable port."""
    return 5556


@pytest.fixture(scope="session")
def port3() -> int:
    """Define another usable port."""
    return 5557


@pytest.fixture(scope="session")
def host() -> str:
    """Define the host of the app docker to spawn."""
    return "localhost"


@pytest.fixture(scope="session")
def pccs_url() -> str:
    """Define the pccs url."""
    e = os.getenv("TEST_PCCS_URL")
    if not e:
        raise Exception("Can't find `TEST_PCCS_URL` env variable")
    return e


@pytest.fixture(scope="session")
def signer_key() -> Path:
    """Define the signer key."""
    e = os.getenv("TEST_SIGNER_KEY")
    if not e:
        raise Exception("Can't find `TEST_SIGNER_KEY` env variable")
    return Path(e)


@pytest.mark.usefixtures("workspace")
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Put an hook the makereport to cleanup after test failure."""
    # Because this is a hookwrapper, calling `yield` lets
    # the actual hooks run & returns a `_Result`
    result = yield
    # Get the actual `TestReport` which the hook(s) returned,
    # having done the hard work for you
    report = result.get_result()

    # If a test fail, try to clean up the dockers we could have spawned
    if report.outcome == "failed":
        if "app_name" in item.funcargs:
            app_name_fixture = item.funcargs["app_name"]

            client = get_client_docker()

            # The test docker (mse home case)
            try:
                container = client.containers.get(f"{app_name_fixture}_test")
                container.stop(timeout=1)
                container.remove()
            except NotFound:
                pass

            # The app docker (mse home case)
            try:
                container = client.containers.get(f"{app_name_fixture}")
                container.stop(timeout=1)
                container.remove()
            except NotFound:
                pass

        # We try to stop the application in case of failure (mse cloud only)
        if "tmp_path" in item.funcargs:
            workspace = Path(item.funcargs["tmp_path"])
            app_id_file: Path = workspace / "app_id"

            if app_id_file.exists():
                app_id = app_id_file.read_text()
                app_id_file.unlink()
                try:
                    run_stop(Namespace(**{"app_id": [UUID(app_id)]}))
                except:
                    pass
