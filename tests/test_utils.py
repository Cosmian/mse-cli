from mse_ctl.utils.entrypoint import (validate_entrypoint, IMPORT_TEMPLATE,
                                      IF_MAIN_TEMPLATE, ENTRYPOINT_TEMPLATE)
from pathlib import Path

from keys import *

import pytest


def test_valid_runpy():
    validate_entrypoint(Path("tests/data/cp/enclave-join/run.py"))
    assert True


def test_invalid_syntax_runpy():
    with pytest.raises(IndentationError) as context:
        validate_entrypoint(Path("tests/data/cp/unit-test/invalidsyntax.py"))

    assert str(context.value).find("unexpected indent") != -1


def test_invalid_noimport_runpy():
    with pytest.raises(Exception) as context:
        validate_entrypoint(Path("tests/data/cp/unit-test/noimport.py"))

    assert str(context.value).endswith(IMPORT_TEMPLATE)


def test_invalid_nowith_runpy():
    with pytest.raises(Exception) as context:
        validate_entrypoint(Path("tests/data/cp/unit-test/nowith.py"))

    assert str(context.value).endswith(ENTRYPOINT_TEMPLATE)


def test_invalid_noifmain_runpy():
    with pytest.raises(Exception) as context:
        validate_entrypoint(Path("tests/data/cp/unit-test/noifmain.py"))

    assert str(context.value).endswith(IF_MAIN_TEMPLATE)


def test_invalid_extrastatement_runpy():
    with pytest.raises(Exception) as context:
        validate_entrypoint(Path("tests/data/cp/unit-test/extrastatement.py"))

    assert str(context.value).endswith(ENTRYPOINT_TEMPLATE)


def test_invalid_noreturn_runpy():
    with pytest.raises(Exception) as context:
        validate_entrypoint(Path("tests/data/cp/unit-test/noreturn.py"))

    assert str(context.value).endswith(ENTRYPOINT_TEMPLATE)


def test_invalid_extraifmain_runpy():
    with pytest.raises(Exception) as context:
        validate_entrypoint(Path("tests/data/cp/unit-test/extraifmain.py"))

    assert str(context.value).endswith(IF_MAIN_TEMPLATE)


def test_invalid_badifmain_runpy():
    with pytest.raises(Exception) as context:
        validate_entrypoint(Path("tests/data/cp/unit-test/badifmain.py"))

    assert str(context.value).endswith(IF_MAIN_TEMPLATE)
