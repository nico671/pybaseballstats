import json
from enum import Enum
from typing import Literal

# TODO: usage docs
import dateparser
import pandas as pd
import polars as pl
import requests

from pybaseballstats.utils.umpire_scorecard_consts import (
    UMPIRE_SCORECARD_GAMES_URL,
    UMPIRE_SCORECARD_TEAMS_URL,
    UMPIRE_SCORECARD_UMPIRES_URL,
)


class UmpireScorecardTeams(Enum):
    ALL = "*"
    DIAMONDBACKS = "AZ"
    ATHLETICS = "ATH"
    BRAVES = "ATL"
    ORIOLES = "BAL"
    RED_SOX = "BOS"
    CUBS = "CHC"
    REDS = "CIN"
    WHITE_SOX = "CWS"
    GAURDIANS = "CLE"
    ROCKIES = "COL"
    ASTROS = "HOU"
    ROYALS = "KC"
    ANGELS = "LAA"
    DODGERS = "LAD"
    MARLINS = "MIA"
    BREWERS = "MIL"
    TWINS = "MIN"
    METS = "NYM"
    YANKEES = "NYY"
    PHILLIES = "PHI"
    PIRATES = "PIT"
    PADRES = "SD"
    MARINERS = "SEA"
    GIANTS = "SF"
    CARDINALS = "STL"
    RAYS = "TB"
    RANGERS = "TEX"
    BLUE_JAYS = "TOR"
    NATIONALS = "WSH"


def umpire_scorecard_games_date_range(
    start_date: str,
    end_date: str,
    game_type: Literal["*", "R", "A", "P", "F", "D", "L", "W"] = "*",
    focus_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    focus_team_home_away: Literal["h", "a", "*"] = "*",
    opponent_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    umpire_name: str = "",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_dt = dateparser.parse(start_date)
    end_dt = dateparser.parse(end_date)

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

    resp = requests.get(
        UMPIRE_SCORECARD_GAMES_URL.format(
            start_date=start_date,
            end_date=end_date,
            game_type=game_type,
            team=team_string,
        )
    )

    df = pl.DataFrame(
        json.loads(resp.text)["rows"],
    )
    if umpire_name:
        df = df.filter(pl.col("umpire").str.contains(umpire_name))
    return df if not return_pandas else df.to_pandas()


def umpire_scorecard_umpires_date_range(
    start_date: str,
    end_date: str,
    game_type: Literal["*", "R", "A", "P", "F", "D", "L", "W"] = "*",
    focus_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    focus_team_home_away: Literal["h", "a", "*"] = "*",
    opponent_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    umpire_name: str = "",
    min_games_called: int = 0,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_dt = dateparser.parse(start_date)
    end_dt = dateparser.parse(end_date)

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
    if umpire_name:
        df = df.filter(pl.col("umpire").str.contains(umpire_name))
    if min_games_called > 0:
        df = df.filter(pl.col("n") >= min_games_called)
    return df


def umpire_scorecard_teams_date_range(
    start_date: str,
    end_date: str,
    game_type: Literal["*", "R", "A", "P", "F", "D", "L", "W"] = "*",
    focus_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_dt = dateparser.parse(start_date)
    end_dt = dateparser.parse(end_date)

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
    return df if not return_pandas else df.to_pandas()
