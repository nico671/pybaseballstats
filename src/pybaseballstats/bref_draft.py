import polars as pl
from bs4 import BeautifulSoup

from pybaseballstats.consts.bref_consts import (
    BREF_DRAFT_YEAR_ROUND_URL,
    TEAM_YEAR_DRAFT_URL,
    BREFTeams,
)
from pybaseballstats.utils.bref_utils import (
    BREFSession,
    _extract_table,
    get_bref_table_html,
    resolve_bref_team_code,
)

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
    polars_data = None
    if resp:
        table_html = get_bref_table_html(resp.text, "draft_stats")

        if table_html:
            table_soup = BeautifulSoup(table_html, "html.parser")
            polars_data = _extract_table(table_soup)
    if not polars_data:
        raise ValueError(f"No draft data found for year {year} and round {draft_round}")
    df = pl.DataFrame(polars_data)
    df = df.drop("draft_abb")
    df = df.with_columns(
        pl.col("player").str.replace_all(r"\s+\(minors\)$", "").alias("player")
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
    print(resolved_code, team.value)
    polars_data = None
    for candidate_code in candidate_codes:
        resp = session.get(TEAM_YEAR_DRAFT_URL.format(year=year, team=candidate_code))

        if resp:
            table_html = get_bref_table_html(resp.text, "draft_stats")

            if table_html:
                table_soup = BeautifulSoup(table_html, "html.parser")
                polars_data = _extract_table(table_soup)
        if polars_data:
            break

    if polars_data is None:
        raise ValueError(f"No draft table found for {team.name} in {year}.")

    df = pl.DataFrame(polars_data)
    df = df.with_columns(
        pl.col("player").str.replace_all(r"\s+\(minors\)$", "").alias("player")
    )
    df = df.drop("draft_abb")
    return df
