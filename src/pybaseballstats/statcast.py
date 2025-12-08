import asyncio

import polars as pl

from typing import Optional

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
) -> pl.LazyFrame | pl.DataFrame | None:
    """Internal async implementation."""
    start_dt, end_dt = _handle_dates(start_date, end_date)
    print(f"Pulling data for date range: {start_dt} to {end_dt}.")
    print("Splitting date range into smaller chunks.")
    date_ranges = list(_create_date_ranges(start_dt, end_dt, step=3))
    assert len(date_ranges) > 0, "No date ranges generated. Check your input dates."

    urls = []
    for start_dt, end_dt in date_ranges:
        urls.append(
            STATCAST_DATE_RANGE_URL.format(
                start_date=start_dt,
                end_date=end_dt,
                team=team.value if team else "",
            )
        )

    date_range_total_days = (end_dt - start_dt).days
    responses = await _fetch_all_data(urls, date_range_total_days)
    data_list = _load_all_data(responses)

    if not data_list:
        print("No data was successfully retrieved.")
        return None

    print("Concatenating data.")
    df = pl.concat(data_list)
    print("Data retrieval complete.")

    if force_collect:
        return df.collect()
    return df


def pitch_by_pitch_data(
    start_date: str,
    end_date: str,
    team: Optional[StatcastTeams] = None,
    force_collect: bool = False,
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

    Example:
        >>> data = pitch_by_pitch_data("2024-04-01", "2024-04-03")
        >>> collected_data = pitch_by_pitch_data("2024-04-01", "2024-04-03", force_collect=True)
    """
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided")

    if not isinstance(team, StatcastTeams) and team is not None:
        raise ValueError("Team must be a valid StatcastTeams enum value. See StatcastTeams class for valid values.")

    try:
        loop = asyncio.get_running_loop()  # noqa: F841
    except RuntimeError:
        # No event loop running - normal case for CLI/scripts
        return asyncio.run(
            _async_pitch_by_pitch_data(
                start_date=start_date,
                end_date=end_date,
                team=team,
                force_collect=force_collect,
            )
        )
    else:
        # Event loop already running - Jupyter notebooks, existing async context
        import nest_asyncio # type: ignore

        nest_asyncio.apply()
        return asyncio.run(
            _async_pitch_by_pitch_data(
                start_date=start_date,
                end_date=end_date,
                team=team,
                force_collect=force_collect,
            )
        )
