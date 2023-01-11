"""mse_cli.utils.fs module."""

import tarfile
from pathlib import Path
from typing import Iterator


def is_hidden(path: Path) -> bool:
    """Check if `path` contains parts with hidden file or folder.

    Parameters
    ----------
    path : Path
        Path to check if any part is hidden.

    Returns
    -------
    bool
        True if any part of `path` is hidden, False otherwise.

    """
    return any((part.startswith(".") for part in path.parts))


def ls(dir_path: Path, dot_files: bool = False) -> Iterator[Path]:
    """Recursive listing of files `dir_path`.

    Parameters
    ----------
    dir_path : Path
        Path to the directory.
    dot_files : bool
        Whether you want to list dot files.

    Yields
    -------
    Path
        Path to a file within `dir_path`.

    """
    for path in sorted(dir_path.absolute().rglob("*")):  # type: Path
        if path.is_file():
            if not dot_files and not is_hidden(path.relative_to(dir_path)):
                yield path


def tar(dir_path: Path, tar_path: Path, dot_files: bool = False) -> Path:
    """Tar directory `dir_path` to `tar_path`.

    Parameters
    ----------
    dir_path : Path
        Directory path to tar.
    tar_path : Path
        Path to output the tar file created.
    dot_files : bool

    Returns
    -------
    Path
        Path to the tar file created.

    """
    with tarfile.open(tar_path, "w:") as tar_file:
        for path in ls(dir_path, dot_files):
            rel_path: Path = path.relative_to(dir_path)
            tar_file.add(path, rel_path)

    return tar_path


def untar(dir_path: Path, tar_file: Path):
    """Untar file `tar_file` to `dir_path`.

    Parameters
    ----------
    dir_path : Path
        Directory output path.
    tar_file : Path
        Path to of the tar file to untar.

    """
    with tarfile.open(tar_file, "r:") as f:
        f.extractall(dir_path)
