import json
from datetime import datetime
from typing import Literal

import polars as pl
import requests

from pybaseballstats.consts.umpire_scorecard_consts import (
    UMPIRE_SCORECARD_GAMES_URL,
    UMPIRE_SCORECARD_TEAMS_URL,
    UMPIRE_SCORECARD_UMPIRES_URL,
    UMPIRE_SCORECARDS_PLAYERS_URL,
    UmpireScorecardTeams,
)

__all__ = [
    "game_type_options",
    "player_data",
    "game_data",
    "umpire_data",
    "team_data",
    "UmpireScorecardTeams",
]


def game_type_options():
    """Print supported game type filter codes for Umpire Scorecards endpoints."""
    print(
        """Game Type Options:
* : All games
R : Regular Season
A : All-Star Game
P : All Postseason games
F : Wild Card games
D : Division Series games
L : League Championship Series games
W : World Series games"""
    )


def game_data(
    start_date: str,
    end_date: str,
    game_type: Literal["*", "R", "A", "P", "F", "D", "L", "W"] = "*",
    focus_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    focus_team_home_away: Literal["h", "a", "*"] = "*",
    opponent_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    umpire_name: str = "",
) -> pl.DataFrame:
    """Return game-level Umpire Scorecards data for a date range.

    Args:
        start_date (str): Inclusive start date in ``YYYY-MM-DD`` format.
        end_date (str): Inclusive end date in ``YYYY-MM-DD`` format.
        game_type (Literal["*", "R", "A", "P", "F", "D", "L", "W"], optional):
            Season/game-type filter.
        focus_team (UmpireScorecardTeams, optional): Team filter.
        focus_team_home_away (Literal["h", "a", "*"], optional): Home/away
            side for ``focus_team``.
        opponent_team (UmpireScorecardTeams, optional): Opponent team filter.
        umpire_name (str, optional): Optional substring match for umpire name.

    Raises:
        ValueError: If dates are missing or invalid.
        ValueError: If date bounds are outside supported years.
        ValueError: If team/game filters are invalid.

    Returns:
        pl.DataFrame: Game-level Umpire Scorecards rows.
    """

    # Input validation
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    assert start_dt is not None, "Failed to parse start_date"
    assert end_dt is not None, "Failed to parse end_date"
    if start_dt > end_dt:
        raise ValueError("start_date must be before end_date.")
    if start_dt.year < 2015 or end_dt.year < 2015:
        raise ValueError("start_date and end_date must be after 2015.")
    if start_dt.year > datetime.now().year or end_dt.year > datetime.now().year:
        raise ValueError("start_date and end_date must be before the current year.")
    start_date_str = start_dt.strftime("%Y-%m-%d")
    end_date_str = end_dt.strftime("%Y-%m-%d")

    if game_type not in ["*", "R", "A", "P", "F", "D", "L", "W"]:
        raise ValueError(
            "game_type must be one of '*', 'R', 'A', 'P', 'F', 'D', 'L', or 'W'"
        )
    assert isinstance(focus_team, UmpireScorecardTeams)
    assert isinstance(opponent_team, UmpireScorecardTeams)
    if focus_team_home_away not in ["h", "a", "*"]:
        raise ValueError("focus_team_home_away must be one of 'h', 'a', or '*'")
    if focus_team != UmpireScorecardTeams.ALL and focus_team == opponent_team:
        raise ValueError("focus_team and opponent_team cannot be the same")

    if focus_team:
        if focus_team == UmpireScorecardTeams.ALL:
            team_string = "*"
        else:
            team_string = f"{focus_team.value}-{focus_team_home_away}"
        if opponent_team:
            if opponent_team != UmpireScorecardTeams.ALL:
                team_string += f"%3B{opponent_team.value}"
                if focus_team_home_away == "*":
                    team_string += "-*"
                if focus_team_home_away == "h":
                    team_string += "-a"
                if focus_team_home_away == "a":
                    team_string += "-h"
    # call to the internal Umpire Scorecard API
    resp = requests.get(
        UMPIRE_SCORECARD_GAMES_URL.format(
            start_date=start_date_str,
            end_date=end_date_str,
            game_type=game_type,
            team=team_string,
        )
    )

    # loading the data into a polars dataframe
    df = pl.DataFrame(
        json.loads(resp.text)["rows"],
    )
    # filtering by umpire name if provided
    if umpire_name != "" and umpire_name is not None:
        unique_umpire_names = df.select(pl.col("umpire").unique()).to_series().to_list()
        if umpire_name not in unique_umpire_names:
            print(
                f"Warning: The umpire name '{umpire_name}' was not found in the data. Returning all umpires instead."
            )
            return df
        else:
            df = df.filter(pl.col("umpire").str.contains(umpire_name))
    return df


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
    """Return umpire-level aggregated Umpire Scorecards data.

    Args:
        start_date (str): Inclusive start date in ``YYYY-MM-DD`` format.
        end_date (str): Inclusive end date in ``YYYY-MM-DD`` format.
        game_type (Literal["*", "R", "A", "P", "F", "D", "L", "W"], optional):
            Season/game-type filter.
        focus_team (UmpireScorecardTeams, optional): Team filter.
        focus_team_home_away (Literal["h", "a", "*"], optional): Home/away
            side for ``focus_team``.
        opponent_team (UmpireScorecardTeams, optional): Opponent team filter.
        umpire_name (str, optional): Optional substring match for umpire name.
        min_games_called (int, optional): Minimum games threshold.

    Raises:
        ValueError: If dates are missing or invalid.
        ValueError: If date bounds are outside supported years.
        ValueError: If team/game filters are invalid.
        ValueError: If ``min_games_called`` is negative.

    Returns:
        pl.DataFrame: Umpire-level aggregated rows.
    """
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    assert start_dt is not None, "Failed to parse start_date"
    assert end_dt is not None, "Failed to parse end_date"
    if start_dt > end_dt:
        raise ValueError("start_date must be before end_date.")
    if start_dt.year < 2015 or end_dt.year < 2015:
        raise ValueError("start_date and end_date must be after 2015.")
    if start_dt.year > datetime.now().year or end_dt.year > datetime.now().year:
        raise ValueError("start_date and end_date must be before the current year.")
    start_date_str = start_dt.strftime("%Y-%m-%d")
    end_date_str = end_dt.strftime("%Y-%m-%d")

    if game_type not in ["*", "R", "A", "P", "F", "D", "L", "W"]:
        raise ValueError(
            "game_type must be one of '*', 'R', 'A', 'P', 'F', 'D', 'L', or 'W'"
        )

    assert isinstance(focus_team, UmpireScorecardTeams)
    assert isinstance(opponent_team, UmpireScorecardTeams)
    if focus_team_home_away not in ["h", "a", "*"]:
        raise ValueError("focus_team_home_away must be one of 'h', 'a', or '*'")
    if focus_team != UmpireScorecardTeams.ALL and focus_team == opponent_team:
        raise ValueError("focus_team and opponent_team cannot be the same")
    if not focus_team and opponent_team:
        raise ValueError("You cannot provide an opponent_team without a focus_team")
    if focus_team:
        if focus_team == UmpireScorecardTeams.ALL:
            team_string = "*"
        else:
            team_string = f"{focus_team.value}-{focus_team_home_away}"
        if opponent_team:
            if opponent_team != UmpireScorecardTeams.ALL:
                team_string += f"%3B{opponent_team.value}"
                if focus_team_home_away == "*":
                    team_string += "-*"
                if focus_team_home_away == "h":
                    team_string += "-a"
                if focus_team_home_away == "a":
                    team_string += "-h"
    if min_games_called < 0:
        raise ValueError("min_games_called must be greater than or equal to 0")
    resp = requests.get(
        UMPIRE_SCORECARD_UMPIRES_URL.format(
            start_date=start_date_str,
            end_date=end_date_str,
            game_type=game_type,
            team=team_string,
        )
    )

    df = pl.DataFrame(
        json.loads(resp.text)["rows"],
    )
    if umpire_name != "" and umpire_name is not None:
        unique_umpire_names = df.select(pl.col("umpire").unique()).to_series().to_list()
        if umpire_name not in unique_umpire_names:
            print(
                f"Warning: The umpire name '{umpire_name}' was not found in the data. Returning all umpires instead."
            )
            return df
        else:
            df = df.filter(pl.col("umpire").str.contains(umpire_name))
    if min_games_called > 0:
        df = df.filter(pl.col("n") >= min_games_called)
    return df


def team_data(
    start_date: str,
    end_date: str,
    game_type: Literal["*", "R", "A", "P", "F", "D", "L", "W"] = "*",
    focus_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
) -> pl.DataFrame:
    """Return team-level aggregated Umpire Scorecards data.

    Args:
        start_date (str): Inclusive start date in ``YYYY-MM-DD`` format.
        end_date (str): Inclusive end date in ``YYYY-MM-DD`` format.
        game_type (Literal["*", "R", "A", "P", "F", "D", "L", "W"], optional):
            Season/game-type filter.
        focus_team (UmpireScorecardTeams, optional): Team filter.

    Raises:
        ValueError: If dates are missing or invalid.
        ValueError: If date bounds are outside supported years.
        ValueError: If ``game_type`` is invalid.

    Returns:
        pl.DataFrame: Team-level aggregated rows.
    """
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    assert start_dt is not None, "Failed to parse start_date"
    assert end_dt is not None, "Failed to parse end_date"
    if start_dt > end_dt:
        raise ValueError("start_date must be before end_date.")
    if start_dt.year < 2015 or end_dt.year < 2015:
        raise ValueError("start_date and end_date must be after 2015.")
    if start_dt.year > datetime.now().year or end_dt.year > datetime.now().year:
        raise ValueError("start_date and end_date must be before the current year.")
    start_date_str = start_dt.strftime("%Y-%m-%d")
    end_date_str = end_dt.strftime("%Y-%m-%d")

    if game_type not in ["*", "R", "A", "P", "F", "D", "L", "W"]:
        raise ValueError(
            "game_type must be one of '*', 'R', 'A', 'P', 'F', 'D', 'L', or 'W'"
        )

    resp = requests.get(
        UMPIRE_SCORECARD_TEAMS_URL.format(
            start_date=start_date_str,
            end_date=end_date_str,
            game_type=game_type,
        )
    )

    df = pl.DataFrame(
        json.loads(resp.text)["rows"],
    )
    if focus_team != UmpireScorecardTeams.ALL:
        df = df.filter(pl.col("team").str.contains(focus_team.value))
    return df


def player_data(
    start_date: str,
    end_date: str,
    player_type: Literal["C", "P", "B"],
    game_type: Literal["*", "R", "A", "P", "F", "D", "L", "W"] = "*",
    team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
) -> pl.DataFrame:
    """Return player-level Umpire Scorecards data.

    Args:
        start_date (str): Inclusive start date in ``YYYY-MM-DD`` format.
        end_date (str): Inclusive end date in ``YYYY-MM-DD`` format.
        player_type (Literal["C", "P", "B"]): Player group filter.
        game_type (Literal["*", "R", "A", "P", "F", "D", "L", "W"], optional):
            Season/game-type filter.
        team (UmpireScorecardTeams, optional): Team filter.

    Raises:
        ValueError: If dates are missing or invalid.
        ValueError: If date bounds are outside supported years.
        ValueError: If ``game_type`` or ``player_type`` is invalid.
        ValueError: If the upstream API responds with HTTP errors or no rows.

    Returns:
        pl.DataFrame: Player-level rows.
    """
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("start_date must be in YYYY-MM-DD format.")
    try:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("end_date must be in YYYY-MM-DD format.")
    assert start_dt is not None, "Failed to parse start_date"
    assert end_dt is not None, "Failed to parse end_date"
    if start_dt > end_dt:
        raise ValueError("start_date must be before end_date.")
    if start_dt.year < 2015 or end_dt.year < 2015:
        raise ValueError("start_date and end_date must be after 2015.")
    if start_dt.year > datetime.now().year or end_dt.year > datetime.now().year:
        raise ValueError("start_date and end_date must be before the current year.")
    start_date_str = start_dt.strftime("%Y-%m-%d")
    end_date_str = end_dt.strftime("%Y-%m-%d")

    if game_type not in ["*", "R", "A", "P", "F", "D", "L", "W"]:
        raise ValueError(
            "game_type must be one of '*', 'R', 'A', 'P', 'F', 'D', 'L', or 'W'"
        )
    if player_type not in ["C", "P", "B"]:
        raise ValueError("player_type must be one of 'C', 'P', or 'B'")
    assert isinstance(team, UmpireScorecardTeams)

    resp = requests.get(
        UMPIRE_SCORECARDS_PLAYERS_URL.format(
            player_type=player_type,
            start_date=start_date_str,
            end_date=end_date_str,
            game_type=game_type,
            team=team.value,
        )
    )
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"HTTP error occurred: {e}")
    try:
        df = pl.DataFrame(
            json.loads(resp.text)["rows"],
        )
    except KeyError:
        raise ValueError("No data found for the given parameters.")
    return df
