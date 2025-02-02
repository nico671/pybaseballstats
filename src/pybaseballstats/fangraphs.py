import asyncio
from typing import List

import pandas as pd
import polars as pl

from pybaseballstats.utils.fangraphs_utils import (
    FangraphsBattingPosTypes,
    FangraphsBattingStatType,
    FangraphsLeagueTypes,
    fangraphs_batting_range_async,
)
from pybaseballstats.utils.statcast_utils import _handle_dates


# TODO: Add more options
# - Add support for specifying team (team=) options are given by ints so need to make an enum for that
# - add support for restricting only to active roster players (rost=) (0 for all, 1 for active roster)
# - add support for season type (postseason=) ("" for regular season, "Y" for all postseason, "W" for world series, "L" for league championship series, "D" for division series, "F" for wild card game)
# - add support for handedness (hand=) ("" for all, "R" for right handed batters, "L" for left handed batters, "S" for switch hitters)
def fangraphs_batting_range(
    start_date: str = None,
    end_date: str = None,
    start_season: str = None,
    end_season: str = None,
    stat_types: List[FangraphsBattingStatType] = None,
    return_pandas: bool = False,
    pos: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    league: FangraphsLeagueTypes = FangraphsLeagueTypes.ALL,
    min_at_bats: str = "y",
    start_age: int = None,
    end_age: int = None,
    # rost: int = 0,
    # game_type: str = "",
    # team: int = 0,
    handedness: str = "",
) -> pl.DataFrame | pd.DataFrame:
    """Pulls batting data from Fangraphs for a given date range or season range. Additional options include filtering by position and league, as well as the ability to specify which stats to pull.

    Args:
        start_date (str, optional): First date for which you want to pull data for, format should follow "yyyy-mm-dd" (ex. ("2024-04-01")). Defaults to None.
        end_date (str, optional): Last date for which you want to pull data for, format should follow "yyyy-mm-dd" (ex. ("2024-06-01")). Defaults to None.
        start_season (str, optional): First season for which you want to pull data for, format should follow "yyyy" (ex. ("2023")). Defaults to None.
        end_season (str, optional): Last season for which you want to pull data for, format should follow "yyyy" (ex. ("2024")). Defaults to None.
        stat_types (List[FangraphsBattingStatType], optional): What stat types to include in the data. Defaults to None (all data types will be retrieved).
        return_pandas (bool, optional): Should the returned dataframe be a Polars Dataframe (False) or a Pandas dataframe (True). Defaults to False.
        pos (FangraphsBattingPosTypes, optional): What batter positions you want to include in your search. Defaults to FangraphsBattingPosTypes.ALL.
        league (FangraphsLeagueTypes, optional): What leagues you want included in your search. Defaults to FangraphsLeagueTypes.ALL.
        min_at_bats (str, optional): Minimum number of at bats to be included in the dataset (ex min_at_bats="123"). Defaults to "y" (qualified hitters).
        age (str, optional): Age range for players to include in the dataset (ex. age="20,25"). Defaults to None.
        handedness (str, optional): Handedness of batters to include in the dataset. Defaults to "" (all batters), options are "" (all), "R" (right_handed), "L" (left_handed), "S" (switch).

    Returns:
        pl.DataFrame | pd.DataFrame: A Polars or Pandas DataFrame containing the requested data.
    """
    # input validation
    if (start_date is None or end_date is None) and (
        start_season is None or end_season is None
    ):
        raise ValueError(
            "Either start_date and end_date must not be None or start_season and end_season must not be None"
        )

    elif (start_date is not None and end_date is None) or (
        start_date is None and end_date is not None
    ):
        raise ValueError(
            "Both start_date and end_date must be provided if one is provided"
        )

    elif (start_season is not None and end_season is None) or (
        start_season is None and end_season is not None
    ):
        raise ValueError(
            "Both start_season and end_season must be provided if one is provided"
        )
    if start_age is None and end_age is None:
        age = ""
    elif start_age is not None and end_age is not None:
        if start_age < 14 or start_age > 56:
            raise ValueError("start_age must be between 14 and 56")
        elif end_age < start_age:
            raise ValueError("end_age must be greater than start_age")
        else:
            age = f"{start_age},{end_age}"
    else:
        raise ValueError(
            "Both start_age and end_age must be provided if one is provided"
        )
    if handedness not in ["", "R", "L", "S"]:
        raise ValueError("handedness must be one of the following: '', 'R', 'L', 'S'")
    # convert start_date and end_date to datetime objects
    if start_date is not None and end_date is not None:
        start_date, end_date = _handle_dates(start_date, end_date)
    # run the async function and return the result
    return asyncio.run(
        fangraphs_batting_range_async(
            start_date,
            end_date,
            start_season,
            end_season,
            stat_types,
            return_pandas,
            pos,
            league,
            min_at_bats,
            age,
            handedness,
        )
    )


def fangraphs_pitching_range():
    print("Not implemented yet.")


def fangraphs_fielding_range():
    print("Not implemented yet.")
