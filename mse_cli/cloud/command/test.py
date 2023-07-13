"""mse_cli.cloud.command.test module."""

import os
import subprocess
import sys
import uuid
from pathlib import Path

from mse_cli.cloud.command.helpers import get_app
from mse_cli.cloud.model.context import Context
from mse_cli.cloud.model.user import UserConf
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("test", help="test a deployed MSE app")

    parser.add_argument(
        "app_id",
        type=uuid.UUID,
        help="identifier of the MSE web application to run tests against",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.load()
    conn = user_conf.get_connection()

    context_path: Path = Context.get_context_filepath(args.app_id, create=False)

    if not context_path.exists():
        raise FileNotFoundError(
            f"Can't find context for UUID: {args.app_id}. Run the tests manually"
        )

    context = Context.load(context_path)
    app = get_app(conn=conn, app_id=args.app_id)

    for package in context.config.tests_requirements:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    try:
        subprocess.check_call(
            context.config.tests_cmd,
            cwd=context.config.tests,
            env=dict(os.environ, TEST_REMOTE_URL=f"https://{app.domain_name}"),
        )

        LOG.info("Tests successful")
    except subprocess.CalledProcessError:
        LOG.error("Tests failed!")
