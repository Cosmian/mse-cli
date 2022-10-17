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
    with Enclave() as enclave:
        # import your ciphered module normally
        import merge

        # convert input data bytes from DataProviders
        datas: Iterator[pd.DataFrame] = input_reader(enclave.read())

        # apply your secret function coded by the CodeProvider
        dataframe: pd.DataFrame = merge.merge_all(datas=datas, on="siren")

        # convert output result
        result: bytes = dataframe.to_csv(index=False, sep=SEP).encode("utf-8")

        # write result for ResultConsumers
        enclave.write(result)

    a = 2 + 3


if __name__ == "__main__":
    main()
