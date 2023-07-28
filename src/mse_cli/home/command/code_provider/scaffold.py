"""mse_cli.home.command.code_provider.scaffold module."""


from mse_cli.common.helpers import scaffold
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "scaffold", help="create a new boilerplate MSE application"
    )

    parser.add_argument(
        "app_name",
        type=str,
        help="name of the MSE application to create",
    )

    parser.set_defaults(func=run)


def run(args) -> None:
    """Run the subcommand."""
    conf_file = scaffold(args.app_name)

    LOG.info(  # type: ignore
        "An example app has been generated in the directory: %s/", args.app_name
    )
    LOG.warning("You can configure your MSE application in: %s", conf_file)
