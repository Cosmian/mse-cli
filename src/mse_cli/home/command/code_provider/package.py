"""mse_cli.home.command.code_provider.package module."""

import argparse
import os
import shutil
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

from docker.errors import BuildError
from mse_lib_crypto.xsalsa20_poly1305 import encrypt_directory, random_key

from mse_cli.core.conf import AppConf, AppConfParsingOption
from mse_cli.core.fs import tar, whitelist
from mse_cli.core.ignore_file import IgnoreFile
from mse_cli.home.command.helpers import get_client_docker
from mse_cli.home.model.package import (
    CODE_TAR_NAME,
    DEFAULT_CODE_DIR,
    DEFAULT_CONFIG_FILENAME,
    DEFAULT_DOCKERFILE_FILENAME,
    DEFAULT_TEST_DIR,
    DOCKER_IMAGE_TAR_NAME,
    TEST_TAR_NAME,
    CodePackage,
)
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "package",
        help="generate a package containing the Docker image and the code to run on MSE",
    )

    parser.add_argument("--project", type=Path, help="path of the project to pack")

    parser.add_argument("--code", type=Path, help="path of the code to run")

    parser.add_argument("--config", type=Path, help="path to the code configuration")

    parser.add_argument("--dockerfile", type=Path, help="path to the Dockerfile")

    parser.add_argument("--test", type=Path, help="test directory")

    parser.add_argument(
        "--output", type=Path, required=True, help="directory to write the package"
    )

    parser.add_argument(
        "--encrypt",
        action="store_true",
        help="encrypt the code before packaging it",
    )

    parser.set_defaults(func=run)


# pylint: disable=too-many-statements
def run(args) -> None:
    """Run the subcommand."""
    package_path: Path = args.output.resolve()
    if not package_path.exists():
        os.makedirs(package_path)
    elif not package_path.is_dir():
        raise NotADirectoryError(f"{package_path} does not exist")

    code_path: Path
    test_path: Path
    config_path: Path
    dockerfile_path: Path

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
    else:
        if not all([args.code, args.config, args.dockerfile, args.test]):
            raise argparse.ArgumentTypeError(
                "the following arguments are required: "
                "--code, --config, --dockerfile, --test"
            )

        code_path = args.code
        test_path = args.test
        config_path = args.config
        dockerfile_path = args.dockerfile

    if not code_path.is_dir():
        raise NotADirectoryError(f"`{code_path}` does not exist")

    if not test_path.is_dir():
        raise NotADirectoryError(f"`{test_path}` does not exist")

    if not config_path.is_file():
        raise FileNotFoundError(f"`{config_path}` does not exist")

    if not dockerfile_path.is_file():
        raise FileNotFoundError(f"`{dockerfile_path}` does not exist")

    code_config = AppConf.load(config_path, option=AppConfParsingOption.SkipCloud)

    workspace = Path(tempfile.mkdtemp(dir=package_path))

    LOG.info("A workspace has been created at: %s", str(workspace))

    package = CodePackage(
        code_tar=workspace / CODE_TAR_NAME,
        image_tar=workspace / DOCKER_IMAGE_TAR_NAME,
        test_tar=workspace / TEST_TAR_NAME,
        config_path=config_path.resolve(),
    )

    now = time.time_ns()
    code_secret_path = package_path / f"package_{code_config.name}_{now}.key"
    package_path = package_path / f"package_{code_config.name}_{now}.tar"

    (secret_key, _) = create_code_tar(
        code_path.resolve(), package.code_tar, args.encrypt
    )

    if secret_key:
        code_secret_path.write_bytes(secret_key)
        LOG.info("Your code secret key has been saved at: %s", code_secret_path)

    create_test_tar(
        test_path.resolve(),
        package.test_tar,
    )

    create_image_tar(dockerfile_path.resolve(), code_config.name, package.image_tar)

    LOG.info("Creating the final package...")

    package.create(package_path)

    LOG.info("Your package is now ready to be shared: %s", package_path)

    # Clean up the workspace
    LOG.info("Cleaning up the temporary workspace...")
    shutil.rmtree(workspace)


def create_code_tar(
    code_path: Path, output_tar_path: Path, encrypt_code: bool
) -> Tuple[Optional[bytes], Optional[Dict[str, bytes]]]:
    """Create the tarball for the code directory."""
    if encrypt_code:
        LOG.info("Encrypting your code...")

        # Generate the key to encrypt the code
        secret_key = random_key()

        encrypted_path = output_tar_path.parent / "encrypted_code"

        # Encrypt the code directory
        nounces = encrypt_directory(
            dir_path=code_path,
            pattern="*",
            key=secret_key,
            nonces=None,
            exceptions=whitelist(),
            ignore_patterns=list(IgnoreFile.parse(code_path)),
            out_dir_path=encrypted_path,
        )

        LOG.info("Your encryption key is: %s", bytes(secret_key).hex())
        LOG.info("Building the code archive...")

        # Generate the tarball
        tar(dir_path=encrypted_path, tar_path=output_tar_path)

        return (secret_key, nounces)

    LOG.info("Building the code archive...")

    mirror_path = output_tar_path.parent / "mirrored_code"

    # We copy the code directory to remove the files to ignore when taring
    shutil.copytree(
        code_path,
        mirror_path,
        ignore=shutil.ignore_patterns(*list(IgnoreFile.parse(code_path))),
    )

    # Generate the tarball
    tar(dir_path=mirror_path, tar_path=output_tar_path)

    return (None, None)


def create_test_tar(test_path: Path, output_tar_path: Path):
    """Create the tarball for the tests directory."""
    LOG.info("Building the tests archive...")

    mirror_path = output_tar_path.parent / "mirrored_tests"

    # We copy the code directory to remove the files to ignore when taring
    shutil.copytree(
        test_path,
        mirror_path,
        ignore=shutil.ignore_patterns(*["__pycache__", ".pytest_cache"]),
    )

    # Generate the tarball
    tar(dir_path=mirror_path, tar_path=output_tar_path)


def create_image_tar(dockerfile: Path, image_name: str, output_tar_path: Path):
    """Build the docker image and export it into a tarball."""
    client = get_client_docker()

    try:
        LOG.info("Building your docker image...")

        # Build the docker
        (image, _streamer) = client.images.build(
            path=str(dockerfile.parent),
            tag=f"{image_name}:{time.time_ns()}",
        )

        # for chunk in streamer:
        #     if "stream" in chunk:
        #         for line in chunk["stream"].splitlines():
        #             LOG.info(line)

        LOG.info("Building the image archive...")

        # Save it as a tarball
        with open(output_tar_path, "wb") as f:
            for chunk in image.save(named=True):
                f.write(chunk)

    except BuildError as exc:
        LOG.error("Failed to build your docker!")
        raise exc
