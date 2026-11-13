import polars as pl
import pytest
from live_assertions import assert_live_frame, assert_numeric

import pybaseballstats.statcast_single_game as ssg

pytestmark = pytest.mark.live


def test_statcast_single_game_available_game_pks_for_date():
    game_pks = ssg.get_available_game_pks_for_date("2025-08-13")
    assert game_pks
    unique_game_pks = set(game["game_pk"] for game in game_pks)
    assert len(unique_game_pks) == len(game_pks)

    assert all(game["home_team"] and game["away_team"] for game in game_pks)

    assert all(game["home_team"] != game["away_team"] for game in game_pks)
    game_pks = ssg.get_available_game_pks_for_date("2020-12-25")
    assert len(game_pks) == 0


def test_statcast_single_game_pitch_by_pitch():
    df = ssg.single_game_pitch_by_pitch(game_pk=776759)
    assert_live_frame(
        df,
        columns=("game_pk", "game_date", "player_name"),
        counts=("game_pk", "pitcher", "batter"),
    )
    assert df.select(pl.col("game_pk").unique()).item() == 776759
    assert df.select(pl.col("game_date").unique()).item() == "2025-08-13"
    with pytest.raises(ValueError):
        ssg.single_game_pitch_by_pitch(game_pk=0)


def test_statcast_single_game_exit_velocity():
    for i in range(2):
        try:
            df = ssg.single_game_exit_velocity(game_date="2025-08-13", game_pk=776759)
        except Exception as e:
            print(
                f"Error occurred while fetching exit velocity data for game_pk 776759: {e}"
            )
            continue

    assert_live_frame(
        df,
        columns=("batter_name",),
        numeric=("exit_velo", "launch_angle", "pitch_velocity"),
        counts=("inning", "num_pa"),
    )
    with pytest.raises(ValueError):
        ssg.single_game_exit_velocity(game_date="2025-08-13", game_pk=0)


def test_statcast_single_game_pitch_velocity():
    df = ssg.single_game_pitch_velocity(game_date="2025-08-13", game_pk=776759)
    assert_live_frame(
        df,
        columns=("pitch_type", "pitcher_name", "batter_name"),
        numeric=(
            "pitch_velocity_mph",
            "spin_rate_rpm",
            "induced_vertical_break",
            "horizontal_break",
        ),
        counts=("inning", "game_pitch_number", "game_pa_number"),
        unique_by=("game_pitch_number",),
    )
    assert df["pitch_type"].dtype == pl.String
    assert df["pitch_type"].null_count() == 0
    with pytest.raises(ValueError):
        ssg.single_game_pitch_velocity(game_date="2025-08-13", game_pk=0)


def test_statcast_single_game_win_probability():
    df = ssg.single_game_win_probability(game_date="2025-08-13", game_pk=776759)

    assert_live_frame(
        df,
        columns=("inning", "batter_name", "pitcher_name"),
        numeric=("Home WP%", "Away WP%", "win_probability_diff"),
        counts=("game_pa_number",),
    )
    assert df["inning"].null_count() == 0
    assert_numeric(df["Away WP%"], minimum=0, maximum=100)
    assert_numeric(df["Home WP%"], minimum=0, maximum=100)

    with pytest.raises(ValueError):
        ssg.single_game_win_probability(game_date="2025-08-13", game_pk=0)
