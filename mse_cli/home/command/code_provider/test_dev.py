"""mse_cli.home.command.code_provider.test_dev module."""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from docker.errors import BuildError, NotFound
from docker.models.containers import Container

from mse_cli.core.bootstrap import is_ready
from mse_cli.core.clock_tick import ClockTick
from mse_cli.core.conf import AppConf, AppConfParsingOption
from mse_cli.core.test_docker import TestDockerConfig
from mse_cli.home.command.helpers import get_client_docker
from mse_cli.home.model.package import (
    DEFAULT_CODE_DIR,
    DEFAULT_CONFIG_FILENAME,
    DEFAULT_DOCKERFILE_FILENAME,
    DEFAULT_SEAL_SECRETS_FILENAME,
    DEFAULT_SECRETS_FILENAME,
    DEFAULT_TEST_DIR,
)
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "test-dev", help="test a MSE app in a development context"
    )

    parser.add_argument("--project", type=Path, help="path of the project to test")

    parser.add_argument("--code", type=Path, help="path to the code to run")

    parser.add_argument(
        "--config", type=Path, help="conf path extracted from the MSE package"
    )

    parser.add_argument("--dockerfile", type=Path, help="path to the Dockerfile")

    parser.add_argument(
        "--test",
        type=Path,
        help="path of the test directory extracted from the MSE package",
    )

    parser.add_argument(
        "--secrets",
        type=Path,
        help="the `secrets.json` file path",
    )

    parser.add_argument(
        "--sealed-secrets",
        type=Path,
        help="the secrets JSON to seal file path (unsealed for the test purpose)",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    code_path: Path
    test_path: Path
    config_path: Path
    dockerfile_path: Path
    secrets_path: Optional[Path]
    sealed_secrets_path: Optional[Path]

    if args.project:
        if any([args.code, args.config, args.dockerfile, args.test]):
            raise argparse.ArgumentTypeError(
                "[--project] and [--code & --config & --dockerfile & --test] "
                "are mutually exclusive"
            )

        if not args.project.is_dir():
            raise NotADirectoryError(f"`{args.project}` does not exist")

        code_path = args.project / DEFAULT_CODE_DIR
        test_path = args.project / DEFAULT_TEST_DIR
        config_path = args.project / DEFAULT_CONFIG_FILENAME
        dockerfile_path = args.project / DEFAULT_DOCKERFILE_FILENAME

        secrets_path = args.project / DEFAULT_SECRETS_FILENAME
        sealed_secrets_path = args.project / DEFAULT_SEAL_SECRETS_FILENAME

    else:
        if not all([args.code, args.config, args.dockerfile, args.test]):
            raise argparse.ArgumentTypeError(
                "the following arguments are required: "
                "--code, --dockerfile, --test, --config\n"
                "the following arguments remain optional: "
                "[--secrets], [--sealed-secrets]"
            )

        code_path = args.code
        test_path = args.test
        config_path = args.config
        dockerfile_path = args.dockerfile
        secrets_path = args.secrets
        sealed_secrets_path = args.sealed_secrets

    if not code_path.is_dir():
        raise NotADirectoryError(f"`{code_path}` does not exist")

    if not test_path.is_dir():
        raise NotADirectoryError(f"`{test_path}` does not exist")

    if not config_path.is_file():
        raise FileNotFoundError(f"`{config_path}` does not exist")

    if not dockerfile_path.is_file():
        raise FileNotFoundError(f"`{dockerfile_path}` does not exist")

    if secrets_path and not secrets_path.is_file():
        raise FileNotFoundError(f"`{secrets_path}` does not exist")

    if sealed_secrets_path and not sealed_secrets_path.is_file():
        raise FileNotFoundError(f"`{sealed_secrets_path}` does not exist")

    code_config = AppConf.load(config_path, option=AppConfParsingOption.SkipCloud)
    container_name = docker_name = f"{code_config.name}_test"

    client = get_client_docker()

    build_test_docker(client, dockerfile_path, docker_name)

    LOG.info("Starting the docker: %s...", docker_name)
    docker_config = TestDockerConfig(
        code=code_path,
        application=code_config.python_application,
        secrets=secrets_path,
        sealed_secrets=sealed_secrets_path,
        port=5000,
    )

    try_run(
        code_config,
        client,
        docker_name,
        container_name,
        docker_config,
        test_path,
        secrets_path,
        sealed_secrets_path,
    )


def try_run(
    app_config: AppConf,
    client,
    docker_name,
    container_name: str,
    docker_config: TestDockerConfig,
    test_path: Path,
    secrets_path: Optional[Path],
    sealed_secrets_path: Optional[Path],
):
    """Try to start the app docker to test"""
    success = False
    try:
        container = run_app_docker(
            client,
            docker_name,
            container_name,
            docker_config,
            app_config.healthcheck_endpoint,
        )

        success = run_tests(
            app_config,
            test_path,
            secrets_path,
            sealed_secrets_path,
        )

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


def run_app_docker(
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
        timeout=10,
        message="Test application docker is unreachable!",
    )

    while clock.tick():
        # Note: container.status is not actualized.
        # Get it again to have the current status
        container = client.containers.get(container_name)

        if container.status == "exited":
            raise Exception("Application docker fails to start")

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


def build_test_docker(client, dockerfile: Path, docker_name: str):
    """Build the test docker."""

    try:
        LOG.info("Building your docker image...")

        # Build the docker
        client.images.build(
            path=str(dockerfile.parent),
            tag=docker_name,
        )
    except BuildError as exc:
        raise Exception(f"Failed to build your docker: {exc}") from exc
