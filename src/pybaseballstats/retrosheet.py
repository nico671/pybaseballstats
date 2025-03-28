from datetime import datetime
from typing import Optional

import pandas as pd
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


# TODO: usage docs
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


EJECTIONS_URL = "https://raw.githubusercontent.com/chadwickbureau/retrosheet/refs/heads/master/reference/ejections.csv"


def retrosheet_ejections_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    ejectee_name: Optional[str] = None,
    umpire_name: Optional[str] = None,
    inning: Optional[int] = None,
    ejectee_job: Optional[str] = None,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    df = pl.read_csv(
        requests.get(EJECTIONS_URL).content,
    )
    df = df.with_columns(
        pl.col("DATE").str.to_date("%m/%d/%Y").alias("DATE"),
    )
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%m/%d/%Y")
        except ValueError:
            raise ValueError("start_date must be in 'MM/DD/YYYY' format")
        df = df.filter(pl.col("DATE") >= start_dt)
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%m/%d/%Y")
        except ValueError:
            raise ValueError("end_date must be in 'MM/DD/YYYY' format")
        df = df.filter(pl.col("DATE") <= end_dt)
    if df.shape[0] == 0:
        print("Warning: No ejections found for the given date range.")
        return df
    if ejectee_name:
        df = df.filter(pl.col("EJECTEENAME").str.contains(ejectee_name))
        if df.shape[0] == 0:
            print("Warning: No ejections found for the given ejectee name.")
            return df
    if umpire_name:
        df = df.filter(pl.col("UMPIRENAME").str.contains(umpire_name))
        if df.shape[0] == 0:
            print("Warning: No ejections found for the given umpire name.")
            return df
    if inning:
        if inning >= -1 and inning <= 20:
            df = df.filter(pl.col("INNING") == inning)
            if df.shape[0] == 0:
                print("Warning: No ejections found for the given inning.")
                return df
        else:
            raise ValueError("Inning must be between -1 and 20")
    if ejectee_job:
        df = df.filter(pl.col("JOB") == ejectee_job)
        if df.shape[0] == 0:
            print("Warning: No ejections found for the given ejectee job.")
            return df
    return df if not return_pandas else df.to_pandas()
