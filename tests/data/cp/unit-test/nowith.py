"""run module."""

from io import BytesIO
from typing import Iterator

import pandas as pd

from cosmian_lib_sgx import Enclave

SEP: str = ";"


def input_reader(datas: Iterator[BytesIO]) -> Iterator[pd.DataFrame]:
    """Transform input data bytes to pandas DataFrame."""
    for data in datas:  # type: BytesIO
        yield pd.read_csv(data, sep=SEP)


def main() -> int:
    """Entrypoint of your code."""
    3 + 2

    return 0


if __name__ == "__main__":
    main()
