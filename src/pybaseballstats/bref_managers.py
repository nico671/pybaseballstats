import polars as pl
from bs4 import BeautifulSoup

from pybaseballstats.consts.bref_consts import (
    BREF_MANAGER_TENDENCIES_URL,
    BREF_MANAGERS_GENERAL_URL,
)
from pybaseballstats.utils.bref_utils import (
    BREFSession,
    _extract_table,
    _goto_and_get_stable_html,
)

session = BREFSession.instance()  # type: ignore[attr-defined]
__all__ = ["managers_basic_data", "managers_tendencies_data"]


def managers_basic_data(year: int) -> pl.DataFrame:
    """Return basic MLB manager statistics for a season.

    Args:
        year (int): Season year.

    Raises:
        ValueError: If ``year`` is not provided.
        ValueError: If ``year`` is earlier than 1871.
        TypeError: If ``year`` is not an integer.

    Returns:
        pl.DataFrame: Manager-level season summary data.
    """
    if not year:
        raise ValueError("Year must be provided")
    if not isinstance(year, int):
        raise TypeError("Year must be an integer")
    if year < 1871:
        raise ValueError("Year must be greater than 1871")

    with session.get_page() as page:
        url = BREF_MANAGERS_GENERAL_URL.format(year=year)
        html = _goto_and_get_stable_html(page, url)
        soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", {"id": "manager_record"})
    df = pl.DataFrame(_extract_table(table))
    df = df.drop("ranker")
    df = df.with_columns(
        [
            pl.col("W_post").fill_null(0).alias("postseason_wins"),
            pl.col("L_post").fill_null(0).alias("postseason_losses"),
        ]
    ).drop(["W_post", "L_post"])
    return df


def managers_tendencies_data(year: int) -> pl.DataFrame:
    """Return MLB manager tendencies for a season.

    Args:
        year (int): Season year.

    Raises:
        ValueError: If ``year`` is not provided.
        ValueError: If ``year`` is earlier than 1871.
        TypeError: If ``year`` is not an integer.

    Returns:
        pl.DataFrame: Manager tendencies and strategic usage metrics.
    """
    if not year:
        raise ValueError("Year must be provided")
    if not isinstance(year, int):
        raise TypeError("Year must be an integer")
    if year < 1871:
        raise ValueError("Year must be greater than 1871")

    resp = session.get(BREF_MANAGER_TENDENCIES_URL.format(year=year))
    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find("table", {"id": "manager_tendencies"})
    df = pl.DataFrame(_extract_table(table))
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
