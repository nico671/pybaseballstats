"""Public bref teams data interface."""

from ._bref_teams import batting as batting
from ._bref_teams import batting_orders as batting_orders
from ._bref_teams import fielding as fielding
from ._bref_teams import game_by_game_schedule_results as game_by_game_schedule_results
from ._bref_teams import pitching as pitching
from ._bref_teams import roster_and_appearances as roster_and_appearances

__all__ = [
    "game_by_game_schedule_results",
    "roster_and_appearances",
    "batting_orders",
    "batting",
    "pitching",
    "fielding",
]


def __dir__() -> list[str]:
    return __all__
