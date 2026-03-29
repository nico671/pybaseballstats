import asyncio
import io
from typing import Dict, List

import nest_asyncio  # type: ignore
import polars as pl
import requests

from pybaseballstats.consts.statcast_consts import (
    STATCAST_SINGLE_GAME_URL,
)
from pybaseballstats.statcast import pitch_by_pitch_data

__all__ = [
    "get_available_game_pks_for_date",
    "single_game_pitch_by_pitch",
    # "single_game_exit_velocity",
    # "single_game_pitch_velocity",
    # "single_game_win_probability",
]


# helper for running async code in sync functions
def _run_in_loop(coro):
    """Run an async coroutine in the current runtime context.

    If an event loop is already active (e.g. notebooks), this function applies
    ``nest_asyncio`` and reuses the running loop.

    Args:
        coro: Coroutine object to execute.

    Returns:
        Any: Result returned by ``coro``.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        nest_asyncio.apply()
        return loop.run_until_complete(coro)


def get_available_game_pks_for_date(
    game_date: str,
) -> List[Dict[str, str]]:
    """Return game IDs and teams for all games on a date.

    Args:
        game_date (str): Date in ``YYYY-MM-DD`` format.

    Returns:
        list[dict[str, str]]: One dictionary per game with ``game_pk``,
        ``home_team``, and ``away_team``.
    """
    available_games: List[Dict[str, str]] = []
    df = pitch_by_pitch_data(
        game_date,
        game_date,
        force_collect=True,  # we force collect here bc we only have one day, dataframe shouldnt be too large
    )  # don't need game date string conversion here, the pitch_by_pitch_data function handles that
    if df is None:
        return available_games
    assert isinstance(df, pl.DataFrame), "Dataframe is not a Polars DataFrame"
    if df.shape[0] == 0 or df.shape[1] == 0:
        print(
            "No games found for the specified date. Please check the date format / date and try again."
        )
        return available_games

    for i, group in df.group_by("game_pk"):
        game_pk = group.select(pl.col("game_pk").first()).item()
        game_data = {}
        game_data["game_pk"] = game_pk
        game_data["home_team"] = group.select(pl.col("home_team").first()).item()
        game_data["away_team"] = group.select(pl.col("away_team").first()).item()
        available_games.append(game_data)
    return available_games


def single_game_pitch_by_pitch(game_pk: int) -> pl.DataFrame:
    """Return Statcast pitch-by-pitch data for one game.

    Args:
        game_pk (int): Baseball Savant game identifier.

    Returns:
        pl.DataFrame: Pitch-level Statcast data for the requested game.
    """
    response = requests.get(
        STATCAST_SINGLE_GAME_URL.format(game_pk=game_pk),
    )
    statcast_content = response.content
    df = pl.read_csv(io.StringIO(statcast_content.decode("utf-8")))
    return df
