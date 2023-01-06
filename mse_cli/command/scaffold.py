"""mse_cli.cli.scaffold module."""

import os
from pathlib import Path

from mse_cli.command.helpers import non_empty_string
from mse_cli.conf.app import AppConf
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "scaffold", help="create a new boilerplate MSE web application")

    parser.set_defaults(func=run)

    parser.add_argument("name",
                        type=non_empty_string,
                        help="name of the MSE web application to create")


def run(args) -> None:
    """Run the subcommand."""
    project_dir = Path(os.getcwd()) / args.app_name
    os.makedirs(project_dir, exist_ok=False)

    # Saving the configuration file
    app_conf = AppConf.default(args.app_name, project_dir)
    app_conf.save(project_dir)

    # Saving the python code
    os.makedirs(app_conf.code.location, exist_ok=False)

    python_module = Path(
        app_conf.code.location) / (app_conf.python_module + ".py")
    python_module.write_text(f"""
from flask import Flask

{app_conf.python_variable} = Flask(__name__)


@{app_conf.python_variable}.route('/')
def hello():
    \"\"\"Get a simple example.\"\"\"
    return "Hello world"
""")

    LOG.info("An empty app has been generated in the current directory.")
    LOG.info("You can configure your mse application in: %s",
             project_dir / 'mse.toml')
