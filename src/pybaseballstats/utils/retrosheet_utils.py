from functools import lru_cache

import polars as pl
import requests

from pybaseballstats.consts.retrosheet_consts import (
    PEOPLES_URL,
    RETROSHEET_KEEP_COLS,
)


@lru_cache(maxsize=1)
def _get_people_data() -> pl.DataFrame:
    """Fetch and cache people data from Retrosheet."""
    df_list = []
    for i in range(0, 10):
        data = requests.get(PEOPLES_URL.format(num=i)).content
        df = pl.read_csv(data)
        df = df.select(pl.col(RETROSHEET_KEEP_COLS))
        df_list.append(df)

    for letter in ["a", "b", "c", "d", "f"]:
        data = requests.get(PEOPLES_URL.format(num=letter)).content
        df = pl.read_csv(data)
        df = df.select(pl.col(RETROSHEET_KEEP_COLS))
        df_list.append(df)

    df = pl.concat(df_list)
    # Drop rows where ALL name fields are null
    df = df.filter(
        pl.col("name_last").is_not_null() & pl.col("name_first").is_not_null()
    )

    # Drop rows where keys are null
    for key_col in [
        "key_fangraphs",
        "key_mlbam",
        "key_retro",
        "key_bbref",
    ]:
        df = df.filter(pl.col(key_col).is_not_null())

    # Normalize name columns to lowercase
    df = df.with_columns(
        [
            pl.col("name_last").str.to_lowercase().alias("name_last_lower"),
            pl.col("name_first").str.to_lowercase().alias("name_first_lower"),
            pl.col("name_given").str.to_lowercase().alias("name_given_lower"),
            pl.col("name_nick").str.to_lowercase().alias("name_nick_lower"),
            pl.col("name_matrilineal")
            .str.to_lowercase()
            .alias("name_matrilineal_lower"),
            pl.col("name_suffix").str.to_lowercase().alias("name_suffix_lower"),
        ]
    )
    return df


def _clear_people_cache():
    """Clear the cached people data to force a refresh from Retrosheet."""
    _get_people_data.cache_clear()
