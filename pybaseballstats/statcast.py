import asyncio
import io
import logging as logger

import pandas as pd
import polars as pl
import requests

from .statcast_utils import (
    ROOT_URL,
    SINGLE_GAME,
    _add_extra_stats,
    _statcast_date_range_helper,
)


def statcast_single_game(
    game_pk: int, extra_stats: bool, return_pandas: bool = False
) -> pl.LazyFrame | pd.DataFrame:
    """
    Pulls statcast data for a single game.

    Args:
    game_pk: the MLB game primary key
    extra_stats: whether to include extra stats

    Returns:
    A DataFrame of statcast data for the game.
    """
    try:
        statcast_content = requests.get(
            ROOT_URL + SINGLE_GAME.format(game_pk=game_pk), timeout=None
        ).content
    except Exception as e:
        logger.error(f"Failed to pull data for game_pk: {game_pk}. {str(e)}")
        return pl.LazyFrame() if not return_pandas else pd.DataFrame()
    if not extra_stats:
        return (
            pl.scan_csv(io.StringIO(statcast_content.decode("utf-8")))
            if not return_pandas
            else pd.read_csv(io.StringIO(statcast_content.decode("utf-8")))
        )
    else:
        df = pl.scan_csv(io.StringIO(statcast_content.decode("utf-8")))
        start_dt = df.select(pl.col("game_date").min())
        end_dt = df.select(pl.col("game_date").max())
        return asyncio.run(_add_extra_stats(df, start_dt, end_dt, return_pandas))


def statcast_date_range(
    start_dt: str,
    end_dt: str,
    team: str = None,
    extra_stats: bool = False,
    return_pandas: bool = False,
) -> pl.LazyFrame | pd.DataFrame:
    """
    Pulls statcast data for a date range.

    Args:
    start_dt: the start date in 'YYYY-MM-DD' format
    end_dt: the end date in 'YYYY-MM-DD' format
    team: the team abbreviation (e.g. 'WSH'). If None, data for all teams will be returned.
    extra_stats: whether to include extra stats
    return_pandas: whether to return a pandas DataFrame (default is False, returning a polars LazyFrame)

    Returns:
    A DataFrame of statcast data for the date range.
    """

    async def async_statcast():
        return await _statcast_date_range_helper(
            start_dt, end_dt, team, extra_stats, return_pandas
        )

    return asyncio.run(async_statcast())
