"""mse_cli.home.command.sgx_operator.list module."""

from mse_cli.core.sgx_docker import SgxDockerConfig
from mse_cli.home.command.helpers import get_client_docker
from mse_cli.log import LOGGER as LOG


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("list", help="list the running MSE applications")

    parser.set_defaults(func=run)


def run(_args) -> None:
    """Run the subcommand."""
    client = get_client_docker()

    containers = client.containers.list(
        all=True, filters={"label": SgxDockerConfig.docker_label}
    )

    LOG.info(
        "\n %s | %s | %s [Image name] ",
        "Started at".center(29),
        "Status".center(10),
        "Application name",
    )
    LOG.info(("-" * 86))

    for container in containers:
        LOG.info(
            "%30s | %s | %s [%s]",
            container.attrs["State"]["StartedAt"],
            container.status.center(10),
            container.name,
            container.image.tags[0],
        )
