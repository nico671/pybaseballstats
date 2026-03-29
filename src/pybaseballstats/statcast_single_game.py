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
    """
    Runs an async coroutine synchronously.
    Handles cases where an event loop is already running (e.g., Jupyter).
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
    """Returns a list of all available gamePKs for a given date, as well as information on the home and away team for each game.

    Args:
        game_date (str): Date to get available gamePKs for in 'YYYY-MM-DD' format.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing gamePKs and information on the home and away teams for each game on the specified date.
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
    """Pulls statcast data for a single game.

    Args:
        game_pk (int): game_pk of the game you want to pull data for

    Returns:
        pl.DataFrame: DataFrame of pitch-by-pitch statcast data for the game
    """
    response = requests.get(
        STATCAST_SINGLE_GAME_URL.format(game_pk=game_pk),
    )
    statcast_content = response.content
    df = pl.read_csv(io.StringIO(statcast_content.decode("utf-8")))
    return df
