"""Team filters for the supported data sources."""

from ._consts.bref_consts import BREFTeams as BREFTeams
from ._consts.statcast_consts import StatcastTeams as StatcastTeams
from ._consts.statcast_leaderboard_consts import (
    StatcastLeaderboardsTeams as StatcastLeaderboardsTeams,
)
from ._consts.umpire_scorecard_consts import (
    UmpireScorecardTeams as UmpireScorecardTeams,
)

__all__ = [
    "BREFTeams",
    "StatcastTeams",
    "StatcastLeaderboardsTeams",
    "UmpireScorecardTeams",
]


def __dir__() -> list[str]:
    return __all__
