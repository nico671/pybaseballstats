import polars as pl
import requests
from unidecode import unidecode

PEOPLES_URL = "https://raw.githubusercontent.com/chadwickbureau/register/refs/heads/master/data/people-{num}.csv"
keep_cols = [
    "key_fangraphs",
    "key_mlbam",
    "key_retro",
    "key_bbref",
    "name_last",
    "name_first",
]


def get_people_data() -> pl.DataFrame:
    df_list = []
    for i in range(0, 10):
        data = requests.get(PEOPLES_URL.format(num=i)).content
        df = pl.read_csv(data, truncate_ragged_lines=True)
        df = df.select(pl.col(keep_cols))
        df_list.append(df)

    for letter in ["a", "b", "c", "d", "f"]:
        data = requests.get(PEOPLES_URL.format(num=letter)).content
        df = pl.read_csv(data, truncate_ragged_lines=True)
        df = df.select(pl.col(keep_cols))
        df_list.append(df)

    df = df_list[0]
    for i in range(1, len(df_list)):
        df = df.vstack(df_list[i])
    df = df.drop_nulls(keep_cols)
    df = df.with_columns(
        [
            pl.col("name_last").str.to_lowercase().alias("name_last"),
            pl.col("name_first").str.to_lowercase().alias("name_first"),
        ]
    )
    return df


def player_lookup(
    first_name: str = None, last_name: str = None, strip_accents: bool = False
) -> pl.DataFrame:
    if not first_name and not last_name:
        raise ValueError("At least one of first_name or last_name must be provided")
    full_df = get_people_data()
    if first_name:
        first_name = first_name.lower()
    else:
        first_name = None
    if last_name:
        last_name = last_name.lower()
    else:
        last_name = None
    if strip_accents:
        first_name = unidecode(first_name) if first_name else None
        last_name = unidecode(last_name) if last_name else None
        full_df = full_df.with_columns(
            [
                pl.col("name_last")
                .map_elements(lambda s: unidecode(s), return_dtype=pl.String)
                .alias("name_last"),
                pl.col("name_first")
                .map_elements(lambda s: unidecode(s), return_dtype=pl.String)
                .alias("name_first"),
            ]
        )
    if first_name and last_name:
        return (
            full_df.filter(pl.col("name_first") == first_name)
            .filter(pl.col("name_last") == last_name)
            .select(keep_cols)
        )
    elif first_name:
        return full_df.filter(pl.col("name_first") == first_name).select(keep_cols)
    else:
        return full_df.filter(pl.col("name_last") == last_name).select(keep_cols)
