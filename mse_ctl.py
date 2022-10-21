"""MicroService Encryption Control (CLI)."""

import argparse

from mse_ctl.cli import (deploy, login, remove, scaffold, signup, status, stop,
                         verify)
from mse_ctl.log import setup_logging

if __name__ == '__main__':
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

    args = parser.parse_args()
    args.func(args)
