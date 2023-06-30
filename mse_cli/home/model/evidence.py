"""mse_cli.home.model.evidence module."""

import base64
import json
from pathlib import Path
from typing import Any, Dict, Tuple

from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)
from cryptography.x509 import (
    Certificate,
    CertificateRevocationList,
    load_pem_x509_certificate,
    load_pem_x509_crl,
)
from pydantic import BaseModel

from mse_cli.core.no_sgx_docker import NoSgxDockerConfig


class ApplicationEvidence(BaseModel):
    """Definition of an enclave evidence."""

    ratls_certificate: Certificate
    root_ca_crl: CertificateRevocationList
    pck_platform_crl: CertificateRevocationList
    tcb_info: bytes
    qe_identity: bytes
    tcb_cert: Certificate
    signer_pk: PublicKeyTypes
    input_args: NoSgxDockerConfig

    class Config:
        """Overwrite internal structure."""

        arbitrary_types_allowed = True

    @property
    def collaterals(
        self,
    ) -> Tuple[
        bytes, bytes, Certificate, CertificateRevocationList, CertificateRevocationList
    ]:
        """Return the PCCS collaterals."""
        return (
            self.tcb_info,
            self.qe_identity,
            self.tcb_cert,
            self.root_ca_crl,
            self.pck_platform_crl,
        )

    @staticmethod
    def load(path: Path):
        """Load the evidence from a json file."""
        with open(path, encoding="utf8") as f:
            data_map = json.load(f)

            return ApplicationEvidence(
                input_args=NoSgxDockerConfig(**data_map["input_args"]),
                ratls_certificate=load_pem_x509_certificate(
                    data_map["ratls_certificate"].encode("utf-8")
                ),
                root_ca_crl=load_pem_x509_crl(data_map["root_ca_crl"].encode("utf-8")),
                pck_platform_crl=load_pem_x509_crl(
                    data_map["pck_platform_crl"].encode("utf-8")
                ),
                tcb_info=base64.b64decode(data_map["tcb_info"].encode("utf-8")),
                qe_identity=base64.b64decode(data_map["qe_identity"].encode("utf-8")),
                tcb_cert=load_pem_x509_certificate(
                    data_map["tcb_cert"].encode("utf-8")
                ),
                signer_pk=load_pem_public_key(
                    data_map["signer_pk"].encode("utf-8"),
                ),
            )

    def save(self, path: Path) -> None:
        """Save the evidence into a json file."""
        with open(path, "w", encoding="utf8") as f:
            data_map: Dict[str, Any] = {
                "input_args": {
                    "subject": self.input_args.subject,
                    "subject_alternative_name": self.input_args.subject_alternative_name,
                    "expiration_date": self.input_args.expiration_date
                    if self.input_args.expiration_date
                    else None,
                    "size": self.input_args.size,
                    "app_id": str(self.input_args.app_id),
                    "application": self.input_args.application,
                },
                "ratls_certificate": self.ratls_certificate.public_bytes(
                    encoding=Encoding.PEM
                ).decode("utf-8"),
                "root_ca_crl": self.root_ca_crl.public_bytes(
                    encoding=Encoding.PEM,
                ).decode("utf-8"),
                "pck_platform_crl": self.pck_platform_crl.public_bytes(
                    encoding=Encoding.PEM,
                ).decode("utf-8"),
                "tcb_info": base64.b64encode(self.tcb_info).decode("utf-8"),
                "qe_identity": base64.b64encode(self.qe_identity).decode("utf-8"),
                "tcb_cert": self.tcb_cert.public_bytes(encoding=Encoding.PEM).decode(
                    "utf-8"
                ),
                "signer_pk": self.signer_pk.public_bytes(
                    encoding=Encoding.PEM,
                    format=PublicFormat.SubjectPublicKeyInfo,
                ).decode("utf-8"),
            }

            json.dump(data_map, f, indent=4)
