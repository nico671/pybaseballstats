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
    *,
    verbose: bool = False,
) -> pl.DataFrame:
    """Return Baseball Savant Statcast Search stats for one player season.

    Results are grouped by player name and use the unfiltered Baseball Savant
    Statcast Search pitch-result selection.

    Args:
        player_id (int): MLBAM player identifier.
        season (int): MLB season year.
        player_type (Literal["batter", "pitcher"]): Statcast Search player
            perspective. This controls whether ``player_id`` is sent as a
            batter or pitcher lookup; it is not inferred from the player.
        verbose (bool, optional): Print additional runtime logs.

    Raises:
        TypeError: If ``player_id`` or ``season`` is not an integer.
        ValueError: If ``season`` is not available.
        ValueError: If ``player_type`` is not ``"batter"`` or ``"pitcher"``.
        RuntimeError: If Baseball Savant returns no CSV data for the lookup.
        RuntimeError: If the Baseball Savant CSV cannot be parsed.

    Returns:
        pl.DataFrame: Baseball Savant grouped Statcast Search stats for the
        requested player season.
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

    if verbose:
        print(f"Pulling Statcast data for player {player_id} in {season}.")

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
    try:
        df = pl.read_csv(io.StringIO(resp.text))
    except pl.exceptions.NoDataError as e:
        raise RuntimeError(
            "No Statcast single-player data found for "
            f"{player_type} {player_id} in {season}."
        ) from e
    except pl.exceptions.PolarsError as e:
        raise RuntimeError(
            "Unable to parse Statcast single-player CSV for "
            f"{player_type} {player_id} in {season}."
        ) from e

    if verbose:
        print("Data retrieval complete.")

    return df
