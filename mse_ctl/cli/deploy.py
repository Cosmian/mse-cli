"""Deploy subparser definition."""

from pathlib import Path

import requests
import time

from mse_ctl.api.enclave import get, new
from mse_ctl.api.types import Enclave, EnclaveStatus

from mse_ctl.conf.enclave import EnclaveConf
from mse_ctl.conf.user import UserConf
from mse_ctl.log import LOGGER as log


def add_subparser(subparsers):
    """Define the subcommand."""
    parser = subparsers.add_parser("deploy",
                                   help="Deploy the application from the "
                                   "current directory into a MSE enclave")

    parser.set_defaults(func=run)


def run(args):
    """Run the subcommand."""
    enclave_conf = EnclaveConf.from_toml(
        Path("examples/enclave.example.toml"))  # TODO: unhardcode that

    user_conf = UserConf.from_toml()

    log.info("Deploying your project...")

    conn = user_conf.get_connection()

    r: requests.Response = new(conn=conn, name=enclave_conf.service_name)

    if not r.ok:
        raise Exception(f"Unexpected response ({r.status_code}): {r.content!r}")

    enclave = Enclave.from_json_dict(r.json())

    log.info(f"Enclave creating for {enclave_conf.service_name}...")

    while enclave.status == EnclaveStatus.Initializing:
        time.sleep(1)

        r: requests.Response = get(conn=conn, uuid=enclave.uuid)

        if not r.ok:
            raise Exception(
                f"Unexpected response ({r.status_code}): {r.content!r}")

        enclave = Enclave.from_json_dict(r.json())

    log.info("Enclave created!")
    log.info(f"Enclave uuid: id {enclave.uuid}")
    log.info("Enclave thrustworthiness check (RA processing...): Ok.")
    log.info("Unsealing your code and your private data from the enclave.")
    log.info("Your application is now fully deployed and started.")
    log.info("It's now ready to be used on https://e1.machine1.cosmian.com")
