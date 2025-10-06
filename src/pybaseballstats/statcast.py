import asyncio

import nest_asyncio
import polars as pl
from consts.statcast_consts import STATCAST_DATE_RANGE_URL
from utils.statcast_utils import (
    _create_date_ranges,
    _fetch_all_data,
    _handle_dates,
    _load_all_data,
)

__all__ = ["statcast_date_range_pitch_by_pitch"]

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()


async def async_statcast_date_range_pitch_by_pitch(
    start_date: str,
    end_date: str,
    force_collect: bool = False,
) -> pl.LazyFrame:
    if start_date is None or end_date is None:
        raise ValueError("Both start_date and end_date must be provided")
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
            )
        )
    date_range_total_days = (end_dt - start_dt).days
    responses = await _fetch_all_data(urls, date_range_total_days)
    data_list = _load_all_data(responses)
    if not data_list:
        print("No data was successfully retrieved.")
        return None

    elif len(data_list) > 0:
        print("Concatenating data.")
        df = pl.concat(data_list)

    if force_collect:
        return df.collect()
    return df


# TODO: usage docs
# TODO: add more restrictions for api calls
def pitch_by_pitch_data(
    start_date: str,
    end_date: str,
    force_collect: bool = False,
) -> pl.LazyFrame:
    # async def async_statcast():
    #     return await _statcast_date_range_helper(start_date, end_date, return_pandas)

    return asyncio.run(
        async_statcast_date_range_pitch_by_pitch(
            start_date=start_date, end_date=end_date, force_collect=force_collect
        )
    )


# TODO: SINGLEPLAYER function
