import asyncio

import nest_asyncio
import pandas as pd
import polars as pl

from .utils.statcast_utils import (
    _statcast_date_range_helper,
)

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()


# TODO: usage docs
def statcast_date_range_pitch_by_pitch(
    start_date: str,
    end_date: str,
    return_pandas: bool = False,
) -> pl.LazyFrame | pd.DataFrame:
    async def async_statcast():
        return await _statcast_date_range_helper(start_date, end_date, return_pandas)

    return asyncio.run(async_statcast())


# TODO: SINGLEPLAYER function
