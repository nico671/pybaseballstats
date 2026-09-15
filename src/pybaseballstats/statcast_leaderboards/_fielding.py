import io
import math
from datetime import datetime
from typing import Literal

import polars as pl
import requests

from pybaseballstats._consts.statcast_leaderboard_consts import (
    ARM_STRENGTH_LEADERBOARD_URL,
    ARM_STRENGTH_POS_INPUT_MAP,
    FIELDING_RUN_VALUE_LEADERBOARD_URL,
    StatcastLeaderboardsTeams,
)


def fielding_run_value_leaderboard(
    start_season: int,
    end_season: int,
    stat_type: Literal[
        "Fielders", "Fielders - Team", "Batters", "Batters - Team", "Pitchers"
    ] = "Fielders",
    group_by: list[Literal["season", "month", "position", "game_type"]] | None = None,
    min_innings: int | float | str = "q",
    min_results: int | float = 1,
    game_type: Literal["Any", "Regular", "Playoff"] = "Regular",
    teams: list[StatcastLeaderboardsTeams] | None = None,
    position: Literal[
        "All",
        "Infield",
        "Outfield",
        "Corner Infield",
        "Middle Infield",
        "Corner Outfield",
        "Up The Middle",
        "C",
        "1B",
        "2B",
        "3B",
        "SS",
        "LF",
        "CF",
        "RF",
    ] = "All",
    start_date: str | None = None,
    end_date: str | None = None,
) -> pl.DataFrame:
    """Return Baseball Savant fielding run value leaderboard data.

    Args:
        start_season (int): First season to include. Must be 2015 or later.
        end_season (int): Last season to include. Must not precede ``start_season``.
        stat_type (Literal[...], optional): Type of leaderboard rows. Options are
            ``"Fielders"``, ``"Fielders - Team"``, ``"Batters"``,
            ``"Batters - Team"``, and ``"Pitchers"``.
        group_by (list[Literal[...]] | None, optional): Split dimensions. Options
            are ``"season"``, ``"month"``, ``"position"``, and ``"game_type"``.
            ``None`` returns no split.
        min_innings (int | float | str, optional): Minimum total innings, or ``"q"``
            for Baseball Savant's qualifying threshold. Must be positive when
            numeric.
        min_results (int | float, optional): Minimum innings within each split.
            Must be positive.
        game_type (Literal["Any", "Regular", "Playoff"], optional): Game-type filter.
        teams (list[StatcastLeaderboardsTeams] | None, optional): Teams to include.
            ``None`` includes all teams.
        position (Literal[...], optional): Position filter. Defaults to ``"All"``.
        start_date (str | None, optional): Optional start date in ``YYYY-MM-DD``
            format. The earliest available date is ``2018-03-29``.
        end_date (str | None, optional): Optional end date in ``YYYY-MM-DD`` format.

    Raises:
        ValueError: If a season, filter, team, threshold, or date is invalid.

    Returns:
        pl.DataFrame: Fielding run value leaderboard data. Player rows use
            ``player_id`` and ``player_name``; team rows use ``team_id`` and
            ``team_name``.
    """
    current_year = datetime.now().year
    if (
        not isinstance(start_season, int)
        or isinstance(start_season, bool)
        or not 2015 <= start_season <= current_year
    ):
        raise ValueError(f"start_season must be between 2015 and {current_year}")
    if (
        not isinstance(end_season, int)
        or isinstance(end_season, bool)
        or not start_season <= end_season <= current_year
    ):
        raise ValueError(f"end_season must be between start_season and {current_year}")

    stat_type_codes = {
        "Fielders": "fielder",
        "Fielders - Team": "fielding-team",
        "Batters": "batter",
        "Batters - Team": "batting-team",
        "Pitchers": "pitcher",
    }
    if stat_type not in stat_type_codes:
        raise ValueError(
            "stat_type must be 'Fielders', 'Fielders - Team', 'Batters', "
            "'Batters - Team', or 'Pitchers'"
        )

    group_by_codes = {
        "season": "year",
        "month": "api_game_date_month_text",
        "position": "position",
        "game_type": "game_type",
    }
    if group_by is None:
        group_by_param = ""
    elif (
        not isinstance(group_by, list)
        or not all(grouping in group_by_codes for grouping in group_by)
        or len(set(group_by)) != len(group_by)
    ):
        raise ValueError(
            "group_by must be a list of unique values from "
            "'season', 'month', 'position', or 'game_type', or None"
        )
    else:
        group_by_param = "|".join(group_by_codes[grouping] for grouping in group_by)

    if isinstance(min_innings, str) and min_innings == "q":
        min_innings_param = min_innings
    elif (
        isinstance(min_innings, (int, float))
        and not isinstance(min_innings, bool)
        and math.isfinite(min_innings)
        and min_innings > 0
    ):
        min_innings_param = str(min_innings)
    else:
        raise ValueError("min_innings must be a positive number or 'q'")

    if (
        not isinstance(min_results, (int, float))
        or isinstance(min_results, bool)
        or not math.isfinite(min_results)
        or min_results <= 0
    ):
        raise ValueError("min_results must be a positive number")

    if game_type not in ["Any", "Regular", "Playoff"]:
        raise ValueError("game_type must be 'Any', 'Regular', or 'Playoff'")

    if teams is None:
        teams_param = ""
    elif not isinstance(teams, list) or not all(
        isinstance(team, StatcastLeaderboardsTeams) for team in teams
    ):
        raise ValueError(
            "teams must be a list of StatcastLeaderboardsTeams enums or None"
        )
    else:
        teams_param = "|".join(str(team.value) for team in teams)

    position_codes = {
        "All": "0",
        "Infield": "11",
        "Outfield": "12",
        "Corner Infield": "111",
        "Middle Infield": "112",
        "Corner Outfield": "121",
        "Up The Middle": "13",
        "C": "2",
        "1B": "3",
        "2B": "4",
        "3B": "5",
        "SS": "6",
        "LF": "7",
        "CF": "8",
        "RF": "9",
    }
    if position not in position_codes:
        raise ValueError(
            "position must be one of the supported Baseball Savant positions"
        )

    earliest_date = datetime(2018, 3, 29).date()
    latest_date = datetime.now().date()
    date_params = {}
    for name, value in [("start_date", start_date), ("end_date", end_date)]:
        if value is None:
            date_params[name] = ""
            continue
        try:
            date_value = datetime.strptime(value, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            raise ValueError(f"{name} must be in YYYY-MM-DD format")
        if date_value < earliest_date:
            raise ValueError(f"{name} must be on or after {earliest_date}")
        if date_value > latest_date:
            raise ValueError(f"{name} cannot be in the future")
        date_params[name] = value

    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValueError("end_date must be on or after start_date")

    url = FIELDING_RUN_VALUE_LEADERBOARD_URL.format(
        start_date=date_params["start_date"],
        end_date=date_params["end_date"],
        game_type=game_type,
        group_by=group_by_param,
        start_season=start_season,
        end_season=end_season,
        teams=teams_param,
        stat_type=stat_type_codes[stat_type],
        position=position_codes[position],
        min_innings=min_innings_param,
        min_results=min_results,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    if stat_type in ["Fielders", "Batters", "Pitchers"]:
        return df.rename({"id": "player_id", "name": "player_name"})
    return df.rename({"id": "team_id", "name": "team_name"})


def arm_strength_leaderboard(
    stat_type: Literal["player", "team"] = "player",
    year: int | str = 2025,  # All for all years (9999) is passed in
    min_throws: int = 50,
    pos: Literal[
        "All", "2b_ss_3b", "outfield", "1b", "2b", "3b", "ss", "lf", "cf", "rf"
    ] = "All",
    team: StatcastLeaderboardsTeams | None = None,
) -> pl.DataFrame:
    """Return Baseball Savant arm-strength leaderboard data.

    Args:
        stat_type (Literal["player", "team"], optional): Aggregate by player or team.
        year (int | str, optional): Season year, or ``"All"`` for all available years.
        min_throws (int, optional): Minimum throw threshold.
        pos (Literal[...], optional): Position group filter.
        team (StatcastLeaderboardsTeams | None, optional): Optional team filter.

    Raises:
        ValueError: If ``stat_type`` is invalid.
        ValueError: If ``year`` is invalid.
        ValueError: If ``min_throws`` is less than 1.
        ValueError: If ``pos`` is invalid.
        ValueError: If ``team`` is not ``None`` or ``StatcastLeaderboardsTeams``.

    Returns:
        pl.DataFrame: Arm-strength leaderboard data.
    """
    if stat_type not in ["player", "team"]:
        raise ValueError("stat_type must be either 'player' or 'team'")
    if isinstance(year, int) and (year < 2020 or year > datetime.now().year):
        raise ValueError(f"year must be between 2020 and {datetime.now().year}")

    if isinstance(year, str) and year != "All":
        raise ValueError(
            "year must be an integer between 2020 and the current year, or 'All'"
        )
    if isinstance(year, str) and year == "All":
        year = 9999

    if min_throws < 1:
        raise ValueError("min_throws must be at least 1")
    if pos not in ARM_STRENGTH_POS_INPUT_MAP.keys():
        raise ValueError(
            f"pos must be one of {list(ARM_STRENGTH_POS_INPUT_MAP.keys())}"
        )
    if team is not None and not isinstance(team, StatcastLeaderboardsTeams):
        raise ValueError(
            "team must be an instance of StatcastLeaderboardsTeams or None"
        )
    team_value = team.value if team is not None else ""
    url = ARM_STRENGTH_LEADERBOARD_URL.format(
        stat_type=stat_type,
        year=year,
        min_throws=min_throws,
        pos=ARM_STRENGTH_POS_INPUT_MAP[pos],
        team=team_value,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text), truncate_ragged_lines=True)
    if stat_type == "player":
        df = df.drop(["team_name"])
    if stat_type == "team":
        df = df.drop(
            [
                "fielder_name",
                "player_id",
                "primary_position",
                "primary_position_name",
                "total_throws",
                "total_throws_inf",
                "total_throws_of",
                "arm_inf",
                "arm_of",
            ]
        )
    return df
