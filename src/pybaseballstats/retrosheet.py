from datetime import datetime
from typing import Optional

import polars as pl
import requests
from rapidfuzz import fuzz
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
    fuzzy: Optional[bool] = False,
    fuzzy_threshold: Optional[int] = 80,
) -> pl.DataFrame:
    """A function to look up players by first and/or last name from Retrosheet's player registry.

    Args:
        first_name (str, optional): The first name of the player. Defaults to None.
        last_name (str, optional): The last name of the player. Defaults to None.
        strip_accents (bool, optional): Whether to strip accents from the names. Defaults to False.
        fuzzy (bool, optional): Whether to use fuzzy matching with similarity scoring. Defaults to False.
        fuzzy_threshold (int, optional): Minimum similarity score (0-100) for fuzzy matches. Defaults to 80.

    Raises:
        ValueError: If both first_name and last_name are None.
        TypeError: If first_name is not a string.
        TypeError: If last_name is not a string.
        ValueError: If fuzzy_threshold is not between 0 and 100.

    Returns:
        pl.DataFrame: A Polars DataFrame containing the player information, sorted by match quality if fuzzy=True.
    """
    if not first_name and not last_name:
        raise ValueError("At least one of first_name or last_name must be provided")
    if first_name and not isinstance(first_name, str):
        raise TypeError("first_name must be a string")
    if last_name and not isinstance(last_name, str):
        raise TypeError("last_name must be a string")
    if not 0 <= fuzzy_threshold <= 100:
        raise ValueError("fuzzy_threshold must be between 0 and 100")

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

    # Build filter conditions
    if fuzzy:
        # Real fuzzy matching using rapidfuzz
        def calculate_name_score(row):
            """Calculate the best fuzzy match score across all name columns."""
            scores = []

            if first_name:
                # Check against first name columns
                for col in ["name_first_lower", "name_given_lower", "name_nick_lower"]:
                    name_val = row[col]
                    if name_val:
                        scores.append(fuzz.ratio(first_name, name_val))

            if last_name:
                # Check against last name columns
                for col in ["name_last_lower", "name_matrilineal_lower"]:
                    name_val = row[col]
                    if name_val:
                        scores.append(fuzz.ratio(last_name, name_val))

            if first_name and last_name:
                # Combine first and last name for a full name score
                full_name_input = f"{first_name} {last_name}"
                for fn_col in [
                    "name_first_lower",
                    "name_given_lower",
                    "name_nick_lower",
                ]:
                    for ln_col in ["name_last_lower", "name_matrilineal_lower"]:
                        fn_val = row[fn_col]
                        ln_val = row[ln_col]
                        if fn_val and ln_val:
                            full_name_val = f"{fn_val} {ln_val}"

                            scores.append(fuzz.ratio(full_name_input, full_name_val))

                            # Also check with suffix if present
                            suffix_val = row["name_suffix_lower"]
                            if suffix_val:
                                full_name_with_suffix = (
                                    f"{fn_val} {ln_val} {suffix_val}"
                                )
                                scores.append(
                                    fuzz.ratio(full_name_input, full_name_with_suffix)
                                )

            # Return the max score
            return max(scores) if scores else 0.0

        # Apply fuzzy matching
        full_df = full_df.with_columns(
            pl.struct(
                [
                    "name_first_lower",
                    "name_given_lower",
                    "name_nick_lower",
                    "name_last_lower",
                    "name_matrilineal_lower",
                    "name_suffix_lower",
                ]
            )
            .map_elements(calculate_name_score)
            .alias("match_score")
        )

        # Filter by threshold and sort by match quality
        df = full_df.filter(pl.col("match_score") >= fuzzy_threshold).sort(
            "match_score", descending=True
        )

    else:
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
    if fuzzy:
        result_cols.append("match_score")  # Include match score for fuzzy results

    return df.select([col for col in result_cols if col in df.columns])


def ejections_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    ejectee_name: Optional[str] = None,
    umpire_name: Optional[str] = None,
    inning: Optional[int] = None,
) -> pl.DataFrame:
    """Returns a DataFrame of MLB ejections from Retrosheet's ejections data.

    Args:
        start_date (Optional[str], optional): The start date for the ejections data in 'MM/DD/YYYY' format. Defaults to None.
        end_date (Optional[str], optional): The end date for the ejections data in 'MM/DD/YYYY' format. Defaults to None.
        ejectee_name (Optional[str], optional): The name of the ejectee. Defaults to None.
        umpire_name (Optional[str], optional): The name of the ejecting umpire. Defaults to None.
        inning (Optional[int], optional): The inning number, between -1 and 20 (not 0). Defaults to None.

    Raises:
        ValueError: If start_date is not in 'MM/DD/YYYY' format.
        ValueError: If end_date is not in 'MM/DD/YYYY' format.
        ValueError: If start_date is after end_date.
        ValueError: If inning is not between -1 and 20.

    Returns:
        pl.DataFrame: A DataFrame containing the ejections data.
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

    if inning is not None:
        if -1 <= inning <= 20:
            df = df.filter(pl.col("INNING") == inning)
            if df.shape[0] == 0:
                print("Warning: No ejections found for the given inning.")
                return df
        else:
            raise ValueError("Inning must be between -1 and 20")

    return df
