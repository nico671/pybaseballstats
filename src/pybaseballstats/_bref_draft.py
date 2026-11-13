import polars as pl

from pybaseballstats._consts.bref_consts import (
    BREF_DRAFT_YEAR_ROUND_URL,
    TEAM_YEAR_DRAFT_URL,
    BREFTeams,
)
from pybaseballstats._utils.bref_utils import (
    _get_draft_dataframe,
    _source_schema_errors,
    resolve_bref_team_code,
)

__all__ = ["BREFTeams", "draft_order_by_year_round", "franchise_draft_order"]


@_source_schema_errors
def draft_order_by_year_round(
    year: int, draft_round: int, verbose: bool = False
) -> pl.DataFrame:
    """Return MLB draft results for a specific year and round.

    Args:
        year (int): Draft year.
        draft_round (int): Draft round number.
        verbose (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.

    Raises:
        ValueError: If ``year`` is earlier than 1965.
        ValueError: If ``draft_round`` is outside 1-60.

    Returns:
        pl.DataFrame: Draft data for the requested year/round.
    """
    if type(year) is not int:
        raise TypeError("year must be an integer")
    if type(draft_round) is not int:
        raise TypeError("draft_round must be an integer")
    if year < 1965:
        raise ValueError("Draft data is only available from 1965 onwards")
    if draft_round < 1 or draft_round > 60:
        raise ValueError("Draft round must be between 1 and 60")
    df = _get_draft_dataframe(
        BREF_DRAFT_YEAR_ROUND_URL.format(year=year, round=draft_round), verbose
    )
    if df is None:
        raise RuntimeError(
            f"draft_order_by_year_round: no draft table for {year} round {draft_round}"
        )
    return df


@_source_schema_errors
def franchise_draft_order(
    team: BREFTeams, year: int, verbose: bool = False
) -> pl.DataFrame:
    """Return MLB draft results for a specific franchise and year.

    Args:
        team (BREFTeams): Franchise filter.
        year (int): Draft year.
        verbose (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.

    Raises:
        ValueError: If ``year`` is earlier than 1965.
        TypeError: If ``team`` is not a ``BREFTeams`` enum value.

    Returns:
        pl.DataFrame: Draft data for the requested franchise/year.
    """
    if type(year) is not int:
        raise TypeError("year must be an integer")
    if year < 1965:
        raise ValueError("Draft data is only available from 1965 onwards")
    if not isinstance(team, BREFTeams):
        raise TypeError(
            "Team must be a valid BREFTeams enum value. See BREFTeams class for valid values."
        )

    resolved_code = resolve_bref_team_code(team=team, year=year)

    candidate_codes = [resolved_code]
    if team.value != resolved_code:
        candidate_codes.append(team.value)
    for candidate_code in candidate_codes:
        df = _get_draft_dataframe(
            TEAM_YEAR_DRAFT_URL.format(year=year, team=candidate_code), verbose
        )
        if df is not None:
            return df

    raise RuntimeError(
        f"franchise_draft_order: no draft table for {team.name} in {year}"
    )
