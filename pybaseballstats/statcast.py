import asyncio
import io
import logging as logger

import pandas as pd
import polars as pl
import requests
from statcast_utils import (
    EXTRA_STATS,
    ROOT_URL,
    SINGLE_GAME,
    _statcast_date_range_helper,
)


def statcast_single_game(
    game_pk: int, extra_stats: bool, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
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
        return pl.DataFrame() if not return_pandas else pd.DataFrame()
    if not extra_stats:
        return (
            pl.read_csv(io.StringIO(statcast_content.decode("utf-8")))
            if not return_pandas
            else pd.read_csv(io.StringIO(statcast_content.decode("utf-8")))
        )
    else:
        df = pl.read_csv(io.StringIO(statcast_content.decode("utf-8")))
        df_list = []
        urls = [ROOT_URL + EXTRA_STATS.format(pos=pos) for pos in ["pitcher", "batter"]]
        for url in urls:
            try:
                extra_content = requests.get(url, timeout=None).content
                df_list.append(pl.read_csv(io.StringIO(extra_content.decode("utf-8"))))
            except Exception as e:
                logger.error(f"Failed to pull data for game_pk: {game_pk}. {str(e)}")
                return pl.DataFrame()
        p_df = df_list[0]
        p_df = p_df.drop("player_name").rename(lambda x: f"{x}_pitcher")
        b_df = df_list[1]
        b_df = b_df.drop("player_name").rename(lambda x: f"{x}_batter")
        df = df.join(p_df, left_on="pitcher", right_on="player_id_pitcher", how="left")
        df = df.join(b_df, left_on="batter", right_on="player_id_batter", how="left")
        return df


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
