import pandas as pd
import polars as pl
import pytest
from polars.testing import assert_frame_equal, assert_series_not_equal

import pybaseballstats as pyb


def test_statcast_bat_tracking_leaderboard_bad_inputs():
    with pytest.raises(ValueError):
        pyb.statcast_bat_tracking_leaderboard(
            start_dt="2021-01-01", end_dt="2021-01-01"
        )
    with pytest.raises(ValueError):
        pyb.statcast_bat_tracking_leaderboard(
            start_dt="2024-01-01", end_dt="2023-01-01"
        )
    with pytest.raises(ValueError):
        pyb.statcast_bat_tracking_leaderboard(
            start_dt="2024-04-10", end_dt="2024-04-15", min_swings="nq"
        )
    with pytest.raises(ValueError):
        pyb.statcast_bat_tracking_leaderboard(
            start_dt="2024-04-10", end_dt="2024-04-15", min_swings=0
        )
    with pytest.raises(ValueError):
        pyb.statcast_bat_tracking_leaderboard(
            start_dt="2024-04-10", end_dt="2024-04-15", perspective="individual"
        )


def test_statcast_bat_tracking_leaderboard_regular():
    df = pyb.statcast_bat_tracking_leaderboard(
        start_dt="2024-04-10", end_dt="2024-04-15"
    )
    assert df.shape[0] == 197
    assert df.shape[1] == 18
    assert df["id"].n_unique() == 197
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_bat_tracking_leaderboard(
        start_dt="2024-04-10", end_dt="2024-04-15", return_pandas=True
    )
    assert df.shape[0] == 197
    assert df.shape[1] == 18
    assert df["id"].n_unique() == 197
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_bat_tracking_leaderboard_diffminswings():
    df = pyb.statcast_bat_tracking_leaderboard(
        start_dt="2024-04-10", end_dt="2024-04-15", min_swings=200
    )
    assert df.shape[0] == 337
    assert df.shape[1] == 18
    assert df["id"].n_unique() == 337
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_bat_tracking_leaderboard(
        start_dt="2024-04-10", end_dt="2024-04-15", min_swings=100
    )
    assert df2.shape[0] > df.shape[0]
    assert df2.shape[1] == 18
    assert df2["id"].n_unique() > df["id"].n_unique()
    assert type(df2) is pl.DataFrame


def test_statcast_bat_tracking_leaderboard_diffperspectives():
    df1 = pyb.statcast_bat_tracking_leaderboard(
        start_dt="2024-04-10", end_dt="2024-04-15", perspective="pitcher"
    )
    assert df1.shape[0] == 166
    assert df1.shape[1] == 18
    assert df1["id"].n_unique() == 166
    assert type(df1) is pl.DataFrame
    df2 = pyb.statcast_bat_tracking_leaderboard(
        start_dt="2024-04-10", end_dt="2024-04-15", perspective="batter"
    )
    assert_series_not_equal(df1["id"], df2["id"])
    df3 = pyb.statcast_bat_tracking_leaderboard(
        start_dt="2024-04-10", end_dt="2024-04-15", perspective="batting-team"
    )
    assert_series_not_equal(df1["id"], df3["id"])
    assert df3.shape[1] == 18
    assert df3.shape[0] == 30
    assert df3["id"].n_unique() == 30
    df4 = pyb.statcast_bat_tracking_leaderboard(
        start_dt="2024-04-10", end_dt="2024-04-15", perspective="pitching-team"
    )
    assert df4.shape[1] == 18
    assert df4.shape[0] == 30
    assert df4["id"].n_unique() == 30
    df5 = pyb.statcast_bat_tracking_leaderboard(
        start_dt="2024-04-10", end_dt="2024-04-15", perspective="league"
    )
    assert df5.shape[0] == 1
    assert df5.shape[1] == 18
    assert df5["id"].n_unique() == 1
    assert type(df5) is pl.DataFrame


def test_statcast_exit_velo_barrels_leaderboard_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_exit_velo_barrels_leaderboard(year=None)
    with pytest.raises(ValueError):
        pyb.statcast_exit_velo_barrels_leaderboard(year=2014)
    with pytest.raises(ValueError):
        pyb.statcast_exit_velo_barrels_leaderboard(year=2024, min_swings="nq")
    with pytest.raises(ValueError):
        pyb.statcast_exit_velo_barrels_leaderboard(year=2024, min_swings=0)
    with pytest.raises(ValueError):
        pyb.statcast_exit_velo_barrels_leaderboard(year=2024, perspective="individual")


def test_statcast_exit_velo_barrels_leaderboard_regular():
    df = pyb.statcast_exit_velo_barrels_leaderboard(year=2024)
    assert df.shape[0] == 252
    assert df.shape[1] == 18
    assert df["player_id"].n_unique() == 252
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_exit_velo_barrels_leaderboard(year=2024, return_pandas=True)
    assert df2.shape[0] == 252
    assert df2.shape[1] == 18
    assert df2["player_id"].nunique() == 252
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_exit_velo_barrels_leaderboard_diffminswings():
    df = pyb.statcast_exit_velo_barrels_leaderboard(year=2024, min_swings=200)
    assert df.shape[0] == 284
    assert df.shape[1] == 18
    assert df["player_id"].n_unique() == 284
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_exit_velo_barrels_leaderboard(year=2024, min_swings=100)
    assert df2.shape[0] > df.shape[0]
    assert df2.shape[1] == 18
    assert df2["player_id"].n_unique() > df["player_id"].n_unique()
    assert type(df2) is pl.DataFrame


def test_statcast_exit_velo_barrels_leaderboard_diffperspectives():
    df1 = pyb.statcast_exit_velo_barrels_leaderboard(year=2024, perspective="pitcher")
    assert df1.shape[0] == 366
    assert df1.shape[1] == 18
    assert df1["player_id"].n_unique() == 366
    assert type(df1) is pl.DataFrame
    df2 = pyb.statcast_exit_velo_barrels_leaderboard(year=2024, perspective="batter")
    assert_series_not_equal(df1["player_id"], df2["player_id"])
    df3 = pyb.statcast_exit_velo_barrels_leaderboard(
        year=2024, perspective="batter-team"
    )
    assert df3.shape[1] == 18
    assert df3.shape[0] == 30
    assert df3["team_id"].n_unique() == 30
    df4 = pyb.statcast_exit_velo_barrels_leaderboard(
        year=2024, perspective="pitcher-team"
    )
    assert df4.shape[1] == 18
    assert df4.shape[0] == 30
    assert df4["team_id"].n_unique() == 30


def test_statcast_expected_stats_leaderboard_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_expected_stats_leaderboard(year=None)
    with pytest.raises(ValueError):
        pyb.statcast_expected_stats_leaderboard(year=2014)
    with pytest.raises(ValueError):
        pyb.statcast_expected_stats_leaderboard(year=2024, min_balls_in_play="nq")
    with pytest.raises(ValueError):
        pyb.statcast_expected_stats_leaderboard(year=2024, min_balls_in_play=0)
    with pytest.raises(ValueError):
        pyb.statcast_expected_stats_leaderboard(year=2024, perspective="individual")


def test_statcast_expected_stats_leaderboard_regular():
    df = pyb.statcast_expected_stats_leaderboard(year=2024)
    assert df.shape[0] == 252
    assert df.shape[1] == 18
    assert df["player_id"].n_unique() == 252
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_expected_stats_leaderboard(year=2024, return_pandas=True)
    assert df2.shape[0] == 252
    assert df2.shape[1] == 18
    assert df2["player_id"].nunique() == 252
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_expected_stats_leaderboard_diffminballs():
    df = pyb.statcast_expected_stats_leaderboard(year=2024, min_balls_in_play=200)
    assert df.shape[0] == 284
    assert df.shape[1] == 18
    assert df["player_id"].n_unique() == 284
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_expected_stats_leaderboard(year=2024, min_balls_in_play=100)
    assert df2.shape[0] > df.shape[0]
    assert df2.shape[1] == 18
    assert df2["player_id"].n_unique() > df["player_id"].n_unique()
    assert type(df2) is pl.DataFrame


def test_statcast_expected_stats_leaderboard_diffperspectives():
    df1 = pyb.statcast_expected_stats_leaderboard(year=2024, perspective="pitcher")
    assert df1.shape[0] == 366
    assert df1.shape[1] == 18
    assert df1["player_id"].n_unique() == 366
    assert type(df1) is pl.DataFrame
    df2 = pyb.statcast_expected_stats_leaderboard(year=2024, perspective="batter")
    assert_series_not_equal(df1["player_id"], df2["player_id"])
    df3 = pyb.statcast_expected_stats_leaderboard(year=2024, perspective="batter-team")
    assert df3.shape[1] == 18
    assert df3.shape[0] == 30
    assert df3["team_id"].n_unique() == 30
    df4 = pyb.statcast_expected_stats_leaderboard(year=2024, perspective="pitcher-team")
    assert df4.shape[1] == 18
    assert df4.shape[0] == 30
    assert df4["team_id"].n_unique() == 30


def test_statcast_arsenal_stats_leaderboard_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenal_stats_leaderboard(year=None)
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenal_stats_leaderboard(year=2014)
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenal_stats_leaderboard(year=2024, min_pa=0)
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenal_stats_leaderboard(
            year=2024, perspective="individual"
        )


def test_statcast_arsenal_stats_leaderboard_regular():
    df = pyb.statcast_pitch_arsenal_stats_leaderboard(year=2024)
    assert df.shape[0] == 410
    assert df.shape[1] == 20
    assert df["player_id"].n_unique() == 257
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_pitch_arsenal_stats_leaderboard(year=2024, return_pandas=True)
    assert df2.shape[0] == 410
    assert df2.shape[1] == 20
    assert df2["player_id"].nunique() == 257
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_arsenal_stats_leaderboard_diffperspectives():
    df1 = pyb.statcast_pitch_arsenal_stats_leaderboard(year=2024, perspective="pitcher")
    assert df1.shape[0] == 582
    assert df1.shape[1] == 20
    assert type(df1) is pl.DataFrame
    df2 = pyb.statcast_pitch_arsenal_stats_leaderboard(year=2024, perspective="batter")
    assert_series_not_equal(df1["player_id"], df2["player_id"])


def test_statcast_arsenal_stats_leaderboard_diffminpa():
    df = pyb.statcast_pitch_arsenal_stats_leaderboard(year=2024, min_pa=200)
    assert df.shape[0] == 39
    assert df.shape[1] == 20
    assert df["player_id"].n_unique() == 39
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_pitch_arsenal_stats_leaderboard(year=2024, min_pa=100)
    assert df2.shape[0] > df.shape[0]
    assert df2.shape[1] == 20
    assert df2["player_id"].n_unique() > df["player_id"].n_unique()
    assert type(df2) is pl.DataFrame


def test_statcast_pitch_arsenals_leaderboard_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenals_leaderboard(year=None)
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenals_leaderboard(year=2014)
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenals_leaderboard(year=2024, min_pitches=0)
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenals_leaderboard(year=2024, hand="Righty")


def test_statcast_pitch_arsenals_leaderboard_regular():
    df = pyb.statcast_pitch_arsenals_leaderboard(year=2024)
    print(df.columns)
    assert df.shape[0] == 712
    assert df.shape[1] == 32
    assert df["pitcher"].n_unique() == 712

    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_pitch_arsenals_leaderboard(year=2024, return_pandas=True)
    assert df2.shape[0] == 712
    assert df2.shape[1] == 32
    assert df2["pitcher"].nunique() == 712
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_pitch_arsenals_leaderboard_diffminpitches():
    df = pyb.statcast_pitch_arsenals_leaderboard(year=2024, min_pitches=1000)
    assert df.shape[0] == 271
    assert df.shape[1] == 32
    assert df["pitcher"].n_unique() == 271
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_pitch_arsenals_leaderboard(year=2024, min_pitches=500)
    assert df2.shape[0] > df.shape[0]
    assert df2.shape[1] == 32
    assert df2["pitcher"].n_unique() > df["pitcher"].n_unique()
    assert type(df2) is pl.DataFrame


def test_statcast_pitch_arsenals_leaderboard_diffhandedness():
    df1 = pyb.statcast_pitch_arsenals_leaderboard(year=2024, hand="L")
    assert df1.shape[0] == 193
    assert df1.shape[1] == 32
    assert df1["pitcher"].n_unique() == 193
    assert type(df1) is pl.DataFrame
    df2 = pyb.statcast_pitch_arsenals_leaderboard(year=2024, hand="R")
    assert_series_not_equal(df1["pitcher"], df2["pitcher"])


def test_statcast_arm_strength_leaderboard_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_arm_strength_leaderboard(year=None)
    with pytest.raises(ValueError):
        pyb.statcast_arm_strength_leaderboard(year=2014)
    with pytest.raises(ValueError):
        pyb.statcast_arm_strength_leaderboard(year=2024, min_throws=0)
    with pytest.raises(ValueError):
        pyb.statcast_arm_strength_leaderboard(year=2024, perspective="individual")


def test_statcast_arm_strength_leaderboard_regular():
    df = pyb.statcast_arm_strength_leaderboard(year=2024)
    assert df.shape[0] == 388
    assert df.shape[1] == 26
    assert df["player_id"].n_unique() == 388
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_arm_strength_leaderboard(year=2024, return_pandas=True)
    assert df2.shape[0] == 388
    assert df2.shape[1] == 26
    assert df2["player_id"].nunique() == 388
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_arm_strength_leaderboard_diffminthrows():
    df = pyb.statcast_arm_strength_leaderboard(year=2024, min_throws=200)
    assert df.shape[0] == 264
    assert df.shape[1] == 26
    assert df["player_id"].n_unique() == 264
    assert df["total_throws"].min() >= 200
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_arm_strength_leaderboard(year=2024, min_throws=100)
    assert df2.shape[0] > df.shape[0]
    assert df2.shape[1] == 26
    assert df2["player_id"].n_unique() > df["player_id"].n_unique()
    assert df2["total_throws"].min() >= 100
    assert type(df2) is pl.DataFrame


def test_statcast_arm_strength_leaderboard_perspectives():
    df = pyb.statcast_arm_strength_leaderboard(year=2024, perspective="team")
    assert df.shape[0] == 30
    assert df.shape[1] == 26
    assert df["player_id"].unique().item() == 999999
    assert df["fielder_name"].unique().item() == "NA"
    assert type(df) is pl.DataFrame


def test_statcast_arm_value_leaderboard_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_arm_value_leaderboard(start_year=None, end_year=2024)
    with pytest.raises(ValueError):
        pyb.statcast_arm_value_leaderboard(start_year=2024, end_year=None)
    with pytest.raises(ValueError):
        pyb.statcast_arm_value_leaderboard(start_year=2015, end_year=2024)
    with pytest.raises(ValueError):
        pyb.statcast_arm_value_leaderboard(start_year=2024, end_year=2020)
    with pytest.raises(ValueError):
        pyb.statcast_arm_value_leaderboard(
            start_year=2022, end_year=2024, perspective="individual"
        )
    with pytest.raises(ValueError):
        pyb.statcast_arm_value_leaderboard(
            start_year=2022, end_year=2024, min_oppurtunities=0
        )
    with pytest.raises(ValueError):
        pyb.statcast_arm_value_leaderboard(
            start_year=2022, end_year=2024, min_oppurtunities="qualified"
        )


def test_statcast_arm_value_leaderboard_regular():
    df = pyb.statcast_arm_value_leaderboard(start_year=2022, end_year=2023)
    assert df.shape[0] == 146
    assert df.shape[1] == 20
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_arm_value_leaderboard(
        start_year=2022, end_year=2023, return_pandas=True
    )
    assert df2.shape == df.shape
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_arm_value_leaderboard_diffminopps():
    df = pyb.statcast_arm_value_leaderboard(
        start_year=2022, end_year=2023, min_oppurtunities=50
    )
    assert df.shape[0] == 263
    assert df.shape[1] == 20
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_arm_value_leaderboard(
        start_year=2022, end_year=2023, min_oppurtunities=10
    )
    assert df2.shape[0] > df.shape[0]
    assert df2.shape[1] == df.shape[1]
    assert type(df2) is pl.DataFrame


def test_statcast_arm_value_leaderboard_diffperspectives():
    df1 = pyb.statcast_arm_value_leaderboard(
        start_year=2022, end_year=2023, perspective="Fld"
    )
    assert df1.shape[0] == 146
    assert type(df1) is pl.DataFrame

    df2 = pyb.statcast_arm_value_leaderboard(
        start_year=2022, end_year=2023, perspective="Pit"
    )
    assert type(df2) is pl.DataFrame
    # Different data between fielders and pitchers
    if "fielder_id" in df1.columns and "fielder_id" in df2.columns:
        assert_series_not_equal(df1["fielder_id"], df2["fielder_id"])

    df3 = pyb.statcast_arm_value_leaderboard(
        start_year=2022, end_year=2023, perspective="Pitching+Team"
    )
    assert df3.shape[0] <= 30  # Should have at most 30 teams
    assert type(df3) is pl.DataFrame


def test_statcast_arm_value_leaderboard_splityears():
    df1 = pyb.statcast_arm_value_leaderboard(
        start_year=2022, end_year=2023, split_years=False
    )
    assert type(df1) is pl.DataFrame

    df2 = pyb.statcast_arm_value_leaderboard(
        start_year=2022, end_year=2023, split_years=True
    )
    assert type(df2) is pl.DataFrame

    # With split years enabled, we should have a column indicating the year
    # and potentially more rows since players are tracked per year
    assert "year" in df2.columns or "season" in df2.columns
    # Should have more rows with split years than aggregated data
    assert df2.shape[0] > df1.shape[0]


def test_statcast_catcher_blocking_leaderboard_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_catcher_blocking_leaderboard(start_year=None, end_year=2024)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_blocking_leaderboard(start_year=2024, end_year=None)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_blocking_leaderboard(start_year=2017, end_year=2024)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_blocking_leaderboard(start_year=2024, end_year=2020)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_blocking_leaderboard(
            start_year=2022, end_year=2024, perspective="individual"
        )
    with pytest.raises(ValueError):
        pyb.statcast_catcher_blocking_leaderboard(
            start_year=2022, end_year=2024, min_pitches=0
        )
    with pytest.raises(ValueError):
        pyb.statcast_catcher_blocking_leaderboard(
            start_year=2022, end_year=2024, min_pitches="qualified"
        )


def test_statcast_catcher_blocking_leaderboard_regular():
    df = pyb.statcast_catcher_blocking_leaderboard(start_year=2022, end_year=2023)
    assert df.shape[0] == 70
    assert df.shape[1] == 17
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_catcher_blocking_leaderboard(
        start_year=2022, end_year=2023, return_pandas=True
    )
    assert df2.shape == df.shape
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_catcher_blocking_leaderboard_diffminpitches():
    df = pyb.statcast_catcher_blocking_leaderboard(
        start_year=2022, end_year=2023, min_pitches=500
    )
    assert df.shape[0] == 105
    assert df.shape[1] == 17
    assert type(df) is pl.DataFrame
    df2 = pyb.statcast_catcher_blocking_leaderboard(
        start_year=2022, end_year=2023, min_pitches=100
    )
    assert df2.shape[0] > df.shape[0]
    assert type(df2) is pl.DataFrame


def test_statcast_catcher_blocking_leaderboard_diffperspectives():
    df1 = pyb.statcast_catcher_blocking_leaderboard(
        start_year=2022, end_year=2023, perspective="Cat"
    )
    assert df1.shape[0] == 70
    assert type(df1) is pl.DataFrame

    df2 = pyb.statcast_catcher_blocking_leaderboard(
        start_year=2022, end_year=2023, perspective="Pit"
    )
    assert type(df2) is pl.DataFrame

    df3 = pyb.statcast_catcher_blocking_leaderboard(
        start_year=2022, end_year=2023, perspective="Pitching+Team"
    )
    assert df3.shape[0] <= 30  # Should have at most 30 teams
    assert type(df3) is pl.DataFrame

    df4 = pyb.statcast_catcher_blocking_leaderboard(
        start_year=2022, end_year=2023, perspective="League"
    )
    assert df4.shape[0] == 1
    assert type(df4) is pl.DataFrame


def test_statcast_catcher_framing_leaderboard_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_catcher_framing_leaderboard(year=None)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_framing_leaderboard(year=2014)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_framing_leaderboard(year=2026)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_framing_leaderboard(
            year=2024, min_pitches_called="qualified"
        )
    with pytest.raises(ValueError):
        pyb.statcast_catcher_framing_leaderboard(year=2024, min_pitches_called=0)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_framing_leaderboard(year=2024, perspective="individual")


def test_statcast_catcher_framing_leaderboard_regular():
    df = pyb.statcast_catcher_framing_leaderboard(year=2023)
    assert df.shape[0] == 65
    assert df.shape[1] == 15
    assert type(df) is pl.DataFrame

    df2 = pyb.statcast_catcher_framing_leaderboard(year=2023, return_pandas=True)
    assert df2.shape[0] == df.shape[0]
    assert df2.shape[1] == df.shape[1]
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_catcher_framing_leaderboard_diffminpitches():
    df = pyb.statcast_catcher_framing_leaderboard(year=2023, min_pitches_called="q")
    assert df.shape[0] == 65
    assert type(df) is pl.DataFrame

    df2 = pyb.statcast_catcher_framing_leaderboard(year=2023, min_pitches_called=1000)
    assert df2.shape[0] == 62
    assert type(df2) is pl.DataFrame

    df3 = pyb.statcast_catcher_framing_leaderboard(year=2023, min_pitches_called=500)
    assert df3.shape[0] > df2.shape[0]
    assert type(df3) is pl.DataFrame


def test_statcast_catcher_framing_leaderboard_diffperspectives():
    df1 = pyb.statcast_catcher_framing_leaderboard(year=2023, perspective="catcher")
    assert df1.shape[0] > 0
    assert type(df1) is pl.DataFrame

    df2 = pyb.statcast_catcher_framing_leaderboard(year=2023, perspective="pitcher")
    assert type(df2) is pl.DataFrame

    df3 = pyb.statcast_catcher_framing_leaderboard(year=2023, perspective="batter")
    assert type(df3) is pl.DataFrame

    df4 = pyb.statcast_catcher_framing_leaderboard(
        year=2023, perspective="fielding_team"
    )
    assert type(df4) is pl.DataFrame
    assert df4.shape[0] <= 30  # Should have at most 30 teams

    df5 = pyb.statcast_catcher_framing_leaderboard(
        year=2023, perspective="batting_team"
    )
    assert type(df5) is pl.DataFrame
    assert df5.shape[0] <= 30  # Should have at most 30 teams


def test_statcast_catcher_framing_leaderboard_all_years():
    df = pyb.statcast_catcher_framing_leaderboard(year=0, min_pitches_called=200)
    assert df.shape[0] == 232
    assert type(df) is pl.DataFrame
    # All years should have more data than a single year
    df2 = pyb.statcast_catcher_framing_leaderboard(year=2023, min_pitches_called=200)
    assert df.shape[0] > df2.shape[0]


def test_statcast_catcher_pop_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_catcher_poptime_leaderboard(year=None)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_poptime_leaderboard(year=2014)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_poptime_leaderboard(year=2024, min_2b_attempts=-1)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_poptime_leaderboard(year=2024, min_3b_attempts=-1)


def test_statcast_catcher_pop_regular():
    df = pyb.statcast_catcher_poptime_leaderboard(year=2024)
    assert df.shape[0] == 83
    assert df.shape[1] == 14
    assert type(df) is pl.DataFrame

    df2 = pyb.statcast_catcher_poptime_leaderboard(year=2024, return_pandas=True)
    assert df2.shape[0] == df.shape[0]
    assert df2.shape[1] == df.shape[1]
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_catcher_pop_custom_attempts():
    df1 = pyb.statcast_catcher_poptime_leaderboard(year=2024, min_2b_attempts=50)
    assert df1.shape[0] == 15
    assert df1.shape[1] == 14
    assert df1.select(pl.col("pop_2b_sba_count")).min().item() >= 50
    assert type(df1) is pl.DataFrame
    df2 = pyb.statcast_catcher_poptime_leaderboard(year=2024, min_3b_attempts=6)
    assert df2.shape[0] == 8
    assert df2.shape[1] == 14
    assert df2.select(pl.col("pop_3b_sba_count")).min().item() >= 6
    assert type(df2) is pl.DataFrame


def test_statcast_outfield_catch_prob_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_outfield_catch_probability_leaderboard(year=None)
    with pytest.raises(ValueError):
        pyb.statcast_outfield_catch_probability_leaderboard(year=2014)
    with pytest.raises(ValueError):
        pyb.statcast_outfield_catch_probability_leaderboard(year="NOT_ALL")
    with pytest.raises(ValueError):
        pyb.statcast_outfield_catch_probability_leaderboard(
            year=2024, min_opportunities=-1
        )
    with pytest.raises(ValueError):
        pyb.statcast_outfield_catch_probability_leaderboard(
            year=2024, min_opportunities="Qualified"
        )


def test_statcast_outfield_catch_prob_regular():
    df = pyb.statcast_outfield_catch_probability_leaderboard(
        year=2024, min_opportunities="q"
    )
    assert df.shape[0] == 102
    assert df.shape[1] == 18
    assert type(df) is pl.DataFrame
    assert df["player_id"].n_unique() == 102
    df2 = pyb.statcast_outfield_catch_probability_leaderboard(
        year=2024, min_opportunities="q", return_pandas=True
    )
    assert df2.shape[0] == df.shape[0]
    assert df2.shape[1] == df.shape[1]
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))
    df3 = pyb.statcast_outfield_catch_probability_leaderboard(
        year=2024, min_opportunities=25
    )
    assert df3.shape[0] == 214
    assert df3.shape[1] == df.shape[1]


def test_statcast_oaa_leaderboard_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_outsaboveaverage_leaderboard(start_year=None, end_year=2020)
    with pytest.raises(ValueError):
        pyb.statcast_outsaboveaverage_leaderboard(start_year=2020, end_year=None)
    with pytest.raises(ValueError):
        pyb.statcast_outsaboveaverage_leaderboard(start_year=2015, end_year=2020)
    with pytest.raises(ValueError):
        pyb.statcast_outsaboveaverage_leaderboard(start_year=2020, end_year=2015)
    with pytest.raises(ValueError):
        pyb.statcast_outsaboveaverage_leaderboard(
            start_year=2020, end_year=2020, perspective="individual"
        )
    with pytest.raises(ValueError):
        pyb.statcast_outsaboveaverage_leaderboard(
            start_year=2020, end_year=2020, min_opportunities=0
        )
    with pytest.raises(ValueError):
        pyb.statcast_outsaboveaverage_leaderboard(
            start_year=2020, end_year=2020, min_opportunities="qualified"
        )


def test_statcast_oaa_leaderboard_regular():
    df = pyb.statcast_outsaboveaverage_leaderboard(start_year=2024, end_year=2024)
    assert df.shape[0] == 274
    assert df.shape[1] == 16
    assert type(df) is pl.DataFrame
    assert df["player_id"].n_unique() == 274
    assert df["year"].n_unique() == 1
    df2 = pyb.statcast_outsaboveaverage_leaderboard(
        start_year=2024, end_year=2024, return_pandas=True
    )
    assert df2.shape[0] == df.shape[0]
    assert df2.shape[1] == df.shape[1]
    assert type(df2) is pd.DataFrame
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))
    df3 = pyb.statcast_outsaboveaverage_leaderboard(
        start_year=2024, end_year=2024, min_opportunities=25
    )
    assert df3.shape[0] > df.shape[0]
    assert df3.shape[1] == df.shape[1]
    assert type(df3) is pl.DataFrame


def test_statcast_oaa_leaderboard_perspectives():
    df = pyb.statcast_outsaboveaverage_leaderboard(
        start_year=2024, end_year=2024, perspective="Fielding_Team"
    )
    assert df.shape[0] == 30
    assert df.shape[1] == 14
    assert type(df) is pl.DataFrame
    assert df["team_id"].n_unique() == 30


def test_statcast_oaa_leaderboard_splityears():
    df = pyb.statcast_outsaboveaverage_leaderboard(
        start_year=2023, end_year=2024, split_years=True
    )
    assert df.shape[0] == 529
    assert df.shape[1] == 16
    assert type(df) is pl.DataFrame
    assert "year" in df.columns
    assert df["year"].n_unique() == 2


def test_statcast_baserunning_rv_leaderboard_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_baserunning_run_value_leaderboard(start_year=None, end_year=2020)
    with pytest.raises(ValueError):
        pyb.statcast_baserunning_run_value_leaderboard(start_year=2020, end_year=None)
    with pytest.raises(ValueError):
        pyb.statcast_baserunning_run_value_leaderboard(start_year=2015, end_year=2020)
    with pytest.raises(ValueError):
        pyb.statcast_baserunning_run_value_leaderboard(start_year=2020, end_year=2015)
    with pytest.raises(ValueError):
        pyb.statcast_baserunning_run_value_leaderboard(start_year=2024, end_year=2023)
    with pytest.raises(ValueError):
        pyb.statcast_baserunning_run_value_leaderboard(
            start_year=2020, end_year=2020, perspective="individual"
        )
    with pytest.raises(ValueError):
        pyb.statcast_baserunning_run_value_leaderboard(
            start_year=2020, end_year=2020, min_oppurtunities=0
        )
    with pytest.raises(ValueError):
        pyb.statcast_baserunning_run_value_leaderboard(
            start_year=2020, end_year=2020, min_oppurtunities="qualified"
        )


def test_statcast_baserunning_leaderboard_regular():
    df = pyb.statcast_baserunning_run_value_leaderboard(start_year=2024, end_year=2024)
    assert df is not None
    assert type(df) is pl.DataFrame
    assert df.shape[0] == 193
    assert df.shape[1] == 18
    assert df.select(pl.col("player_id").n_unique()).item() == 193
    assert df.select(pl.col("start_year").unique()).item() == 2024
    assert df.select(pl.col("end_year").unique()).item() == 2024
    df2 = pyb.statcast_baserunning_run_value_leaderboard(
        start_year=2024, end_year=2024, perspective="Run", return_pandas=True
    )
    assert df2 is not None
    assert type(df2) is pd.DataFrame
    assert df2.shape[0] == 193
    assert df2.shape[1] == 18
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_baserunning_leaderboard_perspectives():
    df = pyb.statcast_baserunning_run_value_leaderboard(
        start_year=2024, end_year=2024, perspective="League"
    )
    assert df.shape[0] == 1
    assert df.shape[1] == 18
    assert type(df) is pl.DataFrame
    assert df.select(pl.col("player_id").first()).item() == 999999
    assert df.select(pl.col("entity_name").first()).item() == "League"
    assert df.select(pl.col("team_name").first()).item() == "League"

    df2 = pyb.statcast_baserunning_run_value_leaderboard(
        start_year=2024, end_year=2024, perspective="Batting+Team"
    )
    assert df2.shape[0] == 30
    assert df2.shape[1] == 18
    assert type(df2) is pl.DataFrame
    assert df2.select(pl.col("entity_name").n_unique()).item() == 30
    assert df2.select(pl.col("team_name").n_unique()).item() == 30
    assert df2.select(pl.col("player_id").n_unique()).item() == 30

    df3 = pyb.statcast_baserunning_run_value_leaderboard(
        start_year=2024, end_year=2024, perspective="Pitching+Team"
    )
    assert df3.shape[0] == 30
    assert df3.shape[1] == 18
    assert type(df3) is pl.DataFrame
    assert df3.select(pl.col("entity_name").n_unique()).item() == 30
    assert df3.select(pl.col("team_name").n_unique()).item() == 30
    assert df3.select(pl.col("player_id").n_unique()).item() == 30


def test_statcast_baserunning_leaderboard_min_opps():
    df = pyb.statcast_baserunning_run_value_leaderboard(
        start_year=2024, end_year=2024, min_oppurtunities=100
    )
    assert df is not None
    assert type(df) is pl.DataFrame
    assert df.shape[0] == 6
    assert df.shape[1] == 18
    assert df.select(pl.col("player_id").n_unique()).item() == 6
    assert df.select(pl.col("N_runner_moved").min()).item() >= 100


def test_basestealing_rv_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_basestealing_runvalue_leaderboard(start_year=None, end_year=2020)
    with pytest.raises(ValueError):
        pyb.statcast_basestealing_runvalue_leaderboard(start_year=2020, end_year=None)
    with pytest.raises(ValueError):
        pyb.statcast_basestealing_runvalue_leaderboard(start_year=2015, end_year=2020)
    with pytest.raises(ValueError):
        pyb.statcast_basestealing_runvalue_leaderboard(start_year=2020, end_year=2015)
    with pytest.raises(ValueError):
        pyb.statcast_basestealing_runvalue_leaderboard(
            start_year=2024, end_year=2024, min_sb_oppurtunities=0
        )
    with pytest.raises(ValueError):
        pyb.statcast_basestealing_runvalue_leaderboard(
            start_year=2024, end_year=2024, min_sb_oppurtunities="qualified"
        )
    with pytest.raises(ValueError):
        pyb.statcast_basestealing_runvalue_leaderboard(
            start_year=2024, end_year=2024, pitch_hand="Lefty"
        )
    with pytest.raises(ValueError):
        pyb.statcast_basestealing_runvalue_leaderboard(
            start_year=2024, end_year=2024, runner_movement="stolen_base"
        )
    with pytest.raises(ValueError):
        pyb.statcast_basestealing_runvalue_leaderboard(
            start_year=2024, end_year=2024, target_base="second"
        )
    with pytest.raises(ValueError):
        pyb.statcast_basestealing_runvalue_leaderboard(
            start_year=2024, end_year=2024, perspective="individual"
        )


def test_statcast_basestealing_rv_leaderboard_regular():
    df = pyb.statcast_basestealing_runvalue_leaderboard(start_year=2024, end_year=2024)
    assert df is not None
    assert type(df) is pl.DataFrame
    assert df.shape[0] == 434
    assert df.shape[1] == 24
    assert df.select(pl.col("player_id").n_unique()).item() == 434

    df2 = pyb.statcast_basestealing_runvalue_leaderboard(
        start_year=2024, end_year=2024, return_pandas=True
    )
    assert df2 is not None
    assert type(df2) is pd.DataFrame
    assert df2.shape[0] == 434
    assert df2.shape[1] == 24
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_basestealing_rv_leaderboard_min_sb_opp():
    df = pyb.statcast_basestealing_runvalue_leaderboard(
        start_year=2024, end_year=2024, min_sb_oppurtunities=50
    )
    assert df is not None
    assert type(df) is pl.DataFrame
    assert df.shape[0] == 543
    assert df.shape[1] == 24
    assert df.select(pl.col("player_id").n_unique()).item() == 543
    assert df.select(pl.col("n_init").min()).item() >= 50


def test_statcast_basestealing_rv_leaderboard_runner_movement():
    df = pyb.statcast_basestealing_runvalue_leaderboard(
        start_year=2024, end_year=2024, runner_movement="Advance"
    )
    assert df is not None
    assert type(df) is pl.DataFrame
    assert df.shape[0] == 361
    assert df.shape[1] == 24
    assert df.select(pl.col("player_id").n_unique()).item() == 361
    assert df.select(pl.col("n_cs").n_unique()).item() == 1
    assert df.select(pl.col("n_cs").unique()).item() == 0
    assert df.select(pl.col("n_pk").n_unique()).item() == 1
    assert df.select(pl.col("n_pk").unique()).item() == 0

    df2 = pyb.statcast_basestealing_runvalue_leaderboard(
        start_year=2024, end_year=2024, runner_movement="Out"
    )
    assert df2 is not None
    assert type(df2) is pl.DataFrame
    assert df.shape[0] == 275
    assert df.shape[1] == 24
    assert df.select(pl.col("player_id").n_unique()).item() == 275
    assert df.select(pl.col("n_sb").n_unique()).item() == 1
    assert df.select(pl.col("n_sb").unique()).item() == 0

    df3 = pyb.statcast_basestealing_runvalue_leaderboard(
        start_year=2024, end_year=2024, runner_movement="Hold"
    )
    assert df3 is not None
    assert type(df3) is pl.DataFrame
    assert df.shape[0] == 434
    assert df.shape[1] == 24
    assert df.select(pl.col("player_id").n_unique()).item() == 434
    assert df.select(pl.col("n_sb").n_unique()).item() == 1
    assert df.select(pl.col("n_sb").unique()).item() == 0
