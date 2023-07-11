"""Test helpers functions."""

from pathlib import Path

from mse_cli.home.command.sgx_operator.evidence import guess_pccs_url


def test_guess_pccs_url():
    """Test guess_pccs_url."""
    conf = Path(__file__).parent / "data/sgx_default_qcnl.conf"

    assert guess_pccs_url(aemsd_conf_file=conf) == "https://example.cosmian.com"
