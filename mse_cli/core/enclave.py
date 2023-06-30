"""mse_cli.core.enclave module."""

import logging
import re
import uuid
from pathlib import Path
from typing import Optional, Tuple, Union

from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.x509 import Certificate, CertificateRevocationList
from docker.client import DockerClient
from docker.errors import NotFound
from intel_sgx_ra.attest import verify_quote
from intel_sgx_ra.maa.attest import verify_quote as azure_verify_quote
from intel_sgx_ra.ratls import ratls_verify
from intel_sgx_ra.signer import mr_signer_from_pk

from mse_cli.core.no_sgx_docker import NoSgxDockerConfig
from mse_cli.error import (
    AppContainerError,
    RatlsVerificationFailure,
    WrongMREnclave,
    WrongMRSigner,
)


def compute_mr_enclave(
    client: DockerClient,
    image: str,
    app_args: NoSgxDockerConfig,
    app_path: Path,
    docker_path_log: Path,
) -> str:
    """Compute the MR enclave."""
    container_name = str(uuid.uuid4())
    output = b""

    try:
        _ = client.containers.run(
            image,
            name=container_name,
            command=app_args.cmd(),
            volumes=app_args.volumes(app_path),
            entrypoint=NoSgxDockerConfig.entrypoint,
            # We do not remove the container to be able to print the error (if some)
            remove=False,
            detach=False,
            stdout=True,
            stderr=True,
        )
    except Exception as exc:
        raise AppContainerError(
            f"Error starting the docker (see logs at {docker_path_log})"
        ) from exc
    finally:
        try:
            container = client.containers.get(container_name)
            # Save the docker output
            output = container.logs()
            docker_path_log.write_bytes(output)
            container.stop(timeout=1)
            # We need to remove the container since we declare remove=False previously
            container.remove()

        except NotFound:
            pass

    # Get the mr_enclave from the docker output
    pattern = "Measurement:\n[ ]*([a-z0-9]{64})"
    m = re.search(pattern.encode("utf-8"), output)

    if not m:
        raise RatlsVerificationFailure(
            f"Fail to compute mr_enclave! See {docker_path_log} for more details."
        )

    return str(m.group(1).decode("utf-8"))


def verify_enclave(
    signer_pk: Union[RSAPublicKey, Path, bytes],
    ratls_certificate: Union[str, bytes, Path, Certificate],
    fingerprint: Optional[str],
    collaterals: Optional[
        Tuple[
            bytes,
            bytes,
            Certificate,
            CertificateRevocationList,
            CertificateRevocationList,
        ]
    ] = None,
    pccs_url: Optional[str] = None,
):
    """Verify an enclave trustworthiness."""
    # Compute MRSIGNER value from public key
    mrsigner = mr_signer_from_pk(signer_pk)

    # Check certificate's public key in quote's user report data
    quote = ratls_verify(ratls_certificate)

    # Check MRSIGNER
    if quote.report_body.mr_signer != mrsigner:
        raise WrongMRSigner(
            "Enclave signer is wrong "
            f"(read {bytes(quote.report_body.mr_signer).hex()} "
            f"but should be {bytes(mrsigner).hex()})"
        )

    logging.info("MRSIGNER: %s", quote.report_body.mr_signer.hex())
    logging.info("MRENCLAVE: %s", quote.report_body.mr_enclave.hex())

    if collaterals is None and pccs_url is None:
        # Azure DCAP attestation through MAA service
        azure_verify_quote(quote=quote)
    else:
        # Intel DCAP attestation using PCCS url or directly collaterals if provided
        verify_quote(quote=quote, collaterals=collaterals, pccs_url=pccs_url)

    # Check MRENCLAVE
    if fingerprint:
        if quote.report_body.mr_enclave != bytes.fromhex(fingerprint):
            raise WrongMREnclave(
                "Code fingerprint is wrong "
                f"(read {bytes(quote.report_body.mr_enclave).hex()} "
                f"but should be {fingerprint})"
            )
