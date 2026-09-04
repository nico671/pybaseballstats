import io
from datetime import datetime
from typing import Literal

import polars as pl
import requests

from pybaseballstats.consts.statcast_leaderboard_consts import (
    ARM_STRENGTH_LEADERBOARD_URL,
    ARM_STRENGTH_POS_INPUT_MAP,
    StatcastLeaderboardsTeams,
)


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
