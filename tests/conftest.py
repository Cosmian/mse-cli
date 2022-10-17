import os
from pathlib import Path
from typing import Dict, Tuple

import pytest
from mse_ctl import (ComputationOwnerAPI, CodeProviderAPI, DataProviderAPI,
                     ResultConsumerAPI, CryptoContext, Side)

from keys import *


def pytest_addoption(parser):
    parser.addoption("--cosmian_api_token",
                     action="store",
                     default=os.getenv("COSMIAN_TOKEN", default=""))
    parser.addoption("--cosmian_email_account",
                     action="store",
                     default=os.getenv("COSMIAN_ACCOUNT",
                                       default="alice@cosmian.com"))
    parser.addoption("--url",
                     action="store",
                     default=os.getenv("COSMIAN_BASE_URL",
                                       default="https://backend.cosmian.com"))


@pytest.fixture(scope="session")
def cosmian_api_token(pytestconfig):
    return pytestconfig.getoption("cosmian_api_token")


@pytest.fixture(scope="session")
def cosmian_email_account(pytestconfig):
    return pytestconfig.getoption("cosmian_email_account")


@pytest.fixture(scope="module")
def cp_root_path():
    return Path(__file__).parent / "data" / "cp"


@pytest.fixture(scope="module")
def code_path():
    return Path(__file__).parent / "data" / "cp" / "enclave-join"


@pytest.fixture(scope="module")
def dp1_root_path():
    return Path(__file__).parent / "data" / "dp1"


@pytest.fixture(scope="module")
def dp2_root_path():
    return Path(__file__).parent / "data" / "dp2"


@pytest.fixture(scope="module")
def rc_root_path():
    return Path(__file__).parent / "data" / "rc"


@pytest.fixture(scope="module")
def words():
    return ("cargo", "error", "thank")


@pytest.fixture(scope="module")
def co(cosmian_api_token):
    yield ComputationOwnerAPI(token=cosmian_api_token)


@pytest.fixture(scope="module")
def computation_uuid(co, cosmian_email_account):
    computation = co.create_computation(
        name="test-e2e-secure-computation",
        code_provider_email=f"{cosmian_email_account}",
        data_providers_emails=[f"{cosmian_email_account}"],
        result_consumers_emails=[f"{cosmian_email_account}"])

    yield computation.uuid


@pytest.fixture(scope="module")
def cp(cosmian_api_token, words, computation_uuid):
    cp_ctx = CryptoContext.from_dict({
        "computation_uuid": computation_uuid,
        "side": "CodeProvider",
        "words": words,
        "ed25519_seed": CP_ED25519_SEED,
        "symkey": CP_SYMKEY
    })
    cp = CodeProviderAPI(token=cosmian_api_token, ctx=cp_ctx)

    yield cp


@pytest.fixture(scope="module")
def dp1(cosmian_api_token, words, computation_uuid):
    dp1_ctx = CryptoContext.from_dict({
        "computation_uuid": computation_uuid,
        "side": "DataProvider",
        "words": words,
        "ed25519_seed": DP1_ED25519_SEED,
        "symkey": DP1_SYMKEY
    })
    dp1 = DataProviderAPI(token=cosmian_api_token, ctx=dp1_ctx)

    yield dp1


@pytest.fixture(scope="module")
def dp2(cosmian_api_token, words, computation_uuid):
    dp2_ctx = CryptoContext.from_dict({
        "computation_uuid": computation_uuid,
        "side": "DataProvider",
        "words": words,
        "ed25519_seed": DP2_ED25519_SEED,
        "symkey": DP2_SYMKEY
    })
    dp2 = DataProviderAPI(token=cosmian_api_token, ctx=dp2_ctx)

    yield dp2


@pytest.fixture(scope="module")
def rc(cosmian_api_token, words, computation_uuid):
    rc_ctx = CryptoContext.from_dict({
        "computation_uuid": computation_uuid,
        "side": "ResultConsumer",
        "words": words,
        "ed25519_seed": RC_ED25519_SEED,
        "symkey": RC_SYMKEY
    })
    rc = ResultConsumerAPI(token=cosmian_api_token, ctx=rc_ctx)

    yield rc


_test_failed_incremental: Dict[str, Dict[Tuple[int, ...], str]] = {}


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            cls_name = str(item.cls)
            parametrize_index = (tuple(item.callspec.indices.values())
                                 if hasattr(item, "callspec") else ())
            test_name = item.originalname or item.name
            _test_failed_incremental.setdefault(cls_name, {}).setdefault(
                parametrize_index, test_name)


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        cls_name = str(item.cls)
        if cls_name in _test_failed_incremental:
            parametrize_index = (tuple(item.callspec.indices.values())
                                 if hasattr(item, "callspec") else ())
            test_name = _test_failed_incremental[cls_name].get(
                parametrize_index, None)
            if test_name is not None:
                pytest.xfail("previous test failed ({})".format(test_name))
