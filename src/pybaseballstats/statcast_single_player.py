import asyncio
from typing import Literal

import polars as pl

from pybaseballstats.consts.statcast_consts import (
    STATCAST_SINGLE_PLAYER_STATS_URL,
    STATCAST_YEAR_RANGES,
)
from pybaseballstats.utils.statcast_utils import (
    _fetch_all_data, 
    _load_all_data,
)

__all__ = ["single_player_season_stats"]


async def _async_single_player_season_stats(
    player_id: int,
    season: int,
    player_type: Literal["batter", "pitcher"],
    *,
    show_progress: bool = True,
    concurrency: int | None = None,
    verbose: bool = False,
) -> pl.DataFrame:
    """Asynchronously fetch Baseball Savant stats for one player season.

    Args:
        player_id (int): MLBAM player identifier.
        season (int): MLB season year.
        player_type (Literal["batter", "pitcher"]): Player perspective.
        show_progress (bool, optional): Show progress while downloading/loading.
        concurrency (int | None, optional): Max concurrent requests override.
        verbose (bool, optional): Print additional runtime logs.

    Returns:
        pl.DataFrame: Baseball Savant grouped Statcast Search stats for the
        requested player, or an empty DataFrame when no rows are returned.
    """
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

    try:
        responses = await _fetch_all_data(
            [url],
            1,
            concurrency=concurrency,
            show_progress=show_progress,
        )
    except RuntimeError as e:
        raise RuntimeError(
            "Unable to complete Statcast single-player download for the requested "
            f"player {player_id} in {season}. {e}"
        ) from e
    data_list = _load_all_data(responses, show_progress=show_progress)

    if not data_list:
        print("No data was successfully retrieved.")
        return pl.DataFrame()

    if verbose:
        print("Concatenating data.")
    df = pl.concat(data_list)
    if verbose:
        print("Data retrieval complete.")

    return df.collect()


def single_player_season_stats(
    player_id: int,
    season: int,
    player_type: Literal["batter", "pitcher"],
    *,
    show_progress: bool = True,
    concurrency: int | None = None,
    verbose: bool = False,
) -> pl.DataFrame:
    """Return Baseball Savant Statcast Search stats for one player season.

    This function manages async downloading internally and exposes a synchronous
    interface for scripts and notebooks.

    Args:
        player_id (int): MLBAM player identifier.
        season (int): MLB season year.
        player_type (Literal["batter", "pitcher"]): Player perspective.
        show_progress (bool, optional): Show progress while downloading/loading.
        concurrency (int | None, optional): Max concurrent requests override.
        verbose (bool, optional): Print additional runtime logs.

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

    coro = _async_single_player_season_stats(
        player_id=player_id,
        season=season,
        player_type=player_type,
        show_progress=show_progress,
        concurrency=concurrency,
        verbose=verbose,
    )

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running - normal case for CLI/scripts
        return asyncio.run(coro)
    else:
        # Event loop already running - Jupyter notebooks, existing async context
        import nest_asyncio  # type: ignore

        nest_asyncio.apply()
        return loop.run_until_complete(coro)
