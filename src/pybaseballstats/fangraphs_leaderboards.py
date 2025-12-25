from typing import Literal, Optional

import polars as pl
import requests

from pybaseballstats.consts.fangraphs_consts import (
    FANGRAPHS_BATTING_LEADERBOARD_URL,
    FangraphsBattingPosTypes,
    FangraphsBattingStatType,
    FangraphsLeaderboardTeams,
)
from pybaseballstats.utils.fangraphs_utils import (
    validate_active_roster_param,
    validate_age_params,
    validate_dates,
    validate_hand_param,
    validate_ind_param,
    validate_league_param,
    validate_min_pa_param,
    validate_pos_param,
    validate_season_type,
    validate_seasons_and_dates_together,
    validate_seasons_param,
    validate_team_stat_split_param,
)


def fangraphs_batting_leaderboard(
    start_season: Optional[int] = None,
    end_season: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    stat_types: Optional[list[FangraphsBattingStatType]] = None,
    position: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    season_type: Literal[
        "regular",
        "all_postseason",
        "world_series",
        "championship_series",
        "division_series",
        "wild_card",
    ] = "regular",
    split_seasons: bool = False,
    league: Literal["", "al", "nl"] = "",
    min_pa: str | int = "y",
    batter_handedness: Literal["", "L", "R", "S"] = "",
    team: FangraphsLeaderboardTeams = FangraphsLeaderboardTeams.ALL,
    active_roster_only: bool = False,
    stat_split: Literal["player", "team", "league"] = "player",
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
) -> pl.DataFrame:
    """Returns a DataFrame containing Fangraphs batting leaderboard data based on the provided parameters.

    Args:
        start_season (Optional[int], optional): The first year from which to retrieve data. Defaults to None.
        end_season (Optional[int], optional): The last year from which to retrieve data. Defaults to None.
        start_date (Optional[str], optional): The starting date from which to retrieve data in YYYY-MM-DD format. Defaults to None.
        end_date (Optional[str], optional): The ending date from which to retrieve data in YYYY-MM-DD format. Defaults to None.
        stat_types (Optional[list[FangraphsBattingStatType]], optional): List of stat types to include. Use FangraphsBattingStatType.show_options() to see available enum options. Defaults to None.
        position (FangraphsBattingPosTypes, optional): The player position to filter by. Defaults to FangraphsBattingPosTypes.ALL.
        season_type (Literal[ "regular", "all_postseason", "world_series", "championship_series", "division_series", "wild_card", ], optional): The type of season to filter by. Defaults to "regular".
        split_seasons (bool, optional): Whether to split seasons. Defaults to False.
        league (Literal["", "al", "nl"], optional): The league to filter by. Defaults to "".
        min_pa (str | int, optional): The minimum plate appearances. Defaults to "y".
        batter_handedness (Literal["", "L", "R", "S"], optional): The handedness of the batter. Defaults to "".
        team (FangraphsLeaderboardTeams, optional): The team to filter by. Defaults to FangraphsLeaderboardTeams.ALL.
        active_roster_only (bool, optional): Whether to include only active roster players. Defaults to False.
        stat_split (Literal["player", "team", "league"], optional): The statistic split type. Defaults to "player".
        min_age (Optional[int], optional): The minimum age of players to include. Defaults to None.
        max_age (Optional[int], optional): The maximum age of players to include. Defaults to None.

    Returns:
        pl.DataFrame: _description_
    """
    using_seasons = validate_seasons_and_dates_together(
        start_season, end_season, start_date, end_date
    )
    if using_seasons:
        # using seasons
        start_season_param, end_season_param = validate_seasons_param(
            start_season, end_season
        )
        start_date_param = end_date_param = ""
        month_param = 0  # indicates seasons are being used
    else:
        # using dates
        start_date_param, end_date_param = validate_dates(start_date, end_date)
        start_season_param = end_season_param = ""
        month_param = 1000  # indicates date range is being used
    position_param = validate_pos_param(position)
    season_type_param = validate_season_type(season_type)
    ind_param = validate_ind_param(split_seasons)
    league_param = validate_league_param(league)
    min_pa_param = validate_min_pa_param(min_pa)
    team_param = validate_team_stat_split_param(team, stat_split)

    hand_param = validate_hand_param(batter_handedness)
    if not min_age:
        min_age = 14
    if not max_age:
        max_age = 56
    validate_age_params(min_age, max_age)
    active_roster_only_param = validate_active_roster_param(active_roster_only)
    url = FANGRAPHS_BATTING_LEADERBOARD_URL.format(
        pos_param=position_param,
        league_param=league_param,
        min_pa_param=min_pa_param,
        start_season_param=start_season_param,
        end_season_param=end_season_param,
        start_date_param=start_date_param,
        end_date_param=end_date_param,
        month_param=month_param,
        hand_param=hand_param,
        team_param=team_param,
        active_roster_param=active_roster_only_param,
        split_seasons_param=ind_param,
        postseason_param=season_type_param,
        custom_players_names_param_addedlater="",  # not implemented yet
    )

    response = requests.get(url)
    data = response.json()
    df = pl.DataFrame(data["data"])
    df = df.drop(["PlayerNameRoute", "TeamNameAbb", "PlayerName", "TeamName"])
    start_cols = [
        "Name",
        "Team",
        "position",
        "Season",
        "Bats",
        "Age",
        "xMLBAMID",
        "teamid",
        "playerid",
        "SeasonMin",
        "SeasonMax",
        "AgeR",
    ]
    if start_season_param == "":
        start_cols.remove("SeasonMin")
        start_cols.remove("SeasonMax")
    other_cols = [col for col in df.columns if col not in start_cols]

    df = df.select(start_cols + other_cols)
    df = df.rename({"teamid": "fg_team_id", "playerid": "fg_player_id"})
    df = df.with_columns(
        pl.col("Name").str.extract(r"<a[^>]*>([^<]+)</a>", 1).alias("Name"),
        pl.col("Team").str.extract(r"<a[^>]*>([^<]+)</a>", 1).alias("Team"),
    )
    # handle stat_types filtering

    wanted_stats = {}
    if not stat_types or len(stat_types) == 0:
        for stat_type in FangraphsBattingStatType:
            for stat in stat_type.value:
                if stat in start_cols:
                    continue
                wanted_stats[stat] = True
    else:
        for stat_type in stat_types:
            for stat in stat_type.value:
                if stat in start_cols:
                    continue
                wanted_stats[stat] = True
    wanted_stats_ordered = list(dict.fromkeys(wanted_stats))  # preserve order
    wanted_stats_ordered = start_cols + wanted_stats_ordered
    df = df.select([pl.col(col) for col in wanted_stats_ordered if col in df.columns])

    # filter by min_age and max_age if provided
    if min_age is not None:
        df = df.filter(pl.col("Age") >= min_age)
    if max_age is not None:
        df = df.filter(pl.col("Age") <= max_age)
    return df
