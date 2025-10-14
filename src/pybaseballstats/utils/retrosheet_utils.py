from functools import lru_cache

import polars as pl
import requests

from pybaseballstats.consts.retrosheet_consts import (
    PEOPLES_URL,
    RETROSHEET_KEEP_COLS,
)


@lru_cache(maxsize=1)
def _get_people_data() -> pl.DataFrame:
    df_list = []
    for i in range(0, 10):
        data = requests.get(PEOPLES_URL.format(num=i)).content
        df = pl.read_csv(data, truncate_ragged_lines=True)
        df = df.select(pl.col(RETROSHEET_KEEP_COLS))
        df_list.append(df)

    for letter in ["a", "b", "c", "d", "f"]:
        data = requests.get(PEOPLES_URL.format(num=letter)).content
        df = pl.read_csv(data, truncate_ragged_lines=True)
        df = df.select(pl.col(RETROSHEET_KEEP_COLS))
        df_list.append(df)

    df = df_list[0]
    for i in range(1, len(df_list)):
        df = df.vstack(df_list[i])
    df = df.drop_nulls(RETROSHEET_KEEP_COLS)
    df = df.with_columns(
        [
            pl.col("name_last").str.to_lowercase().alias("name_last"),
            pl.col("name_first").str.to_lowercase().alias("name_first"),
        ]
    )
    return df
