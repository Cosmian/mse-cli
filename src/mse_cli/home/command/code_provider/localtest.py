"""mse_cli.home.command.code_provider.localtest module."""

import argparse
from pathlib import Path
from typing import Optional

from docker.errors import BuildError

from mse_cli.common.helpers import try_run_test_docker
from mse_cli.core.conf import AppConf, AppConfParsingOption
from mse_cli.core.test_docker import TestDockerConfig
from mse_cli.error import DockerBuildError
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
        "localtest", help="test locally a MSE app in a development context"
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

    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="do not run the tests: just start the docker",
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

    try_run_test_docker(
        code_config,
        client,
        docker_name,
        container_name,
        docker_config,
        test_path,
        secrets_path,
        sealed_secrets_path,
        args.no_tests,
    )


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
        raise DockerBuildError(f"Failed to build your docker: {exc}") from exc
