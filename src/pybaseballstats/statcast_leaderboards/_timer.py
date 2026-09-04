import io
from datetime import datetime
from typing import Literal

import polars as pl
import requests

from pybaseballstats.consts.statcast_leaderboard_consts import (
    TIMER_INFRACTIONS_LEADERBOARD_URL,
)


def timer_infractions_leaderboard(
    season: int,
    perspective: Literal["Pit", "Bat", "Cat", "Team"] = "Pit",
    min_pitches: int = 1,
) -> pl.DataFrame:
    """Return Baseball Savant pitch-timer infraction leaderboard data.

    Args:
        season (int): Season year.
        perspective (Literal["Pit", "Bat", "Cat", "Team"], optional):
            Leaderboard perspective.
        min_pitches (int, optional): Minimum pitch-count threshold.

    Raises:
        ValueError: If ``perspective`` is invalid.
        ValueError: If ``min_pitches`` is less than 1.
        ValueError: If ``season`` is outside valid supported years.

    Returns:
        pl.DataFrame: Timer-infraction leaderboard data.
    """
    if perspective not in ["Pit", "Bat", "Cat", "Team"]:
        raise ValueError("perspective must be one of 'Pit', 'Bat', 'Cat', or 'Team'")
    if min_pitches < 1:
        raise ValueError("min_pitches must be at least 1")
    curr_season = (
        datetime.now().year if datetime.now().month >= 3 else datetime.now().year - 1
    )
    if season < 2023 or season > curr_season:
        raise ValueError(f"Season must be between 2023 and {curr_season}")

    resp = requests.get(
        TIMER_INFRACTIONS_LEADERBOARD_URL.format(
            perspective=perspective, season=season, min_pitches=min_pitches
        )
    )
    df = pl.read_csv(io.StringIO(resp.text))
    df = df.rename(
        {
            "entity_name": "player_name"
            if perspective in ["Pit", "Bat", "Cat"]
            else "team_name",
            "entity_id": "player_id"
            if perspective in ["Pit", "Bat", "Cat"]
            else "team_id",
        }
    )
    return df
