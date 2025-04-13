import asyncio

import nest_asyncio
import pandas as pd
import polars as pl

from .utils.statcast_utils import (
    _statcast_date_range_helper,
    _statcast_single_batter_range_helper,
    _statcast_single_pitcher_range_helper,
)

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()


# TODO: usage docs
def statcast_date_range_pitch_by_pitch(
    start_dt: str,
    end_dt: str,
    team: str = None,
    extra_stats: bool = False,
    return_pandas: bool = False,
) -> pl.LazyFrame | pd.DataFrame:
    """Pulls pitch by pitch statcast data over a date range.

    Args:
        start_dt: the start date in 'YYYY-MM-DD' format
        end_dt: the end date in 'YYYY-MM-DD' format
        team: the team abbreviation you wish to restrict data to (e.g. 'WSH'). If None, data for all teams will be returned.
        extra_stats: whether to include extra stats
        return_pandas: whether to return a pandas DataFrame (default is False, returning a Polars LazyFrame)

    Returns:
        pl.LazyFrame | pd.Dataframe: A DataFrame of statcast data for the date range. Warning: this may be a large amount of data, depending on the date range and team.
        If return_pandas is True, a pandas DataFrame will be returned instead of a Polars LazyFrame which may cause memory / performance issues.
    """

    async def async_statcast():
        try:
            return await _statcast_date_range_helper(
                start_dt, end_dt, team, extra_stats, return_pandas
            )
        except Exception as e:
            print(f"Error fetching statcast data: {str(e)}")
            # Return empty dataframe
            return pl.LazyFrame() if not return_pandas else pd.DataFrame()

    try:
        return asyncio.run(async_statcast())
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return pl.LazyFrame() if not return_pandas else pd.DataFrame()


def statcast_single_batter_range_pitch_by_pitch(
    start_dt: str,
    end_dt: str,
    player_id: int,
    extra_stats: bool = False,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Pulls statcast data for single batter over a date range.

    Args:
        start_dt: the start date in 'YYYY-MM-DD' format
        end_dt: the end date in 'YYYY-MM-DD' format
        player_id: the player_id of the batter
        extra_stats: whether to include extra stats
        return_pandas: whether to return a pandas DataFrame (default is False, returning a Polars DataFrame)

    Returns:
        pl.DataFrame | pd.DataFrame: A DataFrame of statcast data for the date range.
    """

    async def async_statcast_single_batter():
        try:
            return await _statcast_single_batter_range_helper(
                start_dt, end_dt, str(player_id), extra_stats, return_pandas
            )
        except Exception as e:
            print(f"Error fetching statcast data for batter {player_id}: {str(e)}")
            # Return empty dataframe
            return pl.DataFrame() if not return_pandas else pd.DataFrame()

    try:
        return asyncio.run(async_statcast_single_batter())
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return pl.DataFrame() if not return_pandas else pd.DataFrame()


def statcast_single_pitcher_range_pitch_by_pitch(
    start_dt: str,
    end_dt: str,
    player_id: int,
    extra_stats: bool = False,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Pulls pitch by pitch statcast data for a single pitcher over a date range.

    Args:
        start_dt: the start date in 'YYYY-MM-DD' format
        end_dt: the end date in 'YYYY-MM-DD' format
        player_id: the player_id of the pitcher
        extra_stats: whether to include extra stats
        return_pandas: whether to return a pandas DataFrame (default is False, returning a Polars DataFrame)

    Returns:
        pl.DataFrame | pd.DataFrame: A DataFrame of statcast data for the date range.
    """

    async def async_statcast_single_pitcher():
        try:
            return await _statcast_single_pitcher_range_helper(
                start_dt, end_dt, str(player_id), extra_stats, return_pandas
            )
        except Exception as e:
            print(f"Error fetching statcast data for pitcher {player_id}: {str(e)}")
            # Return empty dataframe
            return pl.DataFrame() if not return_pandas else pd.DataFrame()

    try:
        return asyncio.run(async_statcast_single_pitcher())
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return pl.DataFrame() if not return_pandas else pd.DataFrame()
