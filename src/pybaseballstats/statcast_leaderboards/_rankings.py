import io
from datetime import datetime
from typing import Literal

import polars as pl
import requests

from pybaseballstats._consts.statcast_leaderboard_consts import (
    PERCENTILE_RANKINGS_LEADERBOARD_URL,
    StatcastLeaderboardsTeams,
)


def percentile_rankings_leaderboard(
    season: int,
    player_type: Literal["batter", "pitcher"] = "batter",
    position: Literal[
        "All", "P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "DH"
    ] = "All",
    team: StatcastLeaderboardsTeams | str = "All",
) -> pl.DataFrame:
    """Return Baseball Savant percentile-ranking leaderboard data for one season.

    Args:
        season (int): Season year from 2015 through the current year.
        player_type (Literal["batter", "pitcher"], optional): Player group to
            return. Defaults to ``"batter"``.
        position (Literal[...], optional): Position filter. Defaults to ``"All"``.
            Position filters are supported only for batters.
        team (StatcastLeaderboardsTeams | str, optional): Team filter. Use a team
            enum or ``"All"``. Defaults to ``"All"``.

    Raises:
        ValueError: If the season, player type, position, or team is invalid, or if
            a position filter is used for pitchers.

    Returns:
        pl.DataFrame: Bulk percentile rankings. Callers can filter ``player_id`` to
            select an individual player.

    Notes:
        Metric columns contain percentile ranks, not raw statistics. Batter and
        pitcher schemas differ, and sparse rows with null percentiles are expected.
        The CSV export may not include every metric shown on an individual player's
        Baseball Savant page.
    """
    if season < 2015 or season > datetime.now().year:
        raise ValueError(f"season must be between 2015 and {datetime.now().year}")
    if player_type not in ["batter", "pitcher"]:
        raise ValueError("player_type must be 'batter' or 'pitcher'")

    position_params = {
        "All": "",
        "P": "1",
        "C": "2",
        "1B": "3",
        "2B": "4",
        "3B": "5",
        "SS": "6",
        "LF": "7",
        "CF": "8",
        "RF": "9",
        "DH": "10",
    }
    if not isinstance(position, str) or position not in position_params:
        raise ValueError("position must be one of the documented position values")
    if player_type == "pitcher" and position != "All":
        raise ValueError("position filters are not supported for pitchers")

    if isinstance(team, StatcastLeaderboardsTeams):
        team_param = str(team.value)
    elif team == "All":
        team_param = ""
    else:
        raise ValueError("team must be a StatcastLeaderboardsTeams enum or 'All'")

    url = PERCENTILE_RANKINGS_LEADERBOARD_URL.format(
        player_type=player_type,
        season=season,
        position=position_params[position],
        team=team_param,
    )
    resp = requests.get(url)
    return pl.read_csv(io.StringIO(resp.text))
