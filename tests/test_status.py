from typing import Optional

from mse_ctl import ComputationStatus, ComputationStatusType
from mse_ctl.computations import EnclaveStateType, EnclaveState

from keys import *


def test_not_started():
    json = "NotStarted"
    status = ComputationStatus(ComputationStatusType.NotStarted, None)
    assert status == ComputationStatus.from_json_dict(json)


def test_archived():
    json = "Archived"
    status = ComputationStatus(ComputationStatusType.Archived, None)
    assert status == ComputationStatus.from_json_dict(json)


def test_removed():
    json = "Removed"
    status = ComputationStatus(ComputationStatusType.Removed, None)
    assert status == ComputationStatus.from_json_dict(json)


def test_started_init():
    json = {
        "Started": {
            "Init": {
                "cache": {
                    "CodeProvider": "test",
                    "DataProvider": ["test2", "test3"],
                    "ResultConsumer": ["test4"],
                    "Enclave": ["test5"]
                },
                "code": True
            }
        }
    }

    status = ComputationStatus(
        ComputationStatusType.Started,
        EnclaveState(EnclaveStateType.Init, json["Started"]["Init"]))

    assert status == ComputationStatus.from_json_dict(json)


def test_started_running():
    json = {"Started": "Running"}
    status = ComputationStatus(ComputationStatusType.Started,
                               EnclaveState(EnclaveStateType.Running, None))
    assert status == ComputationStatus.from_json_dict(json)


def test_started_identity_success():
    json = {
        "Started": {
            "SetupInput": {
                "cp": True,
                "dps": [(True, False), (False, True)],
                "rcs": [True, True],
            }
        }
    }
    status = ComputationStatus(
        ComputationStatusType.Started,
        EnclaveState(EnclaveStateType.SetupInput,
                     json["Started"]["SetupInput"]))
    assert status == ComputationStatus.from_json_dict(json)
