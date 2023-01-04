"""mse_ctl.cli.context module."""

import shutil
from uuid import UUID
from datetime import datetime
from pathlib import Path

from pydantic import ValidationError
from toml import TomlDecodeError

from mse_ctl.conf.context import Context
from mse_ctl.log import LOGGER as LOG
from mse_ctl.utils.color import bcolors
from mse_ctl.utils.fs import ls


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser(
        "context", help="manage context of your deployed applications")

    parser.set_defaults(func=run)

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--list",
                       action="store_true",
                       help="list application contexts")

    group.add_argument("--remove",
                       metavar="UUID",
                       type=UUID,
                       help="remove specific application context")

    group.add_argument("--purge",
                       action="store_true",
                       help="remove all context")

    group.add_argument(
        "--export",
        metavar="UUID",
        type=UUID,
        help="export specific context to toml file (for migration or to "
        "verify the trustworthiness of an MSE app by a third party)")


def run(args) -> None:
    """Run the subcommand."""
    if args.remove:
        LOG.info("Removing context %s...", args.remove)
        Context.clean(args.remove)
        LOG.info("✅%sContext successfully removed%s", bcolors.OKGREEN,
                 bcolors.ENDC)

    if args.list:
        for path in ls(Context.get_root_dirpath()):
            if path.is_file() and path.suffix == ".mse":
                try:
                    context = Context.from_toml(path)
                    LOG.info("%s -> %s%s-%s%s (%s)", context.instance.id,
                             bcolors.OKBLUE, context.config.name,
                             context.config.version, bcolors.ENDC,
                             datetime.fromtimestamp(path.stat().st_ctime))
                except (TypeError, TomlDecodeError, OSError, ValidationError):
                    LOG.info("%s -> %s[file format not supported]%s",
                             path.parent.name, bcolors.WARNING, bcolors.ENDC)

    if args.purge:
        LOG.info("Removing all contexts...")
        shutil.rmtree(Context.get_root_dirpath())
        LOG.info("✅%sAll context successfully removed%s", bcolors.OKGREEN,
                 bcolors.ENDC)

    if args.export:
        uuid: UUID = args.export
        context_path: Path = Context.get_context_filepath(uuid, create=False)

        if not context_path.exists():
            raise FileNotFoundError(f"Can't find context for UUID: {uuid}")

        target_filename: str = f"{uuid}.toml"

        LOG.info("Exporting context to %s...", target_filename)
        shutil.copyfile(context_path, target_filename)
        LOG.info("✅%sContext successfully exported%s", bcolors.OKGREEN,
                 bcolors.ENDC)
