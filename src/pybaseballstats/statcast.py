import asyncio
from typing import Literal

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
    start_date: str,
    end_date: str,
    perspective: Literal["pitcher", "batter"] = "pitcher",
    return_pandas: bool = False,
) -> pl.LazyFrame | pd.DataFrame:
    async def async_statcast():
        return await _statcast_date_range_helper(
            start_date, end_date, perspective, return_pandas
        )

    return asyncio.run(async_statcast())


def statcast_single_batter_range_pitch_by_pitch(
    start_dt: str,
    end_dt: str,
    player_id: int,
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
                start_dt, end_dt, str(player_id), return_pandas
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
                start_dt, end_dt, str(player_id), return_pandas
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
