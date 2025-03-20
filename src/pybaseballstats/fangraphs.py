import asyncio
from typing import List, Literal, Optional, Union

import nest_asyncio
import pandas as pd
import polars as pl
import requests

from pybaseballstats.utils.fangraphs_utils import (
    FANGRAPHS_BATTING_API_URL,
    FangraphsBattingPosTypes,
    FangraphsBattingStatType,
    FangraphsLeagueTypes,
    FangraphsPitchingStatType,
    FangraphsStatSplitTypes,
    FangraphsTeams,
    fangraphs_batting_input_val,
    fangraphs_fielding_range_async,
    fangraphs_pitching_range_async,
    gen_input_val,
)

nest_asyncio.apply()


def fangraphs_batting_range(
    start_date: Union[str, None] = None,
    end_date: Union[str, None] = None,
    start_year: Union[int, None] = None,
    end_year: Union[int, None] = None,
    min_pa: Union[str, int] = "y",
    stat_types: List[FangraphsBattingStatType] = None,
    fielding_position: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    active_roster_only: bool = False,
    team: FangraphsTeams = FangraphsTeams.ALL,
    league: Literal["nl", "al", ""] = "",
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    batting_hand: Literal["R", "L", "S", ""] = "",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    (
        start_date,
        end_date,
        start_year,
        end_year,
        min_pa,
        fielding_position,
        active_roster_only,
        team,
        league,
        min_age,
        max_age,
        batting_hand,
        stat_types,
    ) = fangraphs_batting_input_val(
        start_date=start_date,
        end_date=end_date,
        start_season=start_year,
        end_season=end_year,
        min_pa=min_pa,
        stat_types=stat_types,
        fielding_position=fielding_position,
        active_roster_only=active_roster_only,
        team=team,
        league=league,
        min_age=min_age,
        max_age=max_age,
        batting_hand=batting_hand,
    )
    start_date = start_date.strftime("%Y-%m-%d") if start_date else ""
    end_date = end_date.strftime("%Y-%m-%d") if end_date else ""
    if start_year and end_year:
        month = 0
    else:
        month = 1000
    url = FANGRAPHS_BATTING_API_URL.format(
        pos=fielding_position,
        league=league,
        min_pa=min_pa,
        start_date=start_date if start_date else "",
        end_date=end_date if end_date else "",
        start_season=start_year if start_year else "",
        end_season=end_year if end_year else "",
        batting_hand=batting_hand,
        team=team.value if isinstance(team, FangraphsTeams) else team,
        active_roster_only=active_roster_only,
        month=month,
    )
    data = requests.get(url).json()
    df = pl.DataFrame(data["data"], infer_schema_length=None)
    df = df.drop(["PlayerNameRoute"])
    stat_types.extend(
        [
            "Bats",
            "xMLBAMID",
            "Name",
            "Team",
            "Season",
            "Age",
            "AgeR",
            "SeasonMin",
            "SeasonMax",
        ]
    )
    df = df.select([col for col in df.columns if col in stat_types])
    df = df.with_columns(
        [
            pl.col("Name").str.extract(r">(.*?)<\/a>").alias("Name"),
            pl.col("Name").str.extract(r"position=([A-Z]+)").alias("Pos"),
            pl.col("Name")
            .str.extract(r"playerid=(\d+)")
            .cast(pl.Int32)
            .alias("fg_player_id"),
            pl.col("Team").str.extract(r">(.*?)<\/a>").alias("Team"),
        ]
    )
    df = df.filter(pl.col("Age") >= min_age) if min_age else df
    df = df.filter(pl.col("Age") <= max_age) if max_age else df
    return df if not return_pandas else df.to_pandas()


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
