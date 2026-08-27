from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Callable

import polars as pl
import pytest

import pybaseballstats.retrosheet as retrosheet
import pybaseballstats.statcast as statcast
import pybaseballstats.statcast_leaderboards as leaderboards
import pybaseballstats.statcast_single_game as single_game
import pybaseballstats.statcast_single_player as single_player
import pybaseballstats.umpire_scorecards as umpire_scorecards


pytestmark = pytest.mark.live


def assert_frame(df: pl.DataFrame, required_columns: set[str]) -> None:
    assert not df.is_empty()
    assert required_columns <= set(df.columns)


def run_in_thread(function: Callable[..., pl.DataFrame], **kwargs: object) -> pl.DataFrame:
    """Keep Playwright's sync API outside pytest's asyncio-aware main thread."""
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(function, **kwargs).result()


def test_retrosheet_people_registry_endpoint():
    df = retrosheet.player_lookup(first_name="Babe", last_name="Ruth")
    assert_frame(df, {"key_retro", "key_bbref", "name_first", "name_last"})


def test_retrosheet_ejections_endpoint():
    df = retrosheet.ejections_data(start_date="04/01/2023", end_date="10/01/2023")
    assert_frame(df, {"DATE", "EJECTEENAME", "UMPIRENAME", "INNING"})


@pytest.mark.parametrize(
    ("function", "kwargs", "required_columns"),
    (
        (
            umpire_scorecards.game_data,
            {"start_date": "2025-07-01", "end_date": "2025-07-07"},
            {"date", "umpire"},
        ),
        (
            umpire_scorecards.umpire_data,
            {"start_date": "2025-07-01", "end_date": "2025-07-07"},
            {"umpire", "n"},
        ),
        (
            umpire_scorecards.team_data,
            {"start_date": "2025-07-01", "end_date": "2025-07-07"},
            {"team"},
        ),
        (
            umpire_scorecards.player_data,
            {
                "start_date": "2025-07-01",
                "end_date": "2025-07-07",
                "player_type": "C",
            },
            {"player_id", "n_pitches"},
        ),
    ),
    ids=("games", "umpires", "teams", "players"),
)
def test_umpire_scorecards_endpoint(function, kwargs, required_columns):
    assert_frame(function(**kwargs), required_columns)


def test_statcast_date_range_endpoint():
    df = statcast.pitch_by_pitch_data(
        start_date="2023-07-01",
        end_date="2023-07-01",
        force_collect=True,
        show_progress=False,
    )
    assert isinstance(df, pl.DataFrame)
    assert_frame(df, {"game_pk", "game_date", "player_name"})


def test_statcast_single_player_endpoint():
    df = single_player.single_player_season_stats(
        player_id=660271,
        season=2024,
        player_type="batter",
    )
    assert_frame(df, {"player_id", "player_name", "pitches"})


def test_statcast_single_game_csv_endpoint():
    df = single_game.single_game_pitch_by_pitch(game_pk=776759)
    assert_frame(df, {"game_pk", "game_date", "player_name"})


@pytest.mark.parametrize(
    ("function", "required_columns"),
    (
        (single_game.single_game_exit_velocity, {"inning", "exit_velo"}),
        (single_game.single_game_pitch_velocity, {"inning", "pitch_type"}),
        (single_game.single_game_win_probability, {"inning", "Home WP%"}),
    ),
    ids=("exit-velocity", "pitch-velocity", "win-probability"),
)
def test_statcast_gamefeed_endpoint(function, required_columns):
    df = function(game_pk=776759, game_date="2025-08-13")
    assert_frame(df, required_columns)


@pytest.mark.parametrize(
    ("name", "fetch", "required_columns"),
    (
        (
            "park-dimensions",
            lambda: run_in_thread(
                leaderboards.park_factor_dimensions_leaderboard,
                season=2025,
                metric="distance",
            ),
            {"Team", "Venue"},
        ),
        (
            "park-yearly",
            lambda: run_in_thread(
                leaderboards.park_factor_yearly_leaderboard,
                season=2025,
                rolling_years=3,
            ),
            {"Team", "Venue", "Park Factor"},
        ),
        (
            "park-distance",
            lambda: run_in_thread(
                leaderboards.park_factor_distance_leaderboard,
                season=2023,
            ),
            {"Team", "Venue"},
        ),
        (
            "timer-infractions",
            lambda: leaderboards.timer_infractions_leaderboard(
                season=2023, perspective="Team"
            ),
            {"year", "all_violations"},
        ),
        (
            "abs-challenges",
            lambda: leaderboards.abs_challenges_leaderboard(season=2026),
            {"level", "team_abbr"},
        ),
        (
            "arm-strength",
            lambda: leaderboards.arm_strength_leaderboard(
                stat_type="team", year=2025, min_throws=10
            ),
            {"team_name"},
        ),
        (
            "spin-direction",
            lambda: leaderboards.spin_direction_leaderboard(
                season=2025, min_pitches=100
            ),
            {"player_name", "n_pitches"},
        ),
        (
            "active-spin",
            lambda: leaderboards.active_spin_leaderboard(
                season=2023, min_pitches=100
            ),
            {"player_id"},
        ),
        (
            "arm-angle",
            lambda: leaderboards.arm_angle_leaderboard(
                start_date="2023-04-01",
                end_date="2023-10-01",
                min_pitches=100,
            ),
            {"n_pitches"},
        ),
        (
            "pitch-arsenals",
            lambda: leaderboards.pitch_arsenals_leaderboard(
                season=2023, min_pitches=100
            ),
            {"player_id"},
        ),
        (
            "pitch-movement",
            lambda: leaderboards.pitch_movement_leaderboard(
                season=2023, min_pitches=100
            ),
            {"pitcher_id", "pitches_thrown"},
        ),
        (
            "catcher-blocking",
            lambda: leaderboards.catcher_blocking_leaderboard(
                start_season=2023,
                end_season=2023,
                min_pitches=100,
            ),
            {"player_id", "player_name", "pitches", "blocks_above_average"},
        ),
        (
            "catcher-framing",
            lambda: leaderboards.catcher_framing_leaderboard(
                start_season=2023,
                end_season=2023,
                min_pitches=100,
            ),
            {"player_id", "player_name", "pitches", "rv_tot"},
        ),
        (
            "catcher-pop-time",
            lambda: leaderboards.catcher_pop_time_leaderboard(season=2023),
            {"entity_name", "entity_id", "pop_2b_sba", "pop_3b_sba"},
        ),
        (
            "pitcher-running-game",
            lambda: leaderboards.pitcher_running_game_leaderboard(
                start_season=2023,
                end_season=2023,
                min_sb_opportunities=10,
            ),
            {"player_id", "n_init"},
        ),
    ),
    ids=(
        "park-dimensions",
        "park-yearly",
        "park-distance",
        "timer-infractions",
        "abs-challenges",
        "arm-strength",
        "spin-direction",
        "active-spin",
        "arm-angle",
        "pitch-arsenals",
        "pitch-movement",
        "catcher-blocking",
        "catcher-framing",
        "catcher-pop-time",
        "pitcher-running-game",
    ),
)
def test_statcast_leaderboard_endpoint(name, fetch, required_columns):
    assert_frame(fetch(), required_columns)
