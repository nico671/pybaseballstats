"""Public umpire scorecards data interface."""

from ._umpire_scorecards import game_data as game_data
from ._umpire_scorecards import player_data as player_data
from ._umpire_scorecards import team_data as team_data
from ._umpire_scorecards import umpire_data as umpire_data

__all__ = [
    "player_data",
    "game_data",
    "umpire_data",
    "team_data",
]


def __dir__() -> list[str]:
    return __all__
