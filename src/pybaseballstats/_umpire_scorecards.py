"""Umpire Scorecards retrieval and source-specific parsing."""

from typing import Any, Literal

import polars as pl

from pybaseballstats._consts.umpire_scorecard_consts import (
    UMPIRE_SCORECARD_GAMES_URL,
    UMPIRE_SCORECARD_TEAMS_URL,
    UMPIRE_SCORECARD_UMPIRES_URL,
    UMPIRE_SCORECARDS_PLAYERS_URL,
    UmpireScorecardTeams,
)
from pybaseballstats._utils.request_utils import get_json
from pybaseballstats._utils.umpire_scorecards_utils import (
    _dates,
    _game_type,
    _player_type,
    _team,
    _team_query,
    _umpire_filters,
)


def _rows(url: str, operation: str, required: set[str]) -> pl.DataFrame:
    try:
        data: Any = get_json(url)
    except RuntimeError as exc:
        raise RuntimeError(f"{operation}: Umpire Scorecards request failed") from exc
    if not isinstance(data, dict) or not isinstance(data.get("rows"), list):
        raise RuntimeError(f"{operation}: Umpire Scorecards response is missing rows")
    rows = data["rows"]
    if any(not isinstance(row, dict) or not row for row in rows):
        raise RuntimeError(
            f"{operation}: Umpire Scorecards rows have invalid structure"
        )
    if rows and not required.issubset(set().union(*(row.keys() for row in rows))):
        raise RuntimeError(f"{operation}: Umpire Scorecards rows lack required fields")
    try:
        return pl.DataFrame(rows)
    except (pl.exceptions.PolarsError, TypeError, ValueError) as exc:
        raise RuntimeError(f"{operation}: invalid Umpire Scorecards rows") from exc


def _exact_umpire(df: pl.DataFrame, name: str, operation: str) -> pl.DataFrame:
    if not name or df.is_empty():
        return df
    if "umpire" not in df.columns:
        raise RuntimeError(f"{operation}: Umpire Scorecards rows are missing umpire")
    return df.filter(pl.col("umpire") == name)


def game_data(
    start_date: str,
    end_date: str,
    game_type: Literal["*", "R", "A", "P", "F", "D", "L", "W"] = "*",
    focus_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    focus_team_home_away: Literal["h", "a", "*"] = "*",
    opponent_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    umpire_name: str = "",
) -> pl.DataFrame:
    """Return game rows for a date range and optional exact umpire name.

    A valid response with no matching rows returns an empty DataFrame. Request
    and response-format failures raise RuntimeError.
    """
    start_date, end_date = _dates(start_date, end_date)
    _game_type(game_type)
    team = _team_query(focus_team, focus_team_home_away, opponent_team)
    _umpire_filters(umpire_name)
    url = UMPIRE_SCORECARD_GAMES_URL.format(
        start_date=start_date, end_date=end_date, game_type=game_type, team=team
    )
    return _exact_umpire(
        _rows(url, "game_data", {"date", "umpire"}), umpire_name, "game_data"
    )


def umpire_data(
    start_date: str,
    end_date: str,
    game_type: Literal["*", "R", "A", "P", "F", "D", "L", "W"] = "*",
    focus_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    focus_team_home_away: Literal["h", "a", "*"] = "*",
    opponent_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    umpire_name: str = "",
    min_games_called: int = 0,
) -> pl.DataFrame:
    """Return umpire summary rows, with exact name and game-count filters."""
    start_date, end_date = _dates(start_date, end_date)
    _game_type(game_type)
    team = _team_query(focus_team, focus_team_home_away, opponent_team)
    _umpire_filters(umpire_name, min_games_called)
    url = UMPIRE_SCORECARD_UMPIRES_URL.format(
        start_date=start_date, end_date=end_date, game_type=game_type, team=team
    )
    df = _exact_umpire(
        _rows(url, "umpire_data", {"umpire", "n"}), umpire_name, "umpire_data"
    )
    if min_games_called and not df.is_empty():
        if "n" not in df.columns:
            raise RuntimeError("umpire_data: Umpire Scorecards rows are missing n")
        df = df.filter(pl.col("n") >= min_games_called)
    return df


def team_data(
    start_date: str,
    end_date: str,
    game_type: Literal["*", "R", "A", "P", "F", "D", "L", "W"] = "*",
    focus_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
) -> pl.DataFrame:
    """Return team summary rows for a date range and optional team filter."""
    start_date, end_date = _dates(start_date, end_date)
    _game_type(game_type)
    _team(focus_team, "focus_team")
    url = UMPIRE_SCORECARD_TEAMS_URL.format(
        start_date=start_date, end_date=end_date, game_type=game_type
    )
    df = _rows(url, "team_data", {"team"})
    if focus_team is not UmpireScorecardTeams.ALL and not df.is_empty():
        if "team" not in df.columns:
            raise RuntimeError("team_data: Umpire Scorecards rows are missing team")
        df = df.filter(pl.col("team") == focus_team.value)
    return df


def player_data(
    start_date: str,
    end_date: str,
    player_type: Literal["C", "P", "B"],
    game_type: Literal["*", "R", "A", "P", "F", "D", "L", "W"] = "*",
    team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
) -> pl.DataFrame:
    """Return player rows for a date range, player type, and team filter."""
    start_date, end_date = _dates(start_date, end_date)
    _game_type(game_type)
    _team(team, "team")
    _player_type(player_type)
    url = UMPIRE_SCORECARDS_PLAYERS_URL.format(
        player_type=player_type,
        start_date=start_date,
        end_date=end_date,
        game_type=game_type,
        team=team.value,
    )
    return _rows(url, "player_data", {"player_id", "n_pitches"})
