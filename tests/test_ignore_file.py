"""Test ignore_file.py."""

from pathlib import Path

from mse_cli.core.ignore_file import IgnoreFile


def test_ignore_file():
    """Test `IgnoreFile`."""
    ignored_files = IgnoreFile.parse(Path(__file__).parent / "data")

    expected_patterns = {
        "mse.toml",
        "secrets.json",
        ".mseignore",
        "__pycache__/",
        ".git*",
        ".vscode/",
        ".idea/",
        "*.egg-info/",
        "*.egg",
        ".venv",
        ".env",
    }

    assert ignored_files == expected_patterns
