"""Validate Umpire Scorecards inputs and construct team filters."""

from datetime import datetime

from pybaseballstats._consts.umpire_scorecard_consts import (
    UMPIRE_SCORECARD_GAME_TYPES,
    UmpireScorecardTeams,
)


def _dates(start_date: str, end_date: str) -> tuple[str, str]:
    for label, value in (("start_date", start_date), ("end_date", end_date)):
        if not isinstance(value, str):
            raise TypeError(f"{label} must be a YYYY-MM-DD string")
        try:
            parsed = datetime.strptime(value, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(f"{label} must be in YYYY-MM-DD format") from exc
        if parsed.strftime("%Y-%m-%d") != value:
            raise ValueError(f"{label} must be in YYYY-MM-DD format")
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    if start > end:
        raise ValueError("start_date must be before end_date")
    if start.year < 2015 or end.year > datetime.now().year:
        raise ValueError("dates must be between 2015 and the current year")
    return start_date, end_date


def _game_type(value: str) -> None:
    if not isinstance(value, str):
        raise TypeError("game_type must be a string")
    if value not in UMPIRE_SCORECARD_GAME_TYPES:
        raise ValueError(f"game_type must be one of {UMPIRE_SCORECARD_GAME_TYPES}")


def _team(value: UmpireScorecardTeams, label: str) -> None:
    if not isinstance(value, UmpireScorecardTeams):
        raise TypeError(f"{label} must be a UmpireScorecardTeams value")


def _team_query(
    focus: UmpireScorecardTeams,
    side: str,
    opponent: UmpireScorecardTeams,
) -> str:
    _team(focus, "focus_team")
    _team(opponent, "opponent_team")
    if not isinstance(side, str):
        raise TypeError("focus_team_home_away must be a string")
    if side not in ("h", "a", "*"):
        raise ValueError("focus_team_home_away must be h, a, or *")
    if focus is not UmpireScorecardTeams.ALL and focus is opponent:
        raise ValueError("focus_team and opponent_team cannot be the same")
    query = "*" if focus is UmpireScorecardTeams.ALL else f"{focus.value}-{side}"
    if opponent is not UmpireScorecardTeams.ALL:
        opposite = {"h": "a", "a": "h", "*": "*"}[side]
        query += f"%3B{opponent.value}-{opposite}"
    return query


def _umpire_filters(name: str, min_games_called: int = 0) -> None:
    if not isinstance(name, str):
        raise TypeError("umpire_name must be a string")
    if type(min_games_called) is not int:
        raise TypeError("min_games_called must be an integer")
    if min_games_called < 0:
        raise ValueError("min_games_called must be nonnegative")


def _player_type(value: str) -> None:
    if not isinstance(value, str):
        raise TypeError("player_type must be a string")
    if value not in ("C", "P", "B"):
        raise ValueError("player_type must be C, P, or B")
