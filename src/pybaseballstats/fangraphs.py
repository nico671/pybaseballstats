from typing import List, Literal, Optional, Union

import pandas as pd
import polars as pl
import requests

from pybaseballstats.utils.fangraphs_consts import FangraphsFieldingStatType
from pybaseballstats.utils.fangraphs_utils import (
    FANGRAPHS_BATTING_API_URL,
    FANGRAPHS_FIELDING_API_URL,
    FANGRAPHS_PITCHING_API_URL,
    FangraphsBattingPosTypes,
    FangraphsBattingStatType,
    FangraphsPitchingStatType,
    FangraphsTeams,
    fangraphs_batting_input_val,
    fangraphs_fielding_input_val,
    fangraphs_pitching_range_input_val,
)

# TODO: figure out how to handle team stats and league stats
# TODO: usage docs


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
    start_date: Union[str, None] = None,
    end_date: Union[str, None] = None,
    start_year: Union[int, None] = None,
    end_year: Union[int, None] = None,
    min_ip: Union[str, int] = "y",
    stat_types: List[FangraphsPitchingStatType] = None,
    active_roster_only: bool = False,
    team: FangraphsTeams = FangraphsTeams.ALL,
    league: Literal["nl", "al", ""] = "",
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    pitching_hand: Literal["R", "L", "S", ""] = "",
    starter_reliever: Literal["sta", "rel", "pit"] = "pit",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    (
        start_date,
        end_date,
        start_year,
        end_year,
        min_ip,
        stat_types,
        active_roster_only,
        team,
        league,
        min_age,
        max_age,
        pitching_hand,
        starter_reliever,
        stat_types,
    ) = fangraphs_pitching_range_input_val(
        start_date=start_date,
        end_date=end_date,
        start_year=start_year,
        end_year=end_year,
        min_ip=min_ip,
        stat_types=stat_types,
        active_roster_only=active_roster_only,
        team=team,
        league=league,
        min_age=min_age,
        max_age=max_age,
        pitching_hand=pitching_hand,
        starter_reliever=starter_reliever,
    )

    url = FANGRAPHS_PITCHING_API_URL.format(
        start_date=start_date,
        end_date=end_date,
        start_year=start_year,
        end_year=end_year,
        min_ip=min_ip,
        team=team,
        league=league,
        pitching_hand=pitching_hand,
        starter_reliever=starter_reliever,
        month=1000 if start_date else 0,
        active_roster_only=active_roster_only,
    )
    resp = requests.get(url)
    data = resp.json()["data"]
    df = pl.DataFrame(data, infer_schema_length=None)
    df = df.drop(["PlayerNameRoute", "PlayerName"])
    stat_types.extend(
        [
            "Throws",
            "xMLBAMID",
            "season",
            "Season",
            "SeasonMin",
            "SeasonMax",
            "Age",
            "AgeR",
        ]
    )
    df = df.select([col for col in df.columns if col in stat_types])
    df = df.with_columns(
        [
            pl.col("Name").str.extract(r">(.*?)<\/a>").alias("Name"),
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


def fangraphs_fielding_range(
    start_year: Union[int, None] = None,
    end_year: Union[int, None] = None,
    min_inn: Union[str, int] = "y",
    stat_types: List[FangraphsFieldingStatType] = None,
    active_roster_only: bool = False,
    team: FangraphsTeams = FangraphsTeams.ALL,
    league: Literal["nl", "al", ""] = "",
    fielding_position: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    (
        start_year,
        end_year,
        min_inn,
        fielding_position,
        active_roster_only,
        team,
        league,
        stat_types,
    ) = fangraphs_fielding_input_val(
        start_year=start_year,
        end_year=end_year,
        min_inn=min_inn,
        stat_types=stat_types,
        active_roster_only=active_roster_only,
        team=team,
        league=league,
        fielding_position=fielding_position,
    )

    url = FANGRAPHS_FIELDING_API_URL.format(
        start_year=start_year if start_year else "",
        end_year=end_year if end_year else "",
        min_inn=min_inn,
        fielding_position=fielding_position.value,
        team=team.value if isinstance(team, FangraphsTeams) else team,
        league=league,
        active_roster_only=active_roster_only,
    )

    resp = requests.get(url)
    data = resp.json()["data"]
    df = pl.DataFrame(data, infer_schema_length=None)
    df = df.drop(["PlayerNameRoute", "Name", "Team"])
    for extra in [
        "Q",
        "Season",
        "season",
        "SeasonMax",
        "SeasonMin",
        "playerid",
        "xMLBAMID",
        "TeamNameAbb",
        "PlayerName",
    ]:
        stat_types.insert(0, extra)
    df = df.select([col for col in stat_types if col in df.columns])
    return df if not return_pandas else df.to_pandas()
