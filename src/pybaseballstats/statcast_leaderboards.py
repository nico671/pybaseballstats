from typing import Literal

import polars as pl
import requests

import pybaseballstats.consts.statcast_leaderboard_consts as sc

__all__ = ["pitch_timer_infractions_leaderboard"]


def pitch_timer_infractions_leaderboard(
    focus: Literal["Pit", "Cat", "Bat", "Team", "Opp"] = "Pit",
    season: int = 2025,
    min_pitches: int = 1000,
    include_non_violators: bool = True,
) -> pl.DataFrame:
    """Returns the Pitch Timer Infractions Leaderboard from Baseball Savant.

    Args:
        focus (str, optional): The player type to focus on (Pitchers, Catchers, Batters, Teams, or Opponent Teams). Defaults to "Pit".
        season (int, optional): The MLB season to filter by. Defaults to 2025.
        min_pitches (int, optional): The minimum number of pitches to qualify for the leaderboard, only matters when focus is set to "Pit", "Cat" or "Bat". Defaults to 1000.
        include_non_violators (bool, optional): Whether to include individuals with no infractions, only matters when focus is set to "Pit", "Cat" or "Bat". Defaults to True.

    Raises:
        ValueError: If the focus parameter isn't one of the valid options.
        ValueError: If the season parameter is invalid.
        ValueError: If the min_pitches parameter is invalid.
        ValueError: If the include_non_violators parameter is invalid.

    Returns:
        pl.DataFrame: The Pitch Timer Infractions Leaderboard.
    """
    # Validate and process input parameters
    if focus not in ["Pit", "Cat", "Bat", "Team", "Opp"]:
        raise ValueError("Invalid focus parameter.")
    if season < 2023 or season > 2025:
        raise ValueError("Invalid season parameter.")
    if min_pitches < 0:
        raise ValueError("Invalid min_pitches parameter.")
    if not isinstance(include_non_violators, bool):
        raise ValueError("Invalid include_non_violators parameter.")

    url = sc.PITCH_TIMER_INFRACTIONS_LEADERBOARD_URL.format(
        stat_type=focus,
        season=season,
        min_pitches=min_pitches,
        include_pitchers_with_zeroes=int(include_non_violators),
    )
    resp = requests.get(url)
    df = pl.read_csv(resp.content)
    return df
