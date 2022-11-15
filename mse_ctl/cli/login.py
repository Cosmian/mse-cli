"""Login subparser definition."""

from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("login", help="Login an existing user")

    parser.set_defaults(func=run)


def run(_args):
    """Run the subcommand."""
    log.info("You are now redirected to your browser to login")
    log.info("Waiting for session... Done")
    log.info("Successfully logged in as my_email@example.com")

    log.info("Your access token is now saved into: conf path")
