import urllib

import pandas as pd
import polars as pl
import requests

from pybaseballstats.utils.statcast_utils import _handle_dates
from pybaseballstats.utils.umpire_scorecard_utils import (
    GAMES_URL,
    TEAMS_URL,
    UMPIRES_URL,
    UmpireScorecardTeams,
)


def umpire_games_date_range(
    start_date: str,
    end_date: str,
    season_type: str = "*",
    home_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    away_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    umpire_name: str = "",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Get a DataFrame of umpire games for a date range.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): Start date in 'YYYY-MM-DD' format.
        season_type (str, optional): Restrict games to only regular season games ("R"), only postseason games ("P") or both ("*"). Defaults to "*".
        home_team (UmpireScorecardTeams, optional): Restrict games to ones where the given team is the home team. Defaults to UmpireScorecardTeams.ALL.
        away_team (UmpireScorecardTeams, optional): Restrict games to ones where the given team is the away team. Defaults to UmpireScorecardTeams.ALL.
        umpire_name (str, optional): Restrict games to ones where the name of the umpire matches the parameter. If "" then all umpires are allowed. Defaults to "".
        return_pandas (bool, optional): If true return data as pandas Dataframe instead of a polars Dataframe. Defaults to False.

    Raises:
        ValueError: If start_date or end_date is None.
        ValueError: If season_type is not one of "*", "R", or "P".

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame of umpire games for the date range.
    """
    # input validation
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_date, end_date = _handle_dates(start_date, end_date)
    if season_type not in ["*", "R", "P"]:
        raise ValueError("season_type must be one of '*', 'R', or 'P'")
    umpire_name = "" if umpire_name is None else umpire_name
    url = GAMES_URL.format(
        season_type=season_type,
        start_date=start_date,
        end_date=end_date,
        home_team=home_team.value,
        away_team=away_team.value,
        umpire_name=urllib.parse.quote(umpire_name),
    )
    if umpire_name != "":
        print(url)
        print(requests.get(url).json())
    df = pl.DataFrame(requests.get(url).json()["games"], infer_schema_length=1000000000)
    return df if not return_pandas else df.to_pandas()


def umpire_stats_date_range(
    start_date: str,
    end_date: str,
    season_type: str = "*",
    home_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    away_team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Return a DataFrame of individual umpire stats for a date range.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): Start date in 'YYYY-MM-DD' format.
        season_type (str, optional): Restrict games to only regular season games ("R"), only postseason games ("P") or both ("*"). Defaults to "*".
        home_team (UmpireScorecardTeams, optional): Restrict games to ones where the given team is the home team. Defaults to UmpireScorecardTeams.ALL.
        away_team (UmpireScorecardTeams, optional): Restrict games to ones where the given team is the away team. Defaults to UmpireScorecardTeams.ALL.
        return_pandas (bool, optional): If true return data as pandas Dataframe instead of a polars Dataframe. Defaults to False.
    Raises:
        ValueError: If season_type is not one of "*", "R", or "P".
        ValueError: If start_date or end_date is None.

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame of umpire stats for the date range.
    """
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_date, end_date = _handle_dates(start_date, end_date)
    if season_type not in ["*", "R", "P"]:
        raise ValueError("season_type must be one of '*', 'R', or 'P'")
    url = UMPIRES_URL.format(
        season_type=season_type,
        start_date=start_date,
        end_date=end_date,
        home_team=home_team.value,
        away_team=away_team.value,
    )
    df = pl.DataFrame(
        requests.get(url).json()["umpires"], infer_schema_length=1000000000
    )
    return df if not return_pandas else df.to_pandas()


def team_umpire_stats_date_range(
    start_date: str,
    end_date: str,
    season_type: str = "*",
    team: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    home_away: str = "*",
    stadium: UmpireScorecardTeams = UmpireScorecardTeams.ALL,
    umpire_name: str = "",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Return a DataFrame of team umpire stats for a date range.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): Start date in 'YYYY-MM-DD' format.
        season_type (str, optional): Restrict games to only regular season games ("R"), only postseason games ("P") or both ("*"). Defaults to "*".
        team (UmpireScorecardTeams, optional): Restrict data to a specific team only. Defaults to UmpireScorecardTeams.ALL.
        home_away (str, optional): Restrict data to be calculated on only home games ("h"), away games ("a") or both ("*"). Defaults to "*".
        stadium (UmpireScorecardTeams, optional): Restrict data to be calculated on only games occuring at the given stadium. Defaults to UmpireScorecardTeams.ALL.
        umpire_name (str, optional): Restrict data to be calculated only for a given umpire. Defaults to "".
        return_pandas (bool, optional): If true return data as pandas Dataframe instead of a polars Dataframe. Defaults to False.

    Raises:
        ValueError: If season_type is not one of "*", "R", or "P".
        ValueError: If home_away is not one of "*", "h", or "a".
        ValueError: If start_date or end_date is None.

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame of team umpire stats for the date range.
    """
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided.")
    start_date, end_date = _handle_dates(start_date, end_date)
    if season_type not in ["*", "R", "P"]:
        raise ValueError("season_type must be one of '*', 'R', or 'P'")
    if home_away not in ["*", "h", "a"]:
        raise ValueError("home_away must be one of '*', 'h', or 'a'")
    umpire_name = "" if umpire_name is None else umpire_name
    url = TEAMS_URL.format(
        season_type=season_type,
        start_date=start_date,
        end_date=end_date,
        umpire_name=urllib.parse.quote(umpire_name),
        team=team.value,
        home_away=home_away,
        stadium=stadium.value,
    )
    df = pl.DataFrame(requests.get(url).json()["teams"], infer_schema_length=1000000000)
    return df if not return_pandas else df.to_pandas()
