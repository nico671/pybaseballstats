import asyncio
import io
import logging as logger

import nest_asyncio
import pandas as pd
import polars as pl
import requests

from .utils.statcast_utils import (
    ROOT_URL,
    SINGLE_GAME,
    _add_extra_stats,
    _statcast_date_range_helper,
)

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# TODO: add more data to be pulled (leaderboard) https://baseballsavant.mlb.com/leaderboard/top


def statcast_single_game(
    game_pk: int, extra_stats: bool, return_pandas: bool = False
) -> pl.LazyFrame | pd.DataFrame:
    """Pulls statcast data for a single game.

    Args:
        game_pk (int): game_pk of the game you want to pull data for
        extra_stats (bool): whether or not to include extra stats
        return_pandas (bool, optional): whether or not to return as a Pandas DataFrame. Defaults to False (returns Polars LazyFrame).

    Returns:
        pl.LazyFrame | pd.DataFrame: DataFrame of statcast data for the game
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
    team: the team abbreviation you wish to restrict data to (e.g. 'WSH'). If None, data for all teams will be returned.
    extra_stats: whether to include extra stats
    return_pandas: whether to return a pandas DataFrame (default is False, returning a Polars LazyFrame)

    Returns:
        pl.LazyFrame | pd.Dataframe: A DataFrame of statcast data for the date range.
    """

    async def async_statcast():
        return await _statcast_date_range_helper(
            start_dt, end_dt, team, extra_stats, return_pandas
        )

    return asyncio.run(async_statcast())
