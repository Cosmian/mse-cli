"""mse_cli.home.command.sgx_operator.stop module."""

from mse_cli.home.command.helpers import get_app_container, get_client_docker
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("restart", help="restart an stopped MSE docker")

    parser.add_argument(
        "name",
        type=str,
        help="the name of the application",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    client = get_client_docker()
    container = get_app_container(client, args.name)

    LOG.info("Restarting your application docker...")
    container.restart()
    LOG.info("Docker '%s' is now restarted!", args.name)
