"""Public bref single player data interface."""

from ._bref_single_player import single_player_batting as single_player_batting
from ._bref_single_player import single_player_fielding as single_player_fielding
from ._bref_single_player import single_player_pitching as single_player_pitching

__all__ = [
    "single_player_batting",
    "single_player_pitching",
    "single_player_fielding",
]


def __dir__() -> list[str]:
    return __all__
