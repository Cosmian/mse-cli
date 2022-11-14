#!/usr/bin/env python
"""MicroService Encryption Control (CLI)."""

from warnings import filterwarnings

filterwarnings("ignore")

import argparse

from mse_ctl.cli import (deploy, list_all, login, remove, scaffold, signup,
                         status, stop, verify)
from mse_ctl.log import setup_logging


def main():
    """Entrypoint of the CLI."""
    setup_logging(False)

    parser = argparse.ArgumentParser(
        description='Microservice Encryption Control.')

    subparsers = parser.add_subparsers(title='subcommands', required=True)

    deploy.add_subparser(subparsers)
    login.add_subparser(subparsers)
    remove.add_subparser(subparsers)
    scaffold.add_subparser(subparsers)
    signup.add_subparser(subparsers)
    status.add_subparser(subparsers)
    stop.add_subparser(subparsers)
    verify.add_subparser(subparsers)
    list_all.add_subparser(subparsers)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()