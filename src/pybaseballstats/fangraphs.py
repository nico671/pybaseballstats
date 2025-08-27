from typing import List, Literal, Optional, Union

import pandas as pd
import polars as pl
import requests
from consts.fangraphs_consts import FANGRAPHS_BATTING_LEADERS_URL
from utils.fangraphs_utils import (
    pick_season_or_dates,
    validate_active_roster_hof,
    validate_age_params,
    validate_dates,
    validate_hand_param,
    validate_ind_param,
    validate_min_pa_param,
    validate_pos_param,
    validate_season_type,
    validate_seasons,
    validate_team_stat_split,
)

from pybaseballstats.consts.fangraphs_consts import (
    FANGRAPHS_FIELDING_API_URL,
    FANGRAPHS_PITCHING_API_URL,
    FangraphsBattingPosTypes,
    FangraphsBattingStatType,
    FangraphsFieldingStatType,
    FangraphsPitchingStatType,
    FangraphsTeams,
)
from pybaseballstats.utils.fangraphs_utils import (
    fangraphs_fielding_input_val,
    fangraphs_pitching_range_input_val,
)


# #TODO: docstrings for all functions
# TODO: REDO all funcs (batting leaderboard new done now just need to write tests for all 3 and redo the other 2)
def fangraphs_batting_leaderboard(
    start_date: str = None,
    end_date: str = None,
    start_season: int = None,
    end_season: int = None,
    pos: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    team: FangraphsTeams = FangraphsTeams.ALL,
    stat_split: Literal["player", "team", "league"] = "player",
    stat_types: List[FangraphsBattingStatType] = None,
    active_roster_only: bool = False,
    season_type: Literal[
        "regular",
        "all_postseason",
        "world_series",
        "championship_series",
        "division_series",
        "wild_card",
    ] = "regular",
    split_seasons: bool = False,
    handedness: Literal["L", "R", "S", None] = None,
    min_age: int = 14,
    max_age: int = 56,
    min_pa: Union[int, str] = "y",
):
    """_summary_

    Args:
        start_date (str, optional): _description_. Defaults to None.
        end_date (str, optional): _description_. Defaults to None.
        start_season (int, optional): _description_. Defaults to None.
        end_season (int, optional): _description_. Defaults to None.
        pos (FangraphsBattingPosTypes, optional): _description_. Defaults to FangraphsBattingPosTypes.ALL.
        team (FangraphsTeams, optional): _description_. Defaults to FangraphsTeams.ALL.
        stat_split (Literal[&quot;player&quot;, &quot;team&quot;, &quot;league&quot;], optional): _description_. Defaults to "player".
        stat_types (List[FangraphsBattingStatType], optional): _description_. Defaults to None.
        active_roster_only (bool, optional): _description_. Defaults to False.
        season_type (Literal[ &quot;regular&quot;, &quot;all_postseason&quot;, &quot;world_series&quot;, &quot;championship_series&quot;, &quot;division_series&quot;, &quot;wild_card&quot;, ], optional): _description_. Defaults to "regular".
        split_seasons (bool, optional): _description_. Defaults to False.
        handedness (Literal[&quot;L&quot;, &quot;R&quot;, &quot;S&quot;, None], optional): _description_. Defaults to None.
        min_age (int, optional): _description_. Defaults to 14.
        max_age (int, optional): _description_. Defaults to 56.
        min_pa (Union[int, str], optional): _description_. Defaults to "y".

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """

    team_param = validate_team_stat_split(team, stat_split)
    print(team_param)
    # team_param = quote(team_param)
    roster_param = validate_active_roster_hof(active_roster_only)
    season_type_param = validate_season_type(season_type)
    ind_param = validate_ind_param(split_seasons)
    month_param = None
    if pick_season_or_dates(start_date, end_date, start_season, end_season):
        print("Using date range")
        # using dates
        start_date, end_date = validate_dates(start_date, end_date)
        start_season, end_season = "", ""
        month_param = 1000
    else:
        print("using season range")
        month_param = 0
        start_date, end_date = "", ""
        start_season, end_season = validate_seasons(start_season, end_season)
        # using season range

    hand_param = validate_hand_param(handedness)
    age_param = validate_age_params(min_age, max_age)
    # age_param = quote(age_param)
    # print(team_param, age_param)
    pos_param = validate_pos_param(pos)
    min_pa_param = validate_min_pa_param(min_pa)

    request_params = {
        "age": age_param,
        "pos": pos_param,
        "stats": "bat",
        "lg": "all",
        "rost": roster_param,
        "postseason": season_type_param,
        "month": month_param,
        "players": 0,
        "season1": start_season,
        "season": end_season,
        "startDate": start_date,
        "endDate": end_date,
        "ind": ind_param,
        "hand": hand_param,
        "team": team_param,
        "pageitems": 2000000000,
        "pagenum": 1,
        "qual": min_pa_param,
    }
    # from urllib.parse import urlencode

    # final_url = (
    #     f"{FANGRAPHS_BATTING_LEADERS_URL}?{urlencode(request_params, doseq=True)}"
    # )
    # print(final_url)
    resp = requests.get(
        FANGRAPHS_BATTING_LEADERS_URL,
        params=request_params,
    )
    print(resp.url)
    if resp.status_code == 200:
        df = pl.DataFrame(resp.json()["data"])
    else:
        print(resp.status_code, resp.text)
        raise ValueError("Error fetching data from Fangraphs API")
    print(df.columns)
    # filter columns using stat_types

    # else:
    wanted_cols = [
        "PlayerName",
        "TeamName",
        "xMLBAMID",
        "Season",
        "Age",
        "AgeR",
        "Bats",
        "Pos",
        "position",
        "teamid",
    ]
    if stat_types:
        for stat in stat_types:
            for col in stat.value:
                if col in df.columns and col not in wanted_cols:
                    wanted_cols.append(col)
    else:
        for enum_opt in FangraphsBattingStatType:
            for col in enum_opt.value:
                if col in df.columns and col not in wanted_cols:
                    wanted_cols.append(col)
    wanted_cols.remove("Name")
    wanted_cols.remove("Team")
    return df.select(wanted_cols)


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
    split_seasons: bool = False,
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
        split_seasons,
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
        split_seasons=split_seasons,
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
        split_seasons=split_seasons,
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


# TODO: split_seasons
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
