import polars as pl
from bs4 import BeautifulSoup

from pybaseballstats.consts.bref_consts import (
    BREF_DRAFT_YEAR_ROUND_URL,
    TEAM_YEAR_DRAFT_URL,
    BREFTeams,
)
from pybaseballstats.utils.bref_utils import BREFSession, _extract_table

session = BREFSession.instance()  # type: ignore[attr-defined]


__all__ = ["BREFTeams", "draft_order_by_year_round", "franchise_draft_order"]


def draft_order_by_year_round(year: int, draft_round: int) -> pl.DataFrame:
    """Returns a DataFrame of draft data for a given year and round.

    Args:
        year (int): The year of the draft.
        draft_round (int): The round of the draft.
    Raises:
        ValueError: If the year is before 1965
        ValueError: If the draft round is not between 1 and 60
    Returns:
        pl.DataFrame: A DataFrame containing the draft data.
    """
    if year < 1965:
        raise ValueError("Draft data is only available from 1965 onwards")
    if draft_round < 1 or draft_round > 60:
        raise ValueError("Draft round must be between 1 and 60")
    resp = session.get(BREF_DRAFT_YEAR_ROUND_URL.format(year=year, round=draft_round))
    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find("table", {"id": "draft_stats"})
    df = pl.DataFrame(_extract_table(table))
    df = df.drop("draft_abb")
    df = df.with_columns(
        pl.col("player").str.replace_all(r"\s+\(minors\)$", "").alias("player")
    )
    df = df.with_columns(
        pl.col(["year_ID", "draft_round", "overall_pick", "round_pick"]).cast(pl.Int16)
    )
    return df


def franchise_draft_order(team: BREFTeams, year: int) -> pl.DataFrame:
    """Returns a Dataframe of draft data for a given team and year. NOTE: This function uses requests to scrape the data.

    Args:
        team (str): Which team to pull draft data from
        year (int): Which year to pull draft data from

    Raises:
        ValueError: If the year is before 1965
        ValueError: If the team abbreviation is not valid

    Returns:
        pl.DataFrame: A DataFrame of draft data for the given team and year.
    """
    if year < 1965:
        raise ValueError("Draft data is only available from 1965 onwards")
    if not isinstance(team, BREFTeams):
        raise ValueError(
            "Team must be a valid BREFTeams enum value. See BREFTeams class for valid values."
        )

    resp = session.get(TEAM_YEAR_DRAFT_URL.format(year=year, team=team.value))
    soup = BeautifulSoup(resp.content, "html.parser")

    table = soup.find("table", id="draft_stats")

    df = pl.DataFrame(_extract_table(table))
    df = df.with_columns(
        pl.col("player").str.replace_all(r"\s+\(minors\)$", "").alias("player")
    )
    df = df.drop("draft_abb")
    df = df.with_columns(
        pl.col(["year_ID", "draft_round", "overall_pick", "round_pick"]).cast(pl.Int16)
    )
    return df
