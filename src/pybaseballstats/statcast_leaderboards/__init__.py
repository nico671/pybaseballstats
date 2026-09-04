"""Public Baseball Savant Statcast leaderboard interface."""

import requests as _requests

from pybaseballstats.consts.statcast_leaderboard_consts import (
    StatcastLeaderboardsTeams,
)

from ._abs import abs_challenges_leaderboard
from ._baserunning import (
    baserunning_run_value_leaderboard,
    basestealing_run_value_leaderboard,
    extra_bases_taken_run_value_leaderboard,
    running_splits_leaderboard,
    sprint_speed_leaderboard,
)
from ._catching import (
    catcher_blocking_leaderboard,
    catcher_framing_leaderboard,
    catcher_pop_time_leaderboard,
    catcher_stance_leaderboard,
    catcher_throwing_leaderboard,
)
from ._fielding import arm_strength_leaderboard
from ._park import (
    park_factor_dimensions_leaderboard,
    park_factor_distance_leaderboard,
    park_factor_yearly_leaderboard,
)
from ._pitching import (
    active_spin_leaderboard,
    arm_angle_leaderboard,
    pitch_arsenals_leaderboard,
    pitch_movement_leaderboard,
    pitcher_running_game_leaderboard,
    spin_direction_leaderboard,
)
from ._rankings import percentile_rankings_leaderboard
from ._timer import timer_infractions_leaderboard

# Backward-compatible test seam. It is intentionally absent from the public API.
requests = _requests

__all__ = [
    "StatcastLeaderboardsTeams",
    "park_factor_yearly_leaderboard",
    "park_factor_distance_leaderboard",
    "park_factor_dimensions_leaderboard",
    "timer_infractions_leaderboard",
    "percentile_rankings_leaderboard",
    "arm_strength_leaderboard",
    "abs_challenges_leaderboard",
    "spin_direction_leaderboard",
    "catcher_blocking_leaderboard",
    "catcher_framing_leaderboard",
    "catcher_pop_time_leaderboard",
    "catcher_stance_leaderboard",
    "catcher_throwing_leaderboard",
    "active_spin_leaderboard",
    "arm_angle_leaderboard",
    "pitch_arsenals_leaderboard",
    "pitch_movement_leaderboard",
    "pitcher_running_game_leaderboard",
    "baserunning_run_value_leaderboard",
    "basestealing_run_value_leaderboard",
    "extra_bases_taken_run_value_leaderboard",
    "sprint_speed_leaderboard",
    "running_splits_leaderboard",
]


def __dir__() -> list[str]:
    """Return only the supported interactive interface."""
    return __all__
