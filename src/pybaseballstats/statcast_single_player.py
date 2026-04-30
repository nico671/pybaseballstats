import io
from typing import Literal

import polars as pl
import requests

from pybaseballstats.consts.statcast_consts import (
    STATCAST_SINGLE_PLAYER_STATS_URL,
    STATCAST_YEAR_RANGES,
)

__all__ = ["single_player_season_stats"]


def single_player_season_stats(
    player_id: int,
    season: int,
    player_type: Literal["batter", "pitcher"],
) -> pl.DataFrame:
    """Return Baseball Savant Statcast Search stats for one player season.

    Args:
        player_id (int): MLBAM player identifier.
        season (int): MLB season year.
        player_type (Literal["batter", "pitcher"]): Player perspective.

    Raises:
        TypeError: If ``player_id`` or ``season`` is not an integer.
        ValueError: If ``season`` is not available.
        ValueError: If ``player_type`` is not ``"batter"`` or ``"pitcher"``.

    Returns:
        pl.DataFrame: Baseball Savant grouped Statcast Search stats for the
        requested player, or an empty DataFrame when no rows are returned.
    """
    if not isinstance(player_id, int):
        raise TypeError("player_id must be an integer")
    if not isinstance(season, int):
        raise TypeError("season must be an integer")
    if season not in STATCAST_YEAR_RANGES:
        raise ValueError(
            f"season must be one of: {', '.join(str(year) for year in STATCAST_YEAR_RANGES)}"
        )
    if player_type not in ["batter", "pitcher"]:
        raise ValueError("player_type must be either 'batter' or 'pitcher'")

    player_lookup_param = (
        "batters_lookup%5B%5D"
        if player_type == "batter"
        else "pitchers_lookup%5B%5D"
    )
    url = STATCAST_SINGLE_PLAYER_STATS_URL.format(
        season=season,
        player_type=player_type,
        player_lookup_param=player_lookup_param,
        player_id=player_id,
    )
    resp = requests.get(url)
    if not resp.text.strip("\ufeff \r\n\t"):
        return pl.DataFrame()
    df = pl.read_csv(io.StringIO(resp.text))
    if df.is_empty():
        return pl.DataFrame()
    return df
