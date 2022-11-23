"""Context file manager subparser definition."""

from datetime import datetime
import uuid
import tarfile

from mse_ctl.conf.context import Context

from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors
from mse_ctl.utils.fs import ls


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

    group.add_argument('--clean-all',
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
        Context.get_exported_path(args.clean).unlink(missing_ok=True)

    if args.list:
        for path in ls(Context.get_context_path()):
            if path.is_file() and path.suffix == ".mse":
                try:
                    context = Context.from_toml(path)
                    log.info("%s -> %s%s-%s%s (%s)", path.name, bcolors.OKBLUE,
                             context.config.name, context.config.version,
                             bcolors.ENDC,
                             datetime.fromtimestamp(path.stat().st_ctime))
                except Exception:
                    log.info("%s -> %s[file format not supported]%s", path.name,
                             bcolors.WARNING, bcolors.ENDC)

    if args.clean_all:
        for path in ls(Context.get_context_path()):
            log.info("Removing context file %s...", path.name)
            path.unlink(missing_ok=True)

    if args.export:
        path = Context.get_exported_path(args.export)
        tar_filename = "context.tar"
        print(path)
        log.info("Exporting %s context in %s...", args.export, tar_filename)
        if not path.exists():
            raise FileNotFoundError(
                f"Can't find context file for app {args.export}")
        with tarfile.open(tar_filename, "w:") as tar_file:
            tar_file.add(path, path.name)
