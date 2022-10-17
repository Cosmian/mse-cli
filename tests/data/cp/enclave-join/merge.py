"""merge module."""

from typing import Iterator

import pandas as pd


def merge_all(datas: Iterator[pd.DataFrame], on: str) -> pd.DataFrame:
    """Inner join of DataFrames in `datas`."""
    dataframe: pd.DataFrame

    try:
        dataframe = next(datas)
    except StopIteration as exc:
        raise Exception("No input data!") from exc

    for data in datas:  # type: pd.DataFrame
        dataframe = pd.merge(
            dataframe,
            data,
            how="inner",
            on=on
        )

    return dataframe
