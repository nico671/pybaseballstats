"""Checks for supported import and completion surfaces."""

import ast
import importlib
import inspect
from pathlib import Path

import pybaseballstats
from pybaseballstats import enums

EXPECTED = {
    "bref_draft": {"draft_order_by_year_round", "franchise_draft_order"},
    "bref_managers": {"managers_basic_data", "managers_tendencies_data"},
    "bref_single_player": {
        "single_player_batting",
        "single_player_pitching",
        "single_player_fielding",
    },
    "bref_teams": {
        "game_by_game_schedule_results",
        "roster_and_appearances",
        "batting_orders",
        "batting",
        "pitching",
        "fielding",
    },
    "retrosheet": {"player_lookup", "ejections_data"},
    "statcast": {"pitch_by_pitch_data"},
    "statcast_leaderboards": {
        "park_factor_yearly_leaderboard",
        "park_factor_distance_leaderboard",
        "park_factor_dimensions_leaderboard",
        "timer_infractions_leaderboard",
        "percentile_rankings_leaderboard",
        "arm_strength_leaderboard",
        "fielding_run_value_leaderboard",
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
    },
    "statcast_single_game": {
        "get_available_game_pks_for_date",
        "single_game_pitch_by_pitch",
        "single_game_exit_velocity",
        "single_game_pitch_velocity",
        "single_game_win_probability",
    },
    "statcast_single_player": {
        "single_player_pitch_by_pitch",
        "single_player_season_stats",
    },
    "umpire_scorecards": {"player_data", "game_data", "umpire_data", "team_data"},
}


def test_public_exports_and_stubs():
    assert set(pybaseballstats.__all__) == set(EXPECTED) | {"enums"}
    for name, expected in EXPECTED.items():
        module = importlib.import_module(f"pybaseballstats.{name}")
        assert getattr(pybaseballstats, name) is module
        assert set(module.__all__) == expected
        assert set(dir(module)) == expected
        stub = Path(module.__file__).with_suffix(".pyi")
        tree = ast.parse(stub.read_text())
        exports = {
            alias.asname
            for node in tree.body
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
            if alias.asname is not None
        }
        assert exports == expected
        for function_name in expected:
            function = getattr(module, function_name)
            assert inspect.isfunction(function)
            assert function.__doc__
        for hidden in (
            "requests",
            "session",
            "get_csv",
            "BREFTeams",
            "StatcastTeams",
            "StatcastLeaderboardsTeams",
            "UmpireScorecardTeams",
            "game_type_options",
        ):
            assert not hasattr(module, hidden)


def test_enum_identity_and_aliases():
    from pybaseballstats._consts.bref_consts import BREFTeams
    from pybaseballstats._consts.statcast_consts import StatcastTeams
    from pybaseballstats._consts.statcast_leaderboard_consts import (
        StatcastLeaderboardsTeams,
    )
    from pybaseballstats._consts.umpire_scorecard_consts import UmpireScorecardTeams

    assert enums.BREFTeams is BREFTeams
    assert enums.StatcastTeams is StatcastTeams
    assert enums.StatcastLeaderboardsTeams is StatcastLeaderboardsTeams
    assert enums.UmpireScorecardTeams is UmpireScorecardTeams
    assert enums.UmpireScorecardTeams.GUARDIANS is enums.UmpireScorecardTeams.GAURDIANS
    assert (
        enums.StatcastLeaderboardsTeams.DIAMONDBACKS
        is enums.StatcastLeaderboardsTeams.D_BACKS
    )
    assert enums.UmpireScorecardTeams.TIGERS.value == "DET"
    assert len(enums.UmpireScorecardTeams) == 31  # 30 teams and ALL
    assert len(enums.StatcastLeaderboardsTeams) == 30
    assert len(enums.BREFTeams) == len(enums.StatcastTeams) == 30


def test_bref_team_code_uses_nearest_known_year():
    from pybaseballstats._utils.bref_utils import resolve_bref_team_code

    assert resolve_bref_team_code(enums.BREFTeams.ATHLETICS, 2024) == "OAK"
    assert resolve_bref_team_code(enums.BREFTeams.ATHLETICS, 2025) == "ATH"
    assert resolve_bref_team_code(enums.BREFTeams.ATHLETICS, 2026) == "ATH"
    assert resolve_bref_team_code(enums.BREFTeams.ATHLETICS, 2027) == "ATH"
    assert resolve_bref_team_code(enums.BREFTeams.ANGELS, 1960) == "LAA"
