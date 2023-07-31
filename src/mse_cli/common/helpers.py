"""mse_cli.common.helpers module."""

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

import pkg_resources
from docker.errors import NotFound
from docker.models.containers import Container
from jinja2 import Template

from mse_cli.cloud.api.types import DefaultAppConfig
from mse_cli.core.bootstrap import is_ready
from mse_cli.core.clock_tick import ClockTick
from mse_cli.core.conf import AppConf, AppConfParsingOption
from mse_cli.core.test_docker import TestDockerConfig
from mse_cli.error import AppContainerError
from mse_cli.home.model.package import (
    DEFAULT_CODE_DIR,
    DEFAULT_CONFIG_FILENAME,
    DEFAULT_TEST_DIR,
)
from mse_cli.log import LOGGER as LOG


def scaffold(app_name: str, cloud_config: Optional[DefaultAppConfig] = None) -> Path:
    """Run the subcommand."""
    project_dir = Path(os.getcwd()) / app_name

    # Copy the template files
    shutil.copytree(pkg_resources.resource_filename("mse_cli", "template"), project_dir)

    template_conf_file = project_dir / "mse.toml.template"
    conf_file = project_dir / DEFAULT_CONFIG_FILENAME

    # Initialize the configuration file
    tm = Template(template_conf_file.read_text())
    if cloud_config:
        content = tm.render(
            name=app_name,
            docker=cloud_config.docker,
            project=cloud_config.project,
            hardware=cloud_config.hardware,
        )
    else:
        content = tm.render(name=app_name)

    conf_file.write_text(content)
    template_conf_file.unlink()

    app_conf = AppConf.load(
        conf_file,
        option=AppConfParsingOption.All
        if cloud_config
        else AppConfParsingOption.SkipCloud,
    )

    # Initialize the python code file
    code_dir = project_dir / (
        app_conf.cloud.code if app_conf.cloud else DEFAULT_CODE_DIR
    )
    template_code_file = code_dir / (app_conf.python_module + ".py.template")
    code_file = template_code_file.with_suffix("")

    tm = Template(template_code_file.read_text())
    content = tm.render(
        app=app_conf.python_variable,
        mse_home=cloud_config is None,
        healthcheck_endpoint=app_conf.healthcheck_endpoint,
    )
    code_file.write_text(content)
    template_code_file.unlink()

    # Initialize the .mseignore
    ignore_file: Path = code_dir / "dotmseignore"
    ignore_file.rename(code_dir / ".mseignore")

    # Initialize the pytest code files
    pytest_dir = project_dir / DEFAULT_TEST_DIR
    template_pytest_file = pytest_dir / "conftest.py.template"
    pytest_file = template_pytest_file.with_suffix("")

    tm = Template(template_pytest_file.read_text())
    content = tm.render(
        mse_home=cloud_config is None,
    )
    pytest_file.write_text(content)
    template_pytest_file.unlink()

    pytest_dir = project_dir / DEFAULT_TEST_DIR
    template_pytest_file = pytest_dir / "test_app.py.template"
    pytest_file = template_pytest_file.with_suffix("")

    tm = Template(template_pytest_file.read_text())
    content = tm.render(
        mse_home=cloud_config is None,
        healthcheck_endpoint=app_conf.healthcheck_endpoint,
    )
    pytest_file.write_text(content)
    template_pytest_file.unlink()

    return conf_file


def try_run_test_docker(
    app_config: AppConf,
    client,
    docker_name,
    container_name: str,
    docker_config: TestDockerConfig,
    test_path: Path,
    secrets_path: Optional[Path],
    sealed_secrets_path: Optional[Path],
    ignore_tests: bool = False,
):
    """Try to start the app docker to test."""
    success = False
    try:
        container = run_app_test_docker(
            client,
            docker_name,
            container_name,
            docker_config,
            app_config.healthcheck_endpoint,
        )

        if not ignore_tests:
            success = run_tests(
                app_config,
                test_path,
                secrets_path,
                sealed_secrets_path,
            )
        else:
            LOG.info(
                "The docker '%s' is started. "
                "You can now query your application on http://localhost:%s",
                docker_name,
                docker_config.port,
            )

            success = True

            for line in container.logs(stream=True):
                LOG.info(line.decode("utf-8").strip())

    except Exception as exc:
        raise exc
    finally:
        try:
            container = client.containers.get(container_name)
            if not success:
                LOG.info("The docker logs are:\n%s", container.logs().decode("utf-8"))
            container.stop(timeout=1)
            # We need to remove the container since we declare remove=False previously
            container.remove()
        except NotFound:
            pass


def run_app_test_docker(
    client,
    docker_name,
    container_name: str,
    docker_config: TestDockerConfig,
    healthcheck_endpoint: str,
) -> Container:
    """Run the app docker to test."""
    container = client.containers.run(
        docker_name,
        name=container_name,
        command=docker_config.cmd(),
        volumes=docker_config.volumes(),
        entrypoint=TestDockerConfig.entrypoint,
        ports=docker_config.ports(),
        detach=True,
        # We do not remove the container to be able to print the error (if some)
        remove=False,
    )

    clock = ClockTick(
        period=5,
        timeout=60,
        message="Test application docker is unreachable!",
    )

    while clock.tick():
        # Note: container.status is not actualized.
        # Get it again to have the current status
        container = client.containers.get(container_name)

        if container.status == "exited":
            raise AppContainerError("Application docker fails to start")

        if is_ready(f"http://localhost:{docker_config.port}", healthcheck_endpoint):
            break

    return container


def run_tests(
    app_config: AppConf,
    tests: Path,
    secrets: Optional[Path],
    sealed_secrets: Optional[Path],
) -> bool:
    """Run the tests."""
    LOG.info("Installing tests requirements...")
    for package in app_config.tests_requirements:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package],
            stdout=subprocess.DEVNULL,
        )

    LOG.info("Running tests...")
    env = dict(os.environ)
    if secrets:
        env["TEST_SECRET_JSON"] = str(secrets.resolve())

    if sealed_secrets:
        env["TEST_SEALED_SECRET_JSON"] = str(sealed_secrets.resolve())

    try:
        subprocess.check_call(app_config.tests_cmd, cwd=tests, env=env)

        LOG.info("Tests successful")
        return True
    except subprocess.CalledProcessError:
        LOG.error("Tests failed!")

    return False
