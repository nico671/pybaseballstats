from typing import List, Literal, Optional, Union

import polars as pl
import requests
from bs4 import BeautifulSoup

from pybaseballstats.consts.fangraphs_consts import (
    FANGRAPHS_BATTING_LEADERS_URL,
    FANGRAPHS_WAR_LEADERBOARD_URL,
    FangraphsBattingPosTypes,
    FangraphsBattingStatType,
    FangraphsTeams,
)
from pybaseballstats.utils.fangraphs_utils import (
    # fangraphs_fielding_input_val,
    # fangraphs_pitching_range_input_val,
    validate_active_roster_param,
    validate_age_params,
    validate_dates,
    validate_hand_param,
    validate_ind_param,
    validate_min_pa_param,
    validate_pos_param,
    validate_season_type,
    validate_seasons_param,
    validate_team_stat_split_param,
)


def fangraphs_batting_leaderboard(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    start_season: Optional[int] = None,
    end_season: Optional[int] = None,
    pos: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    team: FangraphsTeams = FangraphsTeams.ALL,
    stat_split: Literal["player", "team", "league"] = "player",
    stat_types: Optional[List[FangraphsBattingStatType]] = None,
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
    """Returns a leaderboard of Fangraphs batting statistics. Function is to meant to replicate this leaderboard search: 'https://www.fangraphs.com/leaders/major-league'

    Args:
        start_date (str, optional): When to start the date range. Defaults to None.
        end_date (str, optional): When to end the date range. Defaults to None.
        start_season (int, optional): The starting season year. Defaults to None.
        end_season (int, optional): The ending season year. Defaults to None.
        pos (FangraphsBattingPosTypes, optional): The position filter. Defaults to FangraphsBattingPosTypes.ALL.
        team (FangraphsTeams, optional): The team to filter the data by. Defaults to FangraphsTeams.ALL.
        stat_split (Literal["player", "team", "league"], optional): The statistic split to use. Defaults to "player".
        stat_types (List[FangraphsBattingStatType], optional): The types of statistics to include. Defaults to None.
        active_roster_only (bool, optional): Whether to include only active roster players. Defaults to False.
        season_type (Literal[ "regular", "all_postseason", "world_series", "championship_series", "division_series", "wild_card", ], optional): The type of season to filter by. Defaults to "regular".
        split_seasons (bool, optional): Whether to split the data by seasons. Defaults to False.
        handedness (Literal["L", "R", "S", None], optional): The handedness of the players. Defaults to None.
        min_age (int, optional): The minimum age of players to include. Defaults to 14.
        max_age (int, optional): The maximum age of players to include. Defaults to 56.
        min_pa (Union[int, str], optional): The minimum plate appearances to filter by. Defaults to "y".

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """

    team_param = validate_team_stat_split_param(team, stat_split)
    print(team_param)
    # team_param = quote(team_param)
    roster_param = validate_active_roster_param(active_roster_only)
    season_type_param = validate_season_type(season_type)
    ind_param = validate_ind_param(split_seasons)
    month_param = None

    date_non_null_counts = sum(x is not None for x in [start_date, end_date])
    season_non_null_counts = sum(x is not None for x in [start_season, end_season])

    if date_non_null_counts == 0 and season_non_null_counts == 0:
        raise ValueError("Must provide either date range or season range")
    elif date_non_null_counts == season_non_null_counts:
        raise ValueError("Must provide either date range or season range, not both")
    if date_non_null_counts > season_non_null_counts:
        print("Using date range")
        # using dates

        start_date, end_date = validate_dates(start_date, end_date)
        start_season_str, end_season_str = "", ""
        month_param = "1000"  # Ensure month_param is a string
    else:
        print("Using season range")

        month_param = "0"  # Ensure month_param is a string
        start_date, end_date = "", ""
        start_season_str, end_season_str = validate_seasons_param(
            start_season, end_season
        )

    hand_param = validate_hand_param(handedness)
    age_param = validate_age_params(min_age, max_age)
    pos_param = validate_pos_param(pos)
    min_pa_param = validate_min_pa_param(min_pa)

    request_params = {
        "age": str(age_param),  # Cast to str
        "pos": str(pos_param),  # Cast to str
        "stats": "bat",
        "lg": "all",
        "rost": str(roster_param),  # Cast to str
        "postseason": str(season_type_param),  # Cast to str
        "month": month_param,  # Already a string
        "players": "0",  # Ensure string type
        "season1": start_season_str,
        "season": end_season_str,
        "startDate": start_date,
        "endDate": end_date,
        "ind": str(ind_param),  # Cast to str
        "hand": str(hand_param),  # Cast to str
        "team": str(team_param),  # Cast to str
        "pageitems": "2000000000",  # Ensure string type
        "pagenum": "1",  # Ensure string type
        "qual": str(min_pa_param),  # Cast to str
    }
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


def fangraphs_war_leaderboard(
    pitcher_war_type: Literal[0, 1, 2] = 0,
    team: FangraphsTeams = FangraphsTeams.ALL,
    league: Literal["AL", "NL", ""] = "",
    season: int = 2025,
) -> pl.DataFrame:
    if pitcher_war_type not in [0, 1, 2]:
        raise ValueError(
            "pitcher_war_type must be one of 0 (FIP Based), 1 (RA/9 Based), or 2 (50/50 split)"
        )
    if league not in ["AL", "NL", ""]:
        raise ValueError('league must be one of "AL", "NL", or ""')
    if team not in FangraphsTeams:
        raise ValueError(f"team must be one of {FangraphsTeams.show_options()}")
    if season > 2025 or season < 1871:
        raise ValueError("season must be between 1871 and 2025")
    if team != FangraphsTeams.ALL:
        league = ""
    resp = requests.get(
        FANGRAPHS_WAR_LEADERBOARD_URL.format(
            war_type=pitcher_war_type,
            team_id=team.value,
            league=league,
            season=season,
        )
    )
    soup = BeautifulSoup(resp.content, "html.parser")
    table_wrapper = soup.find("div", class_="leaders-war-data")
    assert table_wrapper is not None, "Could not find table wrapper"
    table = table_wrapper.find("table")
    assert table is not None, "Could not find table"
    tbody = table.find("tbody")
    assert tbody is not None, "Could not find table body"
    row_data = []
    for row in tbody.find_all("tr"):
        curr_row = {}
        for td in row.find_all("td"):
            if "data-stat" in td.attrs:
                curr_row[td.attrs["data-stat"]] = td.text
        row_data.append(curr_row)
    df = pl.DataFrame(row_data)
    df = df.with_columns(
        pl.col("PA").replace("", "0").cast(pl.Int32),
        pl.col(["IP", "Bat WAR", "Pit WAR", "Total WAR"])
        .replace("", "0")
        .cast(pl.Float32),
    )
    return df
