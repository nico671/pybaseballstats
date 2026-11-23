"""Public retrosheet data interface."""

from ._retrosheet import ejections_data as ejections_data
from ._retrosheet import player_lookup as player_lookup
from ._retrosheet_logs import batting_logs as batting_logs
from ._retrosheet_logs import fielding_logs as fielding_logs
from ._retrosheet_logs import game_info as game_info
from ._retrosheet_logs import game_logs as game_logs
from ._retrosheet_logs import manager_logs as manager_logs
from ._retrosheet_logs import pitching_logs as pitching_logs
from ._retrosheet_logs import player_seasons as player_seasons
from ._retrosheet_logs import plays as plays
from ._retrosheet_logs import schedules as schedules
from ._retrosheet_logs import team_logs as team_logs
from ._retrosheet_logs import umpire_logs as umpire_logs
from ._retrosheet_reference import ballpark_codes as ballpark_codes
from ._retrosheet_reference import ballparks as ballparks
from ._retrosheet_reference import coach_assignments as coach_assignments
from ._retrosheet_reference import coaches as coaches
from ._retrosheet_reference import franchise_codes as franchise_codes
from ._retrosheet_reference import managers as managers
from ._retrosheet_reference import people_bios as people_bios
from ._retrosheet_reference import people_ids as people_ids
from ._retrosheet_reference import relatives as relatives
from ._retrosheet_reference import teams as teams
from ._retrosheet_reference import umpires as umpires

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
