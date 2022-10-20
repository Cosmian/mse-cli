"""Scaffold subparser definition."""

import os
from pathlib import Path

from mse_ctl.conf.enclave import EnclaveConf
from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "scaffold", help="Create a new empty project in the current directory")

    parser.set_defaults(func=run)

    parser.add_argument('--name',
                        required=True,
                        type=str,
                        help='The name of the empty project.')


def run(args):
    """Run the subcommand."""
    project_dir = Path(os.getcwd()) / args.name
    os.makedirs(project_dir, exist_ok=False)

    # Saving the configuration file
    enclave_conf = EnclaveConf.default(args.name, project_dir)
    enclave_conf.save(project_dir)

    # Saving the python code
    os.makedirs(enclave_conf.code_location, exist_ok=False)

    python_module = Path(
        enclave_conf.code_location) / (enclave_conf.python_flask_module + ".py")
    python_module.write_text(f"""
from flask import Flask

{enclave_conf.python_flask_variable_name} = Flask(__name__)


@{enclave_conf.python_flask_variable_name}.route('/')
def hello():
    \"\"\"Get a simple example.\"\"\"
    return "Hello world"
""")

    # Saving the requirements
    requirements = Path(enclave_conf.code_location) / "requirements.txt"
    requirements.write_text("flask=2.2.2")

    log.info("An empty project has been generated in the current directory.")
    log.info("You can configured your mse application in: %s",
             project_dir / 'mse.toml')
