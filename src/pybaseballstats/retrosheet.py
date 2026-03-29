from datetime import datetime
from typing import Optional

import polars as pl
import requests
from unidecode import unidecode

from pybaseballstats.consts.retrosheet_consts import (
    EJECTIONS_URL,
    RETROSHEET_KEEP_COLS,
)
from pybaseballstats.utils.retrosheet_utils import _get_people_data

__all__ = ["player_lookup", "ejections_data"]


def player_lookup(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    strip_accents: Optional[bool] = False,
) -> pl.DataFrame:
    """Look up players in Retrosheet's people registry.

    Args:
        first_name (str | None, optional): Player first name filter.
        last_name (str | None, optional): Player last name filter.
        strip_accents (bool | None, optional): Whether to normalize accents before
            matching.

    Raises:
        ValueError: If neither ``first_name`` nor ``last_name`` is provided.
        TypeError: If ``first_name`` is provided and is not a string.
        TypeError: If ``last_name`` is provided and is not a string.

    Returns:
        pl.DataFrame: Matching player rows with canonical Retrosheet columns.
    """
    if not first_name and not last_name:
        raise ValueError("At least one of first_name or last_name must be provided")
    if first_name and not isinstance(first_name, str):
        raise TypeError("first_name must be a string")
    if last_name and not isinstance(last_name, str):
        raise TypeError("last_name must be a string")

    full_df = _get_people_data()

    # Normalize input
    if first_name:
        first_name = first_name.lower().strip()
    if last_name:
        last_name = last_name.lower().strip()

    # Apply accent stripping if requested
    if strip_accents:
        if first_name:
            first_name = unidecode(first_name)
        if last_name:
            last_name = unidecode(last_name)

        # Strip accents from all name columns in the dataframe
        full_df = full_df.with_columns(
            [
                pl.col("name_last_lower")
                .map_elements(
                    lambda s: unidecode(s) if s else s, return_dtype=pl.String
                )
                .alias("name_last_lower"),
                pl.col("name_first_lower")
                .map_elements(
                    lambda s: unidecode(s) if s else s, return_dtype=pl.String
                )
                .alias("name_first_lower"),
                pl.col("name_given_lower")
                .map_elements(
                    lambda s: unidecode(s) if s else s, return_dtype=pl.String
                )
                .alias("name_given_lower"),
                pl.col("name_nick_lower")
                .map_elements(
                    lambda s: unidecode(s) if s else s, return_dtype=pl.String
                )
                .alias("name_nick_lower"),
                pl.col("name_matrilineal_lower")
                .map_elements(
                    lambda s: unidecode(s) if s else s, return_dtype=pl.String
                )
                .alias("name_matrilineal_lower"),
                pl.col("name_suffix_lower")
                .map_elements(
                    lambda s: unidecode(s) if s else s, return_dtype=pl.String
                )
                .alias("name_suffix_lower"),
            ]
        )

    # Exact matching
    if first_name and last_name:
        df = full_df.filter(
            (pl.col("name_first_lower") == first_name)
            & (pl.col("name_last_lower") == last_name)
        )
    elif first_name:
        df = full_df.filter(pl.col("name_first_lower") == first_name)
    else:  # last_name only
        df = full_df.filter(pl.col("name_last_lower") == last_name)

    # Select only the original columns (not the lowercase/score columns)
    result_cols = RETROSHEET_KEEP_COLS.copy()

    return df.select([col for col in result_cols if col in df.columns])


def ejections_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    ejectee_name: Optional[str] = None,
    umpire_name: Optional[str] = None,
    inning: Optional[int] = None,
) -> pl.DataFrame:
    """Return MLB ejections from Retrosheet with optional filters.

    Args:
        start_date (str | None, optional): Inclusive start date in ``MM/DD/YYYY``.
        end_date (str | None, optional): Inclusive end date in ``MM/DD/YYYY``.
        ejectee_name (str | None, optional): Substring filter on ``EJECTEENAME``.
        umpire_name (str | None, optional): Substring filter on ``UMPIRENAME``.
        inning (int | None, optional): Inning filter from -1 to 20.

    Raises:
        ValueError: If ``start_date`` is not in ``MM/DD/YYYY`` format.
        ValueError: If ``end_date`` is not in ``MM/DD/YYYY`` format.
        ValueError: If ``start_date`` is after ``end_date``.
        ValueError: If ``inning`` is outside -1 to 20.

    Returns:
        pl.DataFrame: Ejection rows matching the provided filters.
    """
    df = pl.read_csv(
        requests.get(EJECTIONS_URL).content,
        infer_schema_length=None,
        truncate_ragged_lines=True,
    )
    df = df.with_columns(
        pl.col("DATE").str.to_date("%m/%d/%Y").alias("DATE"),
    )
    df = df.filter(pl.col("INNING") != "Cy Rigler")  # remove bad data row
    df = df.with_columns(pl.col("INNING").cast(pl.Int8))

    start_dt = None
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%m/%d/%Y")
        except ValueError:
            raise ValueError("start_date must be in 'MM/DD/YYYY' format")

    end_dt = None
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%m/%d/%Y")
        except ValueError:
            raise ValueError("end_date must be in 'MM/DD/YYYY' format")

    if start_dt and end_dt and start_dt > end_dt:
        raise ValueError("start_date must be before end_date")

    if start_dt:
        df = df.filter(pl.col("DATE") >= start_dt)
    if end_dt:
        df = df.filter(pl.col("DATE") <= end_dt)

    if df.is_empty():
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

    if inning is not None:
        if -1 <= inning <= 20:
            df = df.filter(pl.col("INNING") == inning)
            if df.shape[0] == 0:
                print("Warning: No ejections found for the given inning.")
                return df
        else:
            raise ValueError("Inning must be between -1 and 20")

    return df
