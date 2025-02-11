import asyncio
from typing import List

import pandas as pd
import polars as pl

from pybaseballstats.utils.fangraphs_utils import (
    FangraphsBattingPosTypes,
    FangraphsBattingStatType,
    FangraphsLeagueTypes,
    FangraphsPitchingStatType,
    FangraphsStatSplitTypes,
    FangraphsTeams,
    fangraphs_batting_range_async,
    fangraphs_fielding_range_async,
    fangraphs_pitching_range_async,
    gen_input_val,
)


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
    qual: str = "y",
    handedness: str = "",
    rost: int = 0,
    team: FangraphsTeams = FangraphsTeams.ALL,
    stat_split: FangraphsStatSplitTypes = FangraphsStatSplitTypes.PLAYER,
) -> pl.DataFrame | pd.DataFrame:
    """Fetches batting statistics from Fangraphs within a specified date or season range.
    Args:
        start_date (str, optional): The start date for the range in 'YYYY-MM-DD' format. Defaults to None.
        end_date (str, optional): The end date for the range in 'YYYY-MM-DD' format. Defaults to None.
        start_season (str, optional): The start season for the range. Defaults to None.
        end_season (str, optional): The end season for the range. Defaults to None.
        stat_types (List[FangraphsBattingStatType], optional): List of stat types to fetch. Defaults to None.
        return_pandas (bool, optional): Whether to return the result as a pandas DataFrame. Defaults to False.
        pos (FangraphsBattingPosTypes, optional): The position type to filter by. Defaults to FangraphsBattingPosTypes.ALL.
        league (FangraphsLeagueTypes, optional): The league type to filter by. Defaults to FangraphsLeagueTypes.ALL.
        qual (str, optional): Minimum at-bats qualifier. Defaults to "y".
        handedness (str, optional): The handedness of the batter ('', 'R', 'L', 'S'). Defaults to "".
        rost (int, optional): Roster status (0 for all players, 1 for active roster). Defaults to 0.
        team (FangraphsTeams, optional): The team to filter by. Defaults to FangraphsTeams.ALL.
        stat_split (FangraphsStatSplitTypes, optional): The stat split type. Defaults to FangraphsStatSplitTypes.PLAYER.
    Raises:
        ValueError: If both start_date and end_date are not provided or both start_season and end_season are not provided.
        ValueError: If only one of start_date or end_date is provided.
        ValueError: If only one of start_season or end_season is provided.
        ValueError: If handedness is not one of '', 'R', 'L', 'S'.
        ValueError: If rost is not 0 or 1.
    Returns:
        pl.DataFrame | pd.DataFrame: The fetched batting statistics as a Polars or pandas DataFrame."""
    start_date, end_date, start_season, end_season, team = gen_input_val(
        start_date=start_date,
        end_date=end_date,
        start_season=start_season,
        end_season=end_season,
        rost=rost,
        team=team,
        stat_split=stat_split,
    )
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
            qual=qual,
            rost=rost,
            team=team,
            handedness=handedness,
        )
    )


def fangraphs_pitching_range(
    start_date: str = None,
    end_date: str = None,
    start_season: str = None,
    end_season: str = None,
    stat_types: List[FangraphsPitchingStatType] = None,
    starter_reliever: str = "pit",  # stats in url ("sta", "rel", "pit")
    return_pandas: bool = False,
    league: FangraphsLeagueTypes = FangraphsLeagueTypes.ALL,
    team: FangraphsTeams = FangraphsTeams.ALL,
    rost: int = 0,
    handedness: str = "",
    stat_split: FangraphsStatSplitTypes = FangraphsStatSplitTypes.PLAYER,
) -> pl.DataFrame | pd.DataFrame:
    """Fetches pitching statistics from Fangraphs within a specified date or season range.
    Args:
        start_date (str, optional): The start date for the range in 'YYYY-MM-DD' format. Defaults to None.
        end_date (str, optional): The end date for the range in 'YYYY-MM-DD' format. Defaults to None.
        start_season (str, optional): The start season for the range in 'YYYY' format. Defaults to None.
        end_season (str, optional): The end season for the range in 'YYYY' format. Defaults to None.
        stat_types (List[FangraphsPitchingStatType], optional): List of pitching stat types to retrieve. Defaults to None.
        starter_reliever (str, optional): Filter for starters, relievers, or all. Defaults to "all".
        return_pandas (bool, optional): Whether to return the result as a pandas DataFrame. Defaults to False.
        league (FangraphsLeagueTypes, optional): The league to filter by. Defaults to FangraphsLeagueTypes.ALL.
        team (FangraphsTeams, optional): The team to filter by. Defaults to FangraphsTeams.ALL.
        qual (str, optional): Qualification status. Defaults to "y".
        rost (int, optional): Roster status, 0 for all players, 1 for active roster. Defaults to 0.
        handedness (str, optional): Filter by handedness (e.g., 'R' for right-handed, 'L' for left-handed). Defaults to "".
        stat_split (FangraphsStatSplitTypes, optional): The type of stat split to apply. Defaults to FangraphsStatSplitTypes.PLAYER.
    Raises:
        ValueError: If both start_date and end_date are not provided or both start_season and end_season are not provided.
        ValueError: If only one of start_date or end_date is provided.
        ValueError: If only one of start_season or end_season is provided.
        ValueError: If rost is not 0 or 1.
    Returns:
        pl.DataFrame | pd.DataFrame: The pitching statistics as a Polars or pandas DataFrame.
    """
    # input validation
    if starter_reliever not in ["sta", "rel", "pit"]:
        raise ValueError("starter_reliever must be one of 'sta', 'rel', or 'pit'.")
    start_date, end_date, start_season, end_season, team = gen_input_val(
        start_date=start_date,
        end_date=end_date,
        start_season=start_season,
        end_season=end_season,
        rost=rost,
        team=team,
        stat_split=stat_split,
    )
    return asyncio.run(
        fangraphs_pitching_range_async(
            start_date=start_date,
            end_date=end_date,
            start_season=start_season,
            end_season=end_season,
            stat_types=stat_types,
            return_pandas=return_pandas,
            league=league,
            qual="y",
            rost=rost,
            team=team,
            handedness=handedness,
            starter_reliever=starter_reliever,
        )
    )


def fangraphs_fielding_range(
    start_date: str = None,
    end_date: str = None,
    start_season: str = None,
    end_season: str = None,
    stat_types: List[FangraphsPitchingStatType] = None,
    return_pandas: bool = False,
    league: FangraphsLeagueTypes = FangraphsLeagueTypes.ALL,
    team: FangraphsTeams = FangraphsTeams.ALL,
    qual: str = "y",
    rost: int = 0,
    pos: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    stat_split: FangraphsStatSplitTypes = FangraphsStatSplitTypes.PLAYER,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieve fielding range statistics from Fangraphs.

    Args:
        start_date (str, optional): The start date for the range in 'YYYY-MM-DD' format. Defaults to None.
        end_date (str, optional): The end date for the range in 'YYYY-MM-DD' format. Defaults to None.
        start_season (str, optional): The start season year. Defaults to None.
        end_season (str, optional): The end season year. Defaults to None.
        stat_types (List[FangraphsPitchingStatType], optional): List of pitching stat types to retrieve. Defaults to None.
        return_pandas (bool, optional): Whether to return the result as a pandas DataFrame. Defaults to False.
        league (FangraphsLeagueTypes, optional): The league type to filter by. Defaults to FangraphsLeagueTypes.ALL.
        team (FangraphsTeams, optional): The team to filter by. Defaults to FangraphsTeams.ALL.
        qual (str, optional): The qualification type. Defaults to "y".
        rost (int, optional): Roster status, 0 for all players, 1 for active roster. Defaults to 0.
        pos (FangraphsBattingPosTypes, optional): The batting position type to filter by. Defaults to FangraphsBattingPosTypes.ALL.
        stat_split (FangraphsStatSplitTypes, optional): The stat split type. Defaults to FangraphsStatSplitTypes.PLAYER.

    Raises:
        ValueError: If neither date range nor season range is provided.
        ValueError: If only one of start_date or end_date is provided.
        ValueError: If only one of start_season or end_season is provided.
        ValueError: If rost is not 0 or 1.


    Returns:
        pl.DataFrame | pd.DataFrame: The fielding range statistics as a Polars or pandas DataFrame.
    """
    # input validation
    start_date, end_date, start_season, end_season, team = gen_input_val(
        start_date=start_date,
        end_date=end_date,
        start_season=start_season,
        end_season=end_season,
        rost=rost,
        team=team,
        stat_split=stat_split,
    )
    return asyncio.run(
        fangraphs_fielding_range_async(
            start_date=start_date,
            end_date=end_date,
            start_season=start_season,
            end_season=end_season,
            stat_types=stat_types,
            return_pandas=return_pandas,
            league=league,
            qual=qual,
            rost=rost,
            pos=pos,
            team=team,
        )
    )
