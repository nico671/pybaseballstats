import polars as pl
from bs4 import BeautifulSoup

from pybaseballstats.consts.bref_consts import (
    BREF_DRAFT_YEAR_ROUND_URL,
    TEAM_YEAR_DRAFT_URL,
    BREFTeams,
    resolve_bref_team_code,
)
from pybaseballstats.utils.bref_utils import BREFSession, _extract_table

session = BREFSession.instance()  # type: ignore[attr-defined]


__all__ = ["BREFTeams", "draft_order_by_year_round", "franchise_draft_order"]


def draft_order_by_year_round(year: int, draft_round: int) -> pl.DataFrame:
    """Return MLB draft results for a specific year and round.

    Args:
        year (int): Draft year.
        draft_round (int): Draft round number.

    Raises:
        ValueError: If ``year`` is earlier than 1965.
        ValueError: If ``draft_round`` is outside 1-60.

    Returns:
        pl.DataFrame: Draft data for the requested year/round.
    """
    if year < 1965:
        raise ValueError("Draft data is only available from 1965 onwards")
    if draft_round < 1 or draft_round > 60:
        raise ValueError("Draft round must be between 1 and 60")
    resp = session.get(BREF_DRAFT_YEAR_ROUND_URL.format(year=year, round=draft_round))
    assert resp is not None, (
        "Failed to retrieve data from Baseball Reference. Please check your internet connection and try again."
    )
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
    """Return MLB draft results for a specific franchise and year.

    Args:
        team (BREFTeams): Franchise filter.
        year (int): Draft year.

    Raises:
        ValueError: If ``year`` is earlier than 1965.
        ValueError: If ``team`` is not a valid ``BREFTeams`` enum value.

    Returns:
        pl.DataFrame: Draft data for the requested franchise/year.
    """
    if year < 1965:
        raise ValueError("Draft data is only available from 1965 onwards")
    if not isinstance(team, BREFTeams):
        raise ValueError(
            "Team must be a valid BREFTeams enum value. See BREFTeams class for valid values."
        )

    resolved_code = resolve_bref_team_code(team=team, year=year)
    candidate_codes = [resolved_code]
    if team.value != resolved_code:
        candidate_codes.append(team.value)

    table = None
    for team_code in candidate_codes:
        resp = session.get(TEAM_YEAR_DRAFT_URL.format(year=year, team=team_code))
        if resp is None:
            continue
        soup = BeautifulSoup(resp.content, "html.parser")
        table = soup.find("table", id="draft_stats")
        if table is not None:
            break

    if table is None:
        raise ValueError(
            f"No draft table found for {team.name} in {year}. Tried team codes: {candidate_codes}"
        )

    df = pl.DataFrame(_extract_table(table))
    df = df.with_columns(
        pl.col("player").str.replace_all(r"\s+\(minors\)$", "").alias("player")
    )
    df = df.drop("draft_abb")
    df = df.with_columns(
        pl.col(["year_ID", "draft_round", "overall_pick", "round_pick"]).cast(pl.Int16)
    )
    return df
