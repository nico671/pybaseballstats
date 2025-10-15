import json
from typing import Literal

import dateparser
import polars as pl
import requests

from .consts.umpire_scorecard_consts import (
    UMPIRE_SCORECARD_GAMES_URL,
    UMPIRE_SCORECARD_TEAMS_URL,
    UMPIRE_SCORECARD_UMPIRES_URL,
    UmpireScorecardTeams,
)

__all__ = [
    "game_type_options",
    "game_data",
    "umpire_data",
    "team_data",
    "UmpireScorecardTeams",
]


def game_type_options():
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
    """Fetches umpire scorecard data for individual games within a given date range. Essentially functions as a wrapper around the following URL: https://umpscorecards.com/data/games

    Args:
        start_date (str): The first date to start fetching data from.
        end_date (str): The last date to fetch data from.
        game_type (Literal["*", "R", "A", "P", "F", "D", "L", "W"], optional): The type of game to filter by. To see a description on the different game type options call the `game_type_options` function Defaults to "*".
        focus_team (UmpireScorecardTeams, optional): The team to return data on. To see all team options call the `available_teams` function. Defaults to UmpireScorecardTeams.ALL.
        focus_team_home_away (Literal["h", "a", "*"], optional): Whether to return home or away games for the focus team. To see a description on the different game type options call the `game_type_options` function Defaults to "*".
        opponent_team (UmpireScorecardTeams, optional): The opponent team to filter by. To see all team options call the `available_teams` function. Defaults to UmpireScorecardTeams.ALL.
        umpire_name (str, optional): The name of the umpire to filter by. Defaults to "".

    Raises:
        ValueError: If both start_date and end_date are not provided.
        ValueError: If start_date is after end_date.
        ValueError: If start_date or end_date are before 2015.
        ValueError: If game_type is not one of the allowed values.
        ValueError: If focus_team and opponent_team are the same.
        ValueError: If focus_team_home_away is not one of the allowed values.
        ValueError: If focus_team is not a valid UmpireScorecardTeams value.
        ValueError: If opponent_team is not a valid UmpireScorecardTeams value.

    Returns:
        pl.DataFrame: A polars DataFrame containing the umpire scorecard data for individual games within the specified date range.
    """

    # Input validation
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_dt = dateparser.parse(start_date)
    end_dt = dateparser.parse(end_date)
    assert start_dt is not None, "Failed to parse start_date"
    assert end_dt is not None, "Failed to parse end_date"
    if start_dt > end_dt:
        raise ValueError("start_date must be before end_date.")
    if start_dt.year < 2015 or end_dt.year < 2015:
        raise ValueError("start_date and end_date must be after 2015.")
    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = end_dt.strftime("%Y-%m-%d")

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
            start_date=start_date,
            end_date=end_date,
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
    """Returns information on umpires who have officiated games within a given date range. Essentially functions as a wrapper around the following URL: https://umpscorecards.com/data/umpires

    Args:
        start_date (str): The start date for the query.
        end_date (str): The end date for the query.
        game_type (Literal["*", "R", "A", "P", "F", "D", "L", "W"], optional): The type of game to filter by. To see a description on the different game type options call the `game_type_options` function Defaults to "*".
        focus_team (UmpireScorecardTeams, optional): The team to focus on. To see all team options call the `available_teams` function. Defaults to UmpireScorecardTeams.ALL.
        focus_team_home_away (Literal["h", "a", "*"], optional): Whether to focus on home or away games. To see a description on the different game type options call the `game_type_options` function Defaults to "*".
        opponent_team (UmpireScorecardTeams, optional): The opponent team to filter by. To see all team options call the `available_teams` function. Defaults to UmpireScorecardTeams.ALL.
        umpire_name (str, optional): The name of the umpire to filter by. Defaults to "".
        min_games_called (int, optional): The minimum number of games the umpire must have called. Defaults to 0.

    Raises:
        ValueError: If both start_date and end_date are not provided.
        ValueError: If start_date is after end_date.
        ValueError: If start_date or end_date are before 2015.
        ValueError: If game_type is not one of the allowed values.
        ValueError: If focus_team is not one of the allowed values.
        ValueError: If focus_team_home_away is not one of the allowed values.
        ValueError: If opponent_team is not one of the allowed values.
        ValueError: If umpire_name is not a string.
        ValueError: If min_games_called is not a positive integer.
        ValueError: If focus_team is not provided.
        ValueError: If focus_team_home_away is not provided.
        ValueError: If opponent_team is not provided.

    Returns:
        pl.DataFrame: A polars DataFrame containing information on umpires who have officiated games within the specified date range.
    """
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_dt = dateparser.parse(start_date)
    end_dt = dateparser.parse(end_date)
    assert start_dt is not None, "Failed to parse start_date"
    assert end_dt is not None, "Failed to parse end_date"
    if start_dt > end_dt:
        raise ValueError("start_date must be before end_date.")
    if start_dt.year < 2015 or end_dt.year < 2015:
        raise ValueError("start_date and end_date must be after 2015.")
    if start_dt.year > 2025 or end_dt.year > 2025:
        raise ValueError("start_date and end_date must be before 2024.")
    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = end_dt.strftime("%Y-%m-%d")

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
            start_date=start_date,
            end_date=end_date,
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
    """Retrieve umpire performance data for teams within a specified date range. Essentially functions as a wrapper around the following URL: https://umpscorecards.com/data/teams

    Args:
        start_date (str): The start date for the data retrieval in YYYY-MM-DD format.
        end_date (str): The end date for the data retrieval in YYYY-MM-DD format.
        game_type (Literal["*", "R", "A", "P", "F", "D", "L", "W"], optional): The type of games to include. To see a description on the different game type options call the `game_type_options` function Defaults to "*".
        focus_team (UmpireScorecardTeams, optional): The team to focus on. To see all team options call the `available_teams` function. Defaults to UmpireScorecardTeams.ALL.

    Raises:
        ValueError: If start_date or end_date is not provided.
        ValueError: If start_date is after end_date.
        ValueError: If game_type is not one of the allowed values.
        ValueError: If focus_team is not a valid UmpireScorecardTeams value.

    Returns:
        pl.DataFrame: A DataFrame containing the requested team data.
    """
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_dt = dateparser.parse(start_date)
    end_dt = dateparser.parse(end_date)
    assert start_dt is not None, "Failed to parse start_date"
    assert end_dt is not None, "Failed to parse end_date"
    if start_dt > end_dt:
        raise ValueError("start_date must be before end_date.")
    if start_dt.year < 2015 or end_dt.year < 2015:
        raise ValueError("start_date and end_date must be after 2015.")
    if start_dt.year > 2025 or end_dt.year > 2025:
        raise ValueError("start_date and end_date must be before 2024.")
    start_date = start_dt.strftime("%Y-%m-%d")
    end_date = end_dt.strftime("%Y-%m-%d")

    if game_type not in ["*", "R", "A", "P", "F", "D", "L", "W"]:
        raise ValueError(
            "game_type must be one of '*', 'R', 'A', 'P', 'F', 'D', 'L', or 'W'"
        )

    resp = requests.get(
        UMPIRE_SCORECARD_TEAMS_URL.format(
            start_date=start_date,
            end_date=end_date,
            game_type=game_type,
        )
    )

    df = pl.DataFrame(
        json.loads(resp.text)["rows"],
    )
    if focus_team != UmpireScorecardTeams.ALL:
        df = df.filter(pl.col("team").str.contains(focus_team.value))
    return df


if __name__ == "__main__":
    print(
        game_data(
            start_date="2023-04-01",
            end_date="2023-07-07",
            focus_team=UmpireScorecardTeams.ANGELS,
            focus_team_home_away="a",
            opponent_team=UmpireScorecardTeams.RANGERS,
        )
    )
