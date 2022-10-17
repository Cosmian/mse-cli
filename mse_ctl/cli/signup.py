"""Signup subparser definition."""

from pathlib import Path
from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("signup", help="Sign up a new user")

    parser.set_defaults(func=run)


def run(args):
    """Run the subcommand."""
    log.info("You are now redirected to your browser to sign up...")

    log.info("Waiting for session... Done")
    log.info("Successfully logged in as my_email@example.com")

    log.info("Your access token is now saved into: path")

    log.info("Welcome to Full-Encrypted-Saas. "
             "You can use scaffold subcommand to initialize a new project.")
