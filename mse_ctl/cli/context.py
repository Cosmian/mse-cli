"""Context file manager subparser definition."""

from datetime import datetime
import shutil
import uuid
import tarfile

from mse_ctl.conf.context import Context

from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors
from mse_ctl.utils.fs import ls, tar


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("context",
                                   help="Manage your mse context files")

    parser.set_defaults(func=run)

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--list',
                       action='store_true',
                       help='List the current saved context files.')

    group.add_argument('--clean',
                       metavar="APP_UUID",
                       type=uuid.UUID,
                       help='The id of the MSE context to remove.')

    group.add_argument('--purge',
                       action='store_true',
                       help='Remove all the MSE context files.')

    group.add_argument('--export',
                       metavar="APP_UUID",
                       type=uuid.UUID,
                       help='Create a tar file with all the context data '
                       'to share with an app user wishing to verify '
                       'the trustworthiness of the app.')


def run(args):
    """Run the subcommand."""
    if args.clean:
        log.info("Removing context file for %s...", args.clean)
        Context.clean(args.clean)

    if args.list:
        for path in ls(Context.get_root_dirpath()):
            if path.is_file() and path.suffix == ".mse":
                try:
                    context = Context.from_toml(path)
                    log.info("%s -> %s%s-%s%s (%s)", context.instance.id,
                             bcolors.OKBLUE, context.config.name,
                             context.config.version, bcolors.ENDC,
                             datetime.fromtimestamp(path.stat().st_ctime))
                except Exception:
                    log.info("%s -> %s[file format not supported]%s",
                             path.parent.name, bcolors.WARNING, bcolors.ENDC)

    if args.purge:
        log.info("Removing all the context files...")
        shutil.rmtree(Context.get_root_dirpath())

    if args.export:
        path = Context.get_dirpath(args.export)
        tar_filename = "context.tar"
        log.info("Exporting %s context in %s...", args.export, tar_filename)
        if not path.exists():
            raise FileNotFoundError(f"Can't find context for app {args.export}")

        tar(path, tar_filename)
        log.info("You can now transfert this file to your app user.")
