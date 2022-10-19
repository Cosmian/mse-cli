"""Status subparser definition."""

import uuid
from pathlib import Path

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

    log.info("Fetching the enclave status for %s...", args.id)

    r: requests.Response = get(conn=user_conf.get_connection(), uuid=args.id)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    enclave = Enclave.from_json_dict(r.json())

    log.info("\nMicroservice")
    log.info("\tName        = %s", enclave.service_name)
    log.info("\tVersion     = %s", enclave.service_version)
    log.info("\tDomain name = %s", enclave.domain_name)

    log.info("\nDeployement status")
    log.info("\tUUID            = %s", enclave.uuid)
    log.info("\tSGX MSE lib     = %s", enclave.enclave_version)
    log.info("\tEnclave size    = %s", str(enclave.enclave_size))
    log.info("\tCode protection = %s", str(enclave.code_protection))
    log.info("\tCreated at      = %s", enclave.created_at)

    if enclave.status == EnclaveStatus.Running:
        log.info("\tStatus           = %s%s%s", bcolors.OKGREEN,
                 enclave.status.value, bcolors.ENDC)
        log.info("\tOnline since     = %s", enclave.ready_at)
    elif enclave.status == EnclaveStatus.Deleted:
        log.info("\tStatus           = %s%s%s", bcolors.WARNING,
                 enclave.status.value, bcolors.ENDC)
        log.info("\tOnline since     = %s", enclave.deleted_at)
    elif enclave.status == EnclaveStatus.OnError:
        log.info("\tStatus           = %s%s%s", bcolors.FAIL,
                 enclave.status.value, bcolors.ENDC)
    elif enclave.status == EnclaveStatus.Initializing:
        log.info("\tStatus           = %s%s%s", bcolors.OKBLUE,
                 enclave.status.value, bcolors.ENDC)
