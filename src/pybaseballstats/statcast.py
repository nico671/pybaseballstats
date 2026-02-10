import asyncio
from typing import Optional

import polars as pl

from pybaseballstats.consts.statcast_consts import (
    STATCAST_DATE_RANGE_URL,
    StatcastTeams,
)
from pybaseballstats.utils.statcast_utils import (
    _create_date_ranges,
    _fetch_all_data,
    _handle_dates,
    _load_all_data,
)

__all__ = ["pitch_by_pitch_data"]


async def _async_pitch_by_pitch_data(
    start_date: str,
    end_date: str,
    team: Optional[StatcastTeams] = None,
    force_collect: bool = False,
    *,
    chunk_size_days: int = 3,
    show_progress: bool = True,
    concurrency: int | None = None,
    verbose: bool = False,
) -> pl.LazyFrame | pl.DataFrame | None:
    """Internal async implementation."""
    start_dt, end_dt = _handle_dates(start_date, end_date)
    if verbose:
        print(f"Pulling data for date range: {start_dt} to {end_dt}.")
        print("Splitting date range into smaller chunks.")

    if chunk_size_days <= 0:
        raise ValueError("chunk_size_days must be a positive integer")

    date_ranges = list(_create_date_ranges(start_dt, end_dt, step=chunk_size_days))
    assert len(date_ranges) > 0, "No date ranges generated. Check your input dates."

    urls = []
    for chunk_start_dt, chunk_end_dt in date_ranges:
        urls.append(
            STATCAST_DATE_RANGE_URL.format(
                start_date=chunk_start_dt,
                end_date=chunk_end_dt,
                team=team.value if team else "",
            )
        )

    # inclusive days in the requested range (used only for concurrency heuristics)
    date_range_total_days = (end_dt - start_dt).days + 1
    responses = await _fetch_all_data(
        urls,
        date_range_total_days,
        concurrency=concurrency,
        show_progress=show_progress,
    )
    data_list = _load_all_data(responses, show_progress=show_progress)

    if not data_list:
        if verbose:
            print("No data was successfully retrieved.")
        return None

    if verbose:
        print("Concatenating data.")
    df = pl.concat(data_list)
    if verbose:
        print("Data retrieval complete.")

    if force_collect:
        return df.collect()
    return df


def pitch_by_pitch_data(
    start_date: str,
    end_date: str,
    team: Optional[StatcastTeams] = None,
    force_collect: bool = False,
    *,
    chunk_size_days: int = 3,
    show_progress: bool = True,
    concurrency: int | None = None,
    verbose: bool = False,
) -> pl.LazyFrame | pl.DataFrame | None:
    """Returns pitch-by-pitch data from Statcast for a given date range.

    This function handles async operations internally for performance,
    but provides a simple synchronous interface for end users.

    Args:
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.
        team (StatcastTeams, optional): MLB team abbreviation for filtering. Defaults to None (all teams).
        force_collect (bool, optional): Whether to force collection of the data,
            meaning conversion to a Polars DataFrame rather than the default
            Polars LazyFrame. Defaults to False.

    Returns:
        pl.LazyFrame | pl.DataFrame | None: The pitch-by-pitch data as a Polars
            LazyFrame if force_collect is False, a Polars DataFrame if
            force_collect is True, or None if no data is found.

    Raises:
        ValueError: If start_date or end_date is invalid or if start_date > end_date.
        ValueError: If team is provided but not found in TEAM_ABBR.
    """
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided")

    if not isinstance(team, StatcastTeams) and team is not None:
        raise ValueError(
            "Team must be a valid StatcastTeams enum value. See StatcastTeams class for valid values."
        )

    coro = _async_pitch_by_pitch_data(
        start_date=start_date,
        end_date=end_date,
        team=team,
        force_collect=force_collect,
        chunk_size_days=chunk_size_days,
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
