from .fangraphs import (  # noqa: F401
    fangraphs_batting_range,
    fangraphs_fielding_range,
    fangraphs_pitching_range,
)
from .player_lookup import player_lookup  # noqa: F401
from .plotting import (  # noqa: F401
    plot_scatter_on_sz,
    plot_stadium,
    plot_strike_zone,
    scatter_plot_over_stadium,
)
from .statcast import (  # noqa: F401
    statcast_date_range,
    statcast_single_batter_range,
    statcast_single_game,
    statcast_single_pitcher_range,
)
from .statcast_leaderboards import (  # noqa: F401
    statcast_bat_tracking_leaderboard,
)

# from .statcast_leaderboards import (  # noqa: F401
#     # statcast_arm_strength,
#     statcast_bat_tracking,
#     statcast_catcher_stats,
#     statcast_exit_velo_barrels,
#     statcast_expected_stats,
#     statcast_pitch_arsenal,
#     statcast_pitching_active_spin,
#     statcast_pitching_arm_angle,
# )
from .umpire_scorecard import (  # noqa: F401
    UmpireScorecardTeams,
    team_umpire_stats_date_range,
    umpire_games_date_range,
    umpire_stats_date_range,
)

# Re-export only necessary Enums from fangraphs_utils
from .utils.fangraphs_utils import (  # noqa: F401
    FangraphsBattingPosTypes,
    FangraphsBattingStatType,
    FangraphsFieldingStatType,
    FangraphsLeagueTypes,
    FangraphsPitchingStatType,
    FangraphsStatSplitTypes,
    FangraphsTeams,
)

# # Define public API
# __all__ = [
#     "statcast_exit_velo_barrels",
#     "statcast_bat_tracking",
#     "fangraphs_batting_range",
#     "fangraphs_pitching_range",
#     "plot_scatter_on_sz",
#     "plot_stadium",
#     "plot_strike_zone",
#     "scatter_plot_over_stadium",
#     "statcast_single_pitcher_range",
#     "statcast_date_range",
#     "statcast_single_batter_range",
#     "statcast_single_game",
#     "UmpireScorecardTeams",
#     "team_umpire_stats_date_range",
#     "umpire_games_date_range",
#     "umpire_stats_date_range",
#     "FangraphsBattingPosTypes",
#     "FangraphsBattingStatType",
#     "FangraphsFieldingStatType",
#     "FangraphsLeagueTypes",
#     "FangraphsPitchingStatType",
#     "FangraphsStatSplitTypes",
#     "FangraphsTeams",
#     "fangraphs_fielding_range",
# ]
