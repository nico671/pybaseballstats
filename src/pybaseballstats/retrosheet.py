"""Public retrosheet data interface."""

from ._retrosheet import ejections_data as ejections_data
from ._retrosheet import player_lookup as player_lookup

__all__ = [
    "player_lookup",
    "ejections_data",
]


def __dir__() -> list[str]:
    return __all__
