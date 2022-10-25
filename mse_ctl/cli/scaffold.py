"""Scaffold subparser definition."""

import os
from pathlib import Path

from mse_ctl.conf.app import AppConf
from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "scaffold", help="Create a new empty app in the current directory")

    parser.set_defaults(func=run)

    parser.add_argument('--name',
                        required=True,
                        type=str,
                        help='The name of the empty app.')


def run(args):
    """Run the subcommand."""
    project_dir = Path(os.getcwd()) / args.name
    os.makedirs(project_dir, exist_ok=False)

    # Saving the configuration file
    app_conf = AppConf.default(args.name, project_dir)
    app_conf.save(project_dir)

    # Saving the python code
    os.makedirs(app_conf.code_location, exist_ok=False)

    python_module = Path(
        app_conf.code_location) / (app_conf.python_module + ".py")
    python_module.write_text(f"""
from flask import Flask

{app_conf.python_variable} = Flask(__name__)


@{app_conf.python_variable}.route('/')
def hello():
    \"\"\"Get a simple example.\"\"\"
    return "Hello world"
""")

    # Saving the requirements
    requirements = Path(app_conf.code_location) / "requirements.txt"
    requirements.write_text("flask==2.0.2")

    log.info("An empty app has been generated in the current directory.")
    log.info("You can configure your mse application in: %s",
             project_dir / 'mse.toml')
