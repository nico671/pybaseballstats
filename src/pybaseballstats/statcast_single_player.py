import asyncio
import io
from datetime import date
from typing import Literal

import polars as pl
import requests

from pybaseballstats.consts.statcast_consts import (
    STATCAST_SINGLE_PLAYER_PITCH_BY_PITCH_URL,
    STATCAST_SINGLE_PLAYER_STATS_URL,
    STATCAST_YEAR_RANGES,
)
from pybaseballstats.utils.statcast_utils import (
    _create_date_ranges,
    _fetch_all_data,
    _load_all_data,
)

__all__ = ["single_player_pitch_by_pitch", "single_player_season_stats"]


async def _async_single_player_pitch_by_pitch(
    player_id: int,
    season: int,
    player_type: Literal["batter", "pitcher"],
    force_collect: bool = False,
    *,
    chunk_size_days: int = 7,
    show_progress: bool = True,
    concurrency: int | None = None,
    verbose: bool = False,
) -> pl.LazyFrame | pl.DataFrame:
    """Asynchronously fetch one player's regular-season pitch details."""
    season_start, configured_season_end = STATCAST_YEAR_RANGES[season]
    season_end = min(configured_season_end, date.today())

    if season_end < season_start:
        raise RuntimeError(
            "No Statcast single-player pitch-by-pitch data found for "
            f"{player_type} {player_id} in {season}."
        )

    if verbose:
        print(
            f"Pulling pitch-by-pitch Statcast data for {player_type} "
            f"{player_id} from {season_start} to {season_end}."
        )
        print("Splitting the season into smaller chunks.")

    player_lookup_param = (
        "batters_lookup%5B%5D" if player_type == "batter" else "pitchers_lookup%5B%5D"
    )
    date_ranges = list(
        _create_date_ranges(
            season_start,
            season_end,
            step=chunk_size_days,
            verbose=verbose,
        )
    )
    urls = [
        STATCAST_SINGLE_PLAYER_PITCH_BY_PITCH_URL.format(
            season=season,
            player_type=player_type,
            start_date=chunk_start,
            end_date=chunk_end,
            player_lookup_param=player_lookup_param,
            player_id=player_id,
        )
        for chunk_start, chunk_end in date_ranges
    ]

    date_range_total_days = (season_end - season_start).days + 1
    try:
        responses = await _fetch_all_data(
            urls,
            date_range_total_days,
            concurrency=concurrency,
            show_progress=show_progress,
        )
    except RuntimeError as e:
        raise RuntimeError(
            "Unable to complete Statcast single-player pitch-by-pitch download "
            f"for {player_type} {player_id} in {season}. {e}"
        ) from e

    non_empty_responses = [response for response in responses if not response.is_empty()]
    if not non_empty_responses:
        raise RuntimeError(
            "No Statcast single-player pitch-by-pitch data found for "
            f"{player_type} {player_id} in {season}."
        )

    if verbose:
        print("Aligning and concatenating chunk data.")
    data_list = _load_all_data(
        non_empty_responses,
        show_progress=show_progress,
    )
    if not data_list:
        raise RuntimeError(
            "Unable to process Statcast single-player pitch-by-pitch data for "
            f"{player_type} {player_id} in {season}."
        )

    df = pl.concat(data_list)
    if verbose:
        print("Data retrieval complete.")

    if force_collect:
        return df.collect()
    return df


def single_player_pitch_by_pitch(
    player_id: int,
    season: int,
    player_type: Literal["batter", "pitcher"],
    force_collect: bool = False,
    *,
    chunk_size_days: int = 7,
    show_progress: bool = True,
    concurrency: int | None = None,
    verbose: bool = False,
) -> pl.LazyFrame | pl.DataFrame:
    """Return regular-season Statcast pitch details for one player.

    The player lookup is sent to Baseball Savant with each date chunk, so the
    remote endpoint returns only pitches thrown by or seen by ``player_id``.

    Args:
        player_id (int): MLBAM player identifier.
        season (int): MLB season year.
        player_type (Literal["batter", "pitcher"]): Player perspective.
        force_collect (bool, optional): Return an eager ``pl.DataFrame`` when True.
        chunk_size_days (int, optional): Days per request chunk.
        show_progress (bool, optional): Show progress while downloading/loading.
        concurrency (int | None, optional): Max concurrent requests override.
        verbose (bool, optional): Print additional runtime logs.

    Raises:
        TypeError: If integer arguments have invalid types.
        ValueError: If an argument is outside its supported range.
        RuntimeError: If downloading fails or no matching pitch data exists.

    Returns:
        pl.LazyFrame | pl.DataFrame: A lazy frame by default, or a collected
        frame when ``force_collect=True``.
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
    if not isinstance(chunk_size_days, int):
        raise TypeError("chunk_size_days must be an integer")
    if chunk_size_days <= 0:
        raise ValueError("chunk_size_days must be a positive integer")
    if concurrency is not None and not isinstance(concurrency, int):
        raise TypeError("concurrency must be an integer or None")
    if concurrency is not None and concurrency <= 0:
        raise ValueError("concurrency must be a positive integer")

    coro = _async_single_player_pitch_by_pitch(
        player_id=player_id,
        season=season,
        player_type=player_type,
        force_collect=force_collect,
        chunk_size_days=chunk_size_days,
        show_progress=show_progress,
        concurrency=concurrency,
        verbose=verbose,
    )

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        import nest_asyncio  # type: ignore[import-untyped]

        nest_asyncio.apply()
        return loop.run_until_complete(coro)


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
        "batters_lookup%5B%5D" if player_type == "batter" else "pitchers_lookup%5B%5D"
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
