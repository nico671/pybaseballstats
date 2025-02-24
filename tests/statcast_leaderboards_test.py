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
