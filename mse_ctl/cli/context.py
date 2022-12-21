"""Context file manager subparser definition."""

from datetime import datetime
import shutil
import uuid
from pydantic import ValidationError

from toml import TomlDecodeError

from mse_ctl.conf.context import Context

from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors
from mse_ctl.utils.fs import ls


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("context",
                                   help="Manage your MSE context files")

    parser.set_defaults(func=run)

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        '--list',
        action='store_true',
        help='List the current saved context files from your store.')

    group.add_argument(
        '--clean',
        metavar="APP_UUID",
        type=uuid.UUID,
        help='The id of the MSE context to remove from your store.')

    group.add_argument('--purge',
                       action='store_true',
                       help='Remove all the MSE context files from your store.')

    group.add_argument(
        '--export',
        metavar="APP_UUID",
        type=uuid.UUID,
        help='Extract a context file from your store with all the data '
        'to share with an app user wishing to verify '
        'the trustworthiness of the app.')


def run(args) -> None:
    """Run the subcommand."""
    if args.clean:
        log.info("Removing context file for %s...", args.clean)
        Context.clean(args.clean)
        log.info("✅ %sContext file removed!%s", bcolors.OKGREEN, bcolors.ENDC)

    if args.list:
        for path in ls(Context.get_root_dirpath()):
            if path.is_file() and path.suffix == ".mse":
                try:
                    context = Context.from_toml(path)
                    log.info("%s -> %s%s-%s%s (%s)", context.instance.id,
                             bcolors.OKBLUE, context.config.name,
                             context.config.version, bcolors.ENDC,
                             datetime.fromtimestamp(path.stat().st_ctime))
                except (TypeError, TomlDecodeError, OSError, ValidationError):
                    log.info("%s -> %s[file format not supported]%s",
                             path.parent.name, bcolors.WARNING, bcolors.ENDC)

    if args.purge:
        log.info("Removing all the context files...")
        shutil.rmtree(Context.get_root_dirpath())
        log.info("✅ %sAll context files removed!%s", bcolors.OKGREEN,
                 bcolors.ENDC)

    if args.export:
        path = Context.get_context_filepath(args.export, create=False)
        target_filename = "context.mse"

        log.info("Exporting %s context in %s...", args.export, target_filename)
        if not path.exists():
            raise FileNotFoundError(f"Can't find context for app {args.export}")

        shutil.copyfile(path, target_filename)

        log.info("You can now transfer this file to your app user.")
