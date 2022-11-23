#!/usr/bin/env python
"""MicroService Encryption Control (CLI)."""

import sys
from warnings import filterwarnings  # noqa: E402

filterwarnings("ignore")  # noqa: E402

# pylint: disable=wrong-import-position

import argparse
import pkg_resources

from mse_ctl.cli import (context, deploy, list_all, login, init, remove,
                         scaffold, signup, status, stop, verify)
from mse_ctl.log import setup_logging


def main():
    """Entrypoint of the CLI."""
    setup_logging(False)

    parser = argparse.ArgumentParser(
        description='Microservice Encryption Control.')

    parser.add_argument('--version',
                        action='store_true',
                        help='The version of the CLI')

    subparsers = parser.add_subparsers(title='subcommands',
                                       required='--version' not in sys.argv)

    context.add_subparser(subparsers)
    deploy.add_subparser(subparsers)
    init.add_subparser(subparsers)
    list_all.add_subparser(subparsers)
    login.add_subparser(subparsers)
    remove.add_subparser(subparsers)
    scaffold.add_subparser(subparsers)
    signup.add_subparser(subparsers)
    status.add_subparser(subparsers)
    stop.add_subparser(subparsers)
    verify.add_subparser(subparsers)

    args = parser.parse_args()

    if args.version:
        print("Version:", pkg_resources.get_distribution("mse_ctl").version)
    else:
        args.func(args)


if __name__ == '__main__':
    main()
