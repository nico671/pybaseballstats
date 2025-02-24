# statcast_bat_tracking
import pandas as pd
import polars as pl
import pytest
from polars.testing import assert_frame_equal, assert_frame_not_equal

import pybaseballstats as pyb


def test_statcast_bat_tracking_bad_inputs():
    # out of order dates, either year < 2023, pitcher_batter not in ['batter', 'pitcher'], end or start is None
    with pytest.raises(ValueError):
        pyb.statcast_bat_tracking("2022-01-01", "2023-01-01", "batter")
    with pytest.raises(ValueError):
        pyb.statcast_bat_tracking("2023-01-01", "2022-01-01", "batter")
    with pytest.raises(ValueError):
        pyb.statcast_bat_tracking(None, "2024-01-01", "batter")
    with pytest.raises(ValueError):
        pyb.statcast_bat_tracking("2023-01-01", None, "batter")
    with pytest.raises(ValueError):
        pyb.statcast_bat_tracking("2023-01-01", "2024-01-01", "not_batter_or_pitcher")


def test_statcast_bat_tracking_normal():
    data1 = pyb.statcast_bat_tracking("2024-07-01", "2024-08-01", "batter")
    assert type(data1) is pl.DataFrame
    assert data1.shape[0] == 208
    assert data1.shape[1] == 18
    data2 = pyb.statcast_bat_tracking("2024-07-01", "2024-08-01", "batter")
    assert type(data2) is pl.DataFrame
    assert_frame_equal(data1, data2)


def test_statcast_bat_tracking_diff_perspectives():
    data1 = pyb.statcast_bat_tracking("2024-07-01", "2024-08-01", "batter")
    data2 = pyb.statcast_bat_tracking("2024-07-01", "2024-08-01", "pitcher")
    assert data1.shape[0] == 208
    assert data2.shape[0] == 198
    assert data1.shape[1] == data2.shape[1]
    assert_frame_not_equal(data1, data2)


def test_statcast_bat_tracking_to_pandas():
    data = pyb.statcast_bat_tracking("2024-07-01", "2024-08-01", "batter", True)
    assert type(data) is pd.DataFrame
    assert data.shape[0] == 208
    assert data.shape[1] == 18
    data2 = pyb.statcast_bat_tracking("2024-07-01", "2024-08-01", "batter", False)
    assert_frame_equal(pl.DataFrame(data, schema=data2.schema), data2)


# statcast_exit_velo_barrels
def test_statcast_exit_velo_barrels_bad_inputs():
    # out of order dates, either year < 2015, end or start is None
    with pytest.raises(ValueError):
        pyb.statcast_exit_velo_barrels(2014, "batter", False)
    with pytest.raises(ValueError):
        pyb.statcast_exit_velo_barrels(None, "batter", False)
    with pytest.raises(ValueError):
        pyb.statcast_exit_velo_barrels(2015, None, False)
    with pytest.raises(ValueError):
        pyb.statcast_exit_velo_barrels(2015, "not_batter_or_pitcher", False)


def test_statcast_exit_velo_barrels():
    data1 = pyb.statcast_exit_velo_barrels(2015, "batter", False)
    assert type(data1) is pl.DataFrame
    assert data1.shape[0] == 250
    assert data1.shape[1] == 18
    data2 = pyb.statcast_exit_velo_barrels(2015, "batter", False)
    assert type(data2) is pl.DataFrame
    assert_frame_equal(data1, data2)


def test_statcast_exit_velo_barrels_diff_perspectives():
    data1 = pyb.statcast_exit_velo_barrels(2015, "batter", False)
    data2 = pyb.statcast_exit_velo_barrels(2015, "pitcher", False)
    assert data1.shape[0] == 250
    assert data2.shape[0] == 340
    assert data1.shape[1] == data2.shape[1]
    assert_frame_not_equal(data1, data2)


def test_statcast_exit_velo_barrels_to_pandas():
    data = pyb.statcast_exit_velo_barrels(2015, "batter", True)
    assert type(data) is pd.DataFrame
    assert data.shape[0] == 250
    assert data.shape[1] == 18
    data2 = pyb.statcast_exit_velo_barrels(2015, "batter", False)
    assert_frame_equal(pl.DataFrame(data, schema=data2.schema), data2)


# expected_stats
def test_statcast_expected_stats_bad_inputs():
    # out of order dates, either year < 2015, end or start is None
    with pytest.raises(ValueError):
        pyb.statcast_expected_stats(2014, "batter", False)
    with pytest.raises(ValueError):
        pyb.statcast_expected_stats(None, "batter", False)
    with pytest.raises(ValueError):
        pyb.statcast_expected_stats(2015, None, False)
    with pytest.raises(ValueError):
        pyb.statcast_expected_stats(2015, "not_batter_or_pitcher", False)


def test_statcast_expected_stats():
    data1 = pyb.statcast_expected_stats(2015, "batter", False)
    assert type(data1) is pl.DataFrame
    assert data1.shape[0] == 250
    assert data1.shape[1] == 14
    data2 = pyb.statcast_expected_stats(2015, "batter", False)
    print(data1.columns)
    assert type(data2) is pl.DataFrame
    assert_frame_equal(data1, data2)


def test_statcast_expected_stats_pandas():
    data = pyb.statcast_expected_stats(2015, "batter", True)
    assert type(data) is pd.DataFrame
    assert data.shape[0] == 250
    assert data.shape[1] == 14
    data2 = pyb.statcast_expected_stats(2015, "batter", False)
    assert_frame_equal(pl.DataFrame(data, schema=data2.schema), data2)


# statcast_pitch_arsenal
def test_statcast_pitch_arsenal_bad_inputs():
    # out of order dates, either year < 2019, end or start is None
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenal(2014, "batter", False)
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenal(None, "batter", False)
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenal(2019, None, False)
    with pytest.raises(ValueError):
        pyb.statcast_pitch_arsenal(2019, "not_batter_or_pitcher", False)


def test_statcast_pitch_arsenal():
    data1 = pyb.statcast_pitch_arsenal(2019, "batter", False)
    assert type(data1) is pl.DataFrame
    assert data1.shape[0] == 178
    assert data1.shape[1] == 20
    data2 = pyb.statcast_pitch_arsenal(2019, "batter", False)
    assert type(data2) is pl.DataFrame
    assert_frame_equal(data1, data2)
    data3 = pyb.statcast_pitch_arsenal(2019, "pitcher", False)
    assert type(data3) is pl.DataFrame
    assert data3.shape[0] == 344
    assert data3.shape[1] == 20
    data4 = pyb.statcast_pitch_arsenal(2019, "pitcher", False)
    assert type(data4) is pl.DataFrame
    assert_frame_equal(data3, data4)
    assert_frame_not_equal(data1, data3)


# pitching active spin
def test_statcast_pitching_active_spin_bad_inputs():
    with pytest.raises(ValueError):
        pyb.statcast_pitching_active_spin(2016, False)
    with pytest.raises(ValueError):
        pyb.statcast_pitching_active_spin(None, False)


def test_statcast_pitching_active_spin():
    df = pyb.statcast_pitching_active_spin(2020, False)
    assert type(df) is pl.DataFrame
    assert df.shape[0] == 562
    assert df.shape[1] == 11
    df2 = pyb.statcast_pitching_active_spin(2020, False)
    assert type(df2) is pl.DataFrame
    assert_frame_equal(df, df2)
    df3 = pyb.statcast_pitching_active_spin(2021, False)
    assert type(df3) is pl.DataFrame
    assert df3.shape[0] == 733
    assert df3.shape[1] == 11
    assert_frame_not_equal(df, df3)


# statcast_pitching_arm_angle
def test_statcast_pitching_arm_angle_bad_inputs():
    # season < 2023, start_dt or end_dt < 2023, start_dt > end_dt, start_dt or end_dt is None
    with pytest.raises(ValueError):
        pyb.statcast_pitching_arm_angle("2022-01-01", "2023-01-01", None, False)
    with pytest.raises(ValueError):
        pyb.statcast_pitching_arm_angle("2023-01-01", "2022-01-01", None, False)
    with pytest.raises(ValueError):
        pyb.statcast_pitching_arm_angle(None, "2024-01-01", None, False)
    with pytest.raises(ValueError):
        pyb.statcast_pitching_arm_angle("2023-01-01", None, None, False)
    with pytest.raises(ValueError):
        pyb.statcast_pitching_arm_angle("2023-01-01", "2024-01-01", 2022, False)


def test_statcast_pitching_arm_angle():
    data1 = pyb.statcast_pitching_arm_angle("2024-07-01", "2024-08-01", None, False)
    assert type(data1) is pl.DataFrame
    assert data1.shape[0] == 268
    assert data1.shape[1] == 10
    data2 = pyb.statcast_pitching_arm_angle("2024-07-01", "2024-08-01", None, False)
    assert type(data2) is pl.DataFrame
    assert_frame_equal(data1, data2)


def test_statcast_pitching_arm_angle_with_season():
    data1 = pyb.statcast_pitching_arm_angle(None, None, 2024, False)
    assert type(data1) is pl.DataFrame
    assert data1.shape[0] == 284
    assert data1.shape[1] == 10
    data2 = pyb.statcast_pitching_arm_angle(None, None, 2024, False)
    assert type(data2) is pl.DataFrame
    assert_frame_equal(data1, data2)


def test_statcast_pitching_arm_angle_to_pandas():
    data = pyb.statcast_pitching_arm_angle("2024-07-01", "2024-08-01", None, True)
    assert type(data) is pd.DataFrame
    assert data.shape[0] == 268
    assert data.shape[1] == 10
    data2 = pyb.statcast_pitching_arm_angle("2024-07-01", "2024-08-01", None, False)
    assert_frame_equal(pl.DataFrame(data, schema=data2.schema), data2)


# statcast_arm_strength
# def test_statcast_arm_strength_bad_inputs():
#     with pytest.raises(ValueError):
#         pyb.statcast_arm_strength(2019, False)
#     with pytest.raises(ValueError):
#         pyb.statcast_arm_strength(None, False)


# def test_statcast_arm_strength():
#     data1 = pyb.statcast_arm_strength(2020, False)
#     assert type(data1) is pl.DataFrame
#     assert data1.shape[0] == 241
#     assert data1.shape[1] == 26
#     data2 = pyb.statcast_arm_strength(2020, False)
#     assert type(data2) is pl.DataFrame
#     assert_frame_equal(data1, data2)


# def test_statcast_arm_strength_to_pandas():
#     data = pyb.statcast_arm_strength(2020, True)
#     assert type(data) is pd.DataFrame
#     assert data.shape[0] == 241
#     assert data.shape[1] == 26
#     data2 = pyb.statcast_arm_strength(2020, False)
#     assert_frame_equal(pl.DataFrame(data, schema=data2.schema), data2)


# statcast_catcher_stats
def test_statcast_catcher_stats_bad_inputs():
    # start_season or end_season < 2018, start_season > end_season
    with pytest.raises(ValueError):
        pyb.statcast_catcher_stats(2017, 2018)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_stats(2018, 2017)
    with pytest.raises(ValueError):
        pyb.statcast_catcher_stats(2019, 2018)


def test_statcast_catcher_stats_single_season():
    data1 = pyb.statcast_catcher_stats(2018, 2018)
    assert type(data1) is pl.DataFrame
    assert data1.shape[0] == 60
    assert data1.shape[1] == 55
    data2 = pyb.statcast_catcher_stats(2018, 2018)
    assert_frame_equal(data1, data2)


def test_statcast_catcher_stats_multiple_seasons():
    data1 = pyb.statcast_catcher_stats(2018, 2020)
    assert type(data1) is pl.DataFrame
    assert data1.shape[0] == 85
    assert data1.shape[1] == 55
    data2 = pyb.statcast_catcher_stats(2018, 2020)
    assert_frame_equal(data1, data2)


def test_statcast_catcher_stats_to_pandas():
    data = pyb.statcast_catcher_stats(2018, 2018, True)
    assert type(data) is pd.DataFrame
    assert data.shape[0] == 60
    assert data.shape[1] == 55
    data2 = pyb.statcast_catcher_stats(2018, 2018, False)
    assert_frame_equal(pl.DataFrame(data, schema=data2.schema), data2)
