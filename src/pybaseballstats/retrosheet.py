from datetime import datetime
from typing import Optional

import polars as pl
import requests
from unidecode import unidecode

from pybaseballstats.consts.retrosheet_consts import (
    EJECTIONS_URL,
    PEOPLES_URL,
    RETROSHEET_KEEP_COLS,
)

__all__ = ["player_lookup", "ejections_data"]


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


def player_lookup(
    first_name: str = None,
    last_name: str = None,
    strip_accents: bool = False,
) -> pl.DataFrame:
    """A function to look up players by first and/or last name from Retrosheet's player registry.

    Args:
        first_name (str, optional): The first name of the player. Defaults to None.
        last_name (str, optional): The last name of the player. Defaults to None.
        strip_accents (bool, optional): Whether to strip accents from the names. Defaults to False.
        return_pandas (bool, optional): Whether to return a pandas DataFrame instead of a polars DataFrame. Defaults to False.

    Raises:
        ValueError: If both first_name and last_name are None.

    Returns:
        pl.DataFrame: A Polars DataFrame containing the player information.
    """
    if not first_name and not last_name:
        raise ValueError("At least one of first_name or last_name must be provided")
    full_df = _get_people_data()
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
        df = (
            full_df.filter(pl.col("name_first") == first_name)
            .filter(pl.col("name_last") == last_name)
            .select(RETROSHEET_KEEP_COLS)
        )
    elif first_name:
        df = full_df.filter(pl.col("name_first") == first_name).select(
            RETROSHEET_KEEP_COLS
        )
    else:
        df = full_df.filter(pl.col("name_last") == last_name).select(
            RETROSHEET_KEEP_COLS
        )
    return df


def ejections_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    ejectee_name: Optional[str] = None,
    umpire_name: Optional[str] = None,
    inning: Optional[int] = None,
    ejectee_job: Optional[str] = None,
) -> pl.DataFrame:
    """Returns a DataFrame of MLB ejections from Retrosheet's ejections data.

    Args:
        start_date (Optional[str], optional): The start date for the ejections data. Defaults to None.
        end_date (Optional[str], optional): The end date for the ejections data. Defaults to None.
        ejectee_name (Optional[str], optional): The name of the ejectee. Defaults to None.
        umpire_name (Optional[str], optional): The name of the ejecting umpire. Defaults to None.
        inning (Optional[int], optional): The inning number. Defaults to None.
        ejectee_job (Optional[str], optional): The job of the ejectee. Defaults to None.

    Raises:
        ValueError: If start_date is not in 'MM/DD/YYYY' format.
        ValueError: If end_date is not in 'MM/DD/YYYY' format.
        ValueError: If inning is not between -1 and 20.

    Returns:
        pl.DataFrame: A DataFrame containing the ejections data.
    """
    df = pl.read_csv(
        requests.get(EJECTIONS_URL).content,
        infer_schema_length=None,
        truncate_ragged_lines=True,
    )
    # for col in df.columns:
    #     print(f"Column: {col}, Type: {df[col].dtype}")
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
    return df
