import asyncio
from typing import List

import pandas as pd
import polars as pl

from pybaseballstats.utils.fangraphs_utils import (
    FangraphsBattingPosTypes,
    FangraphsBattingStatType,
    FangraphsLeagueTypes,
    FangraphsStatSplitTypes,
    FangraphsTeams,
    fangraphs_batting_range_async,
)
from pybaseballstats.utils.statcast_utils import _handle_dates


# TODO: fix age range and game_type
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
    # start_age: int = None,
    # end_age: int = None,
    handedness: str = "",
    rost: int = 0,
    # game_type: str = "",
    team: FangraphsTeams = FangraphsTeams.ALL,
    stat_split: FangraphsStatSplitTypes = FangraphsStatSplitTypes.PLAYER,
) -> pl.DataFrame | pd.DataFrame:
    """Fetches batting statistics from Fangraphs within a specified date or season range.

    start_date (str, optional): The start date for the range in 'YYYY-MM-DD' format. Defaults to None.
    end_date (str, optional): The end date for the range in 'YYYY-MM-DD' format. Defaults to None.
    start_season (str, optional): The start season for the range. Defaults to None.
    end_season (str, optional): The end season for the range. Defaults to None.
    stat_types (List[FangraphsBattingStatType], optional): List of stat types to fetch. Defaults to None.
    return_pandas (bool, optional): Whether to return the result as a pandas DataFrame. Defaults to False.
    pos (FangraphsBattingPosTypes, optional): The position type to filter by. Defaults to FangraphsBattingPosTypes.ALL.
    league (FangraphsLeagueTypes, optional): The league type to filter by. Defaults to FangraphsLeagueTypes.ALL.
    min_at_bats (str, optional): Minimum at-bats qualifier. Defaults to "y".
    handedness (str, optional): The handedness of the batter ('', 'R', 'L', 'S'). Defaults to "".
    rost (int, optional): Roster status (0 for all players, 1 for active roster). Defaults to 0.
    team (FangraphsTeams, optional): The team to filter by. Defaults to FangraphsTeams.ALL.
    stat_split (FangraphsStatSplitTypes, optional): The stat split type. Defaults to FangraphsStatSplitTypes.PLAYER.

    ValueError: If both start_date and end_date are not provided or both start_season and end_season are not provided.
    ValueError: If only one of start_date or end_date is provided.
    ValueError: If only one of start_season or end_season is provided.
    ValueError: If handedness is not one of '', 'R', 'L', 'S'.
    ValueError: If rost is not 0 or 1.

    pl.DataFrame | pd.DataFrame: The fetched batting statistics as a Polars or pandas DataFrame."""
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
    # if start_age is None and end_age is None:
    #     age = ""
    # elif start_age is not None and end_age is not None:
    #     if start_age < 14 or start_age > 56:
    #         raise ValueError("start_age must be between 14 and 56")
    #     elif end_age < start_age:
    #         raise ValueError("end_age must be greater than start_age")
    #     else:
    #         age = f"{start_age},{end_age}"
    # else:
    #     raise ValueError(
    #         "Both start_age and end_age must be provided if one is provided"
    #     )
    if handedness not in ["", "R", "L", "S"]:
        raise ValueError("handedness must be one of the following: '', 'R', 'L', 'S'")
    if rost not in [0, 1]:
        raise ValueError("rost must be either 0 (all players) or 1 (active roster)")
    # if game_type not in ["", "Y", "W", "L", "D", "F"]:
    #     raise ValueError(
    #         "game_type must be one of the following: '', 'Y', 'W', 'L', 'D', 'F'"
    #     )

    if stat_split.value != "":
        team = f"{team},{stat_split.value}"
    else:
        team = f"{team.value}"
    # convert start_date and end_date to datetime objects
    if start_date is not None and end_date is not None:
        start_date, end_date = _handle_dates(start_date, end_date)
    # run the async function and return the result
    return asyncio.run(
        fangraphs_batting_range_async(
            start_date=start_date,
            end_date=end_date,
            start_season=start_season,
            end_season=end_season,
            stat_types=stat_types,
            return_pandas=return_pandas,
            pos=pos,
            league=league,
            min_at_bats=min_at_bats,
            # age=age,
            rost=rost,
            # game_type,
            team=team,
            handedness=handedness,
        )
    )


def fangraphs_pitching_range():
    print("Not implemented yet.")


def fangraphs_fielding_range():
    print("Not implemented yet.")
