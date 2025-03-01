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
