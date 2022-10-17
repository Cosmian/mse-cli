from dataclasses import dataclass
import hashlib
import pytest
from typing import Optional

# from cosmian_secure_computation_client import azure_remote_attestation

from keys import *


@dataclass
class State:
    enclave_public_key: Optional[bytes]
    compressed_code_hash: Optional[bytes]


@pytest.mark.slow
@pytest.mark.incremental
class TestAPI:

    @staticmethod
    @pytest.fixture(autouse=True, scope="class")
    def state() -> State:
        return State(enclave_public_key=None, compressed_code_hash=None)

    @staticmethod
    def test_register(computation_uuid, cp, dp1, rc):
        cp.register(computation_uuid)
        dp1.register(computation_uuid)
        rc.register(computation_uuid)

        computation = cp.get_computation(computation_uuid)

        assert computation.code_provider.public_key is not None
        assert computation.data_providers[0].public_key is not None  # dp1
        assert computation.result_consumers[0].public_key is not None

        assert bytes.fromhex(
            computation.code_provider.public_key.content) == CP_ED25519_PUBKEY
        assert bytes.fromhex(computation.data_providers[0].public_key.content
                            ) == DP1_ED25519_PUBKEY
        assert bytes.fromhex(computation.result_consumers[0].public_key.content
                            ) == RC_ED25519_PUBKEY

    @staticmethod
    def test_cp_upload(state, computation_uuid, cp, code_path):
        tar_path = cp.upload_code(computation_uuid=computation_uuid,
                                  directory_path=code_path)

        state.compressed_code_hash = hashlib.sha256(
            tar_path.read_bytes()).digest()

        computation = cp.get_computation(computation_uuid)

        assert computation.code_provider.code_uploaded_at is not None

    @staticmethod
    def test_identity_and_remote_attestation(state, computation_uuid, cp):
        enclave_public_key: bytes = cp.wait_for_enclave_identity(
            computation_uuid)
        state.enclave_public_key = enclave_public_key
        hash_enclave_pk: bytes = hashlib.sha256(enclave_public_key).digest()

        computation = cp.get_computation(computation_uuid)

        assert computation.enclave is not None
        assert computation.enclave.identity is not None
        assert computation.enclave.identity.public_key == enclave_public_key

        # quote = computation.enclave.identity.quote
        # response = azure_remote_attestation(quote)

        # assert response["tee"] == "sgx"
        # assert response["x-ms-sgx-is-debuggable"] is False
        # assert response["x-ms-sgx-product-id"] == 0
        # assert response["x-ms-sgx-svn"] == 0
        # assert response["x-ms-attestation-type"] == "sgx"

        # print(f"MRENCLAVE: {response['x-ms-sgx-mrenclave']}")
        # print(f"MRSIGNER: {response['x-ms-sgx-mrsigner']}")
        # print(f"Enclave pk: {enclave_public_key.hex()}")
        # print(f"SHA-256(Enclave pk): {hash_enclave_pk.hex()}")
        # print(f"Report User Data: {response['x-ms-sgx-report-data']}")

    @staticmethod
    def test_dp_download(state, tmp_path_factory, computation_uuid, dp1):
        out_dir_path = tmp_path_factory.mktemp("code")
        tar_path = dp1.download_code(computation_uuid=computation_uuid,
                                     directory_path=out_dir_path)

        assert state.compressed_code_hash is not None
        compressed_code_hash = hashlib.sha256(tar_path.read_bytes()).digest()
        assert compressed_code_hash == state.compressed_code_hash

    def test_dp_upload(self, computation_uuid, dp1, dp1_root_path,
                       dp2_root_path):
        dp1.upload_files(computation_uuid=computation_uuid,
                         paths=dp1_root_path.glob("*"))
        dp1.upload_files(computation_uuid=computation_uuid,
                         paths=dp2_root_path.glob("*"))
        dp1.done(computation_uuid)

    @staticmethod
    def test_key_provisioning(state, computation_uuid, cp, dp1, rc):
        assert state.enclave_public_key is not None

        cp.key_provisioning(computation_uuid=computation_uuid,
                            enclave_public_key=state.enclave_public_key)
        dp1.key_provisioning(computation_uuid=computation_uuid,
                             enclave_public_key=state.enclave_public_key)
        rc.key_provisioning(computation_uuid=computation_uuid,
                            enclave_public_key=state.enclave_public_key)

    @staticmethod
    def test_run(computation_uuid, rc, rc_root_path):
        result = rc.wait_result(computation_uuid)

        assert result == (rc_root_path / "result.csv").read_bytes()
