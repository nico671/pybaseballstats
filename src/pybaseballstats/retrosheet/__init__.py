"""Public Retrosheet data interface."""

from ._daily_logs import (
    batting_logs,
    fielding_logs,
    game_info,
    pitching_logs,
    player_seasons,
    plays,
    team_logs,
)
from ._games import (
    game_logs,
    schedules,
)
from ._personnel import (
    ejections_data,
    manager_logs,
    umpire_logs,
)
from ._reference import (
    ballpark_codes,
    ballparks,
    coach_assignments,
    coaches,
    franchise_codes,
    managers,
    people_bios,
    people_ids,
    player_lookup,
    relatives,
    teams,
    umpires,
)

__all__ = [
    "ballpark_codes",
    "ballparks",
    "batting_logs",
    "coach_assignments",
    "coaches",
    "ejections_data",
    "fielding_logs",
    "franchise_codes",
    "game_info",
    "game_logs",
    "manager_logs",
    "managers",
    "people_bios",
    "people_ids",
    "pitching_logs",
    "player_lookup",
    "player_seasons",
    "plays",
    "relatives",
    "schedules",
    "team_logs",
    "teams",
    "umpire_logs",
    "umpires",
]


def __dir__() -> list[str]:
    return __all__
