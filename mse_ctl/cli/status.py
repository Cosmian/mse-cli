"""Status subparser definition."""

from pathlib import Path
import uuid

import requests
from mse_ctl.api.enclave import get
from mse_ctl.api.types import Enclave, EnclaveStatus

from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log
from mse_ctl.utils.color import bcolors


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("status",
                                   help="Print the status of a MSE enclave ")

    parser.set_defaults(func=run)

    parser.add_argument('--id',
                        required=True,
                        type=uuid.UUID,
                        help='The id of the MSE enclave.')


def run(args):
    """Run the subcommand."""
    user_conf = UserConf.from_toml()

    log.info(f"Fetching the enclave status for {args.id}...")

    r: requests.Response = get(conn=user_conf.get_connection(), uuid=args.id)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    enclave = Enclave.from_json_dict(r.json())

    log.info("\nMicroservice")
    log.info(f"\tName        = {enclave.name}")
    log.info(f"\tVersion     = {enclave.version}")
    log.info(f"\tDomain name = {enclave.domain_name}")

    log.info("\nDeployement status")
    log.info(f"\tUUID         = {enclave.uuid}")

    log.info(f"\tCreated at   = {enclave.created_at}")

    if enclave.status == EnclaveStatus.Running:
        log.info(
            f"\tStatus       = {bcolors.OKGREEN}{enclave.status.value}{bcolors.ENDC}"
        )
        log.info(f"\tOnline since = {enclave.ready_at}")
    elif enclave.status == EnclaveStatus.Deleted:
        log.info(
            f"\tStatus       = {bcolors.WARNING}{enclave.status.value}{bcolors.ENDC}"
        )
        log.info(f"\tOnline since = {enclave.deleted_at}")
    elif enclave.status == EnclaveStatus.OnError:
        log.info(
            f"\tStatus       = {bcolors.FAIL}{enclave.status.value}{bcolors.ENDC}"
        )
    elif enclave.status == EnclaveStatus.Initializing:
        log.info(
            f"\tStatus       = {bcolors.OKBLUE}{enclave.status.value}{bcolors.ENDC}"
        )
