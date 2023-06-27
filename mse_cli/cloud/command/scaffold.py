"""mse_cli.cloud.command.scaffold module."""

from mse_cli.cloud.command.helpers import get_default, non_empty_string
from mse_cli.cloud.model.user import UserConf
from mse_cli.common.helpers import scaffold
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "scaffold", help="create a new boilerplate MSE web application"
    )

    parser.set_defaults(func=run)

    parser.add_argument(
        "app_name",
        type=non_empty_string,
        help="name of the MSE web application to create",
    )


# pylint: disable=too-many-locals
def run(args) -> None:
    """Run the subcommand."""
    user_conf = UserConf.load()
    conn = user_conf.get_connection()

    config = get_default(conn=conn)

    conf_file = scaffold(args.app_name, cloud_config=config)

    LOG.success(  # type: ignore
        "An example app has been generated in the directory: %s/", args.app_name
    )
    LOG.warning("You can configure your MSE application in: %s", conf_file)
    LOG.info(
        "You can now test it locally from the '%s/' directory using: "
        "\n\n\tmse cloud localtest\n",
        args.app_name,
    )
    LOG.advice(  # type: ignore
        "Or deploy it from the '%s/' directory using: \n\n\tmse cloud deploy\n",
        args.app_name,
    )
    LOG.info("Refer to the '%s/README.md' for more details", args.app_name)
