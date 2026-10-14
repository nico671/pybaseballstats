import polars as pl

from pybaseballstats._consts.bref_consts import (
    BREF_MANAGER_TENDENCIES_URL,
    BREF_MANAGERS_GENERAL_URL,
)
from pybaseballstats._utils.bref_utils import (
    _required_table,
    _source_schema_errors,
)
from pybaseballstats._utils.session_utils import BREF_SESSION as session

__all__ = ["managers_basic_data", "managers_tendencies_data"]


@_source_schema_errors
def managers_basic_data(year: int, verbose: bool = False) -> pl.DataFrame:
    """Return basic MLB manager statistics for a season.

    Args:
        year (int): Season year.
        verbose (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.

    Raises:
                ValueError: If ``year`` is earlier than 1871.
        TypeError: If ``year`` is not an integer.

    Returns:
        pl.DataFrame: Manager-level season summary data.
    """
    if type(year) is not int:
        raise TypeError("Year must be an integer")
    if year < 1871:
        raise ValueError("Year must be at least 1871")
    resp = session.get(BREF_MANAGERS_GENERAL_URL.format(year=year), verbose=verbose)
    df = _required_table(resp.text, "manager_record", "managers_basic_data")
    df = df.drop("ranker")
    df = df.with_columns(
        [
            pl.col("W_post").fill_null(0).alias("postseason_wins"),
            pl.col("L_post").fill_null(0).alias("postseason_losses"),
        ]
    ).drop(["W_post", "L_post"])
    return df


@_source_schema_errors
def managers_tendencies_data(year: int, verbose: bool = False) -> pl.DataFrame:
    """Return MLB manager tendencies for a season.

    Args:
        year (int): Season year.
        verbose (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.

    Raises:
                ValueError: If ``year`` is earlier than 1871.
        TypeError: If ``year`` is not an integer.

    Returns:
        pl.DataFrame: Manager tendencies and strategic usage metrics.
    """
    if type(year) is not int:
        raise TypeError("Year must be an integer")
    if year < 1871:
        raise ValueError("Year must be at least 1871")
    resp = session.get(BREF_MANAGER_TENDENCIES_URL.format(year=year), verbose=verbose)
    df = _required_table(resp.text, "manager_tendencies", "managers_tendencies_data")
    df = df.drop("ranker")
    df = df.with_columns(
        pl.col(
            [
                "manager",
                "team_ID",
            ]
        ).str.replace("0", "")
    )
    return df
