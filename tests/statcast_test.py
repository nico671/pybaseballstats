import os
import sys

import pandas as pd
import polars as pl
from polars.testing import assert_frame_equal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb

START_DT = "2024-04-01"
END_DT = "2024-04-10"


## statcast_date_range_pitch_by_pitch_TESTS
def test_statcast_date_range_pitch_by_pitch():
    data = pyb.statcast.statcast_date_range_pitch_by_pitch(
        start_dt=START_DT,
        end_dt=END_DT,
        return_pandas=False,
        extra_stats=False,
    )
    assert type(data) is pl.LazyFrame
    data = data.collect()
    assert data is not None
    assert data.shape[0] == 38213
    assert data.shape[1] == 113
    assert data.select(pl.col("game_date").min()).to_series().to_list()[0] == START_DT
    assert data.select(pl.col("game_date").max()).to_series().to_list()[0] == END_DT
    assert type(data) is pl.DataFrame


def test_statcast_date_range_pitch_by_pitch_extra_stats():
    data = pyb.statcast.statcast_date_range_pitch_by_pitch(
        start_dt=START_DT,
        end_dt=END_DT,
        return_pandas=False,
        extra_stats=True,
    ).collect()
    assert data is not None
    assert data.shape[0] == 38213
    assert data.shape[1] == 249
    assert data.select(pl.col("game_date").min()).to_series().to_list()[0] == START_DT
    assert data.select(pl.col("game_date").max()).to_series().to_list()[0] == END_DT
    assert type(data) is pl.DataFrame


def test_statcast_date_range_pitch_by_pitch_return_pandas():
    data = pyb.statcast.statcast_date_range_pitch_by_pitch(
        start_dt=START_DT,
        end_dt=END_DT,
        return_pandas=True,
        extra_stats=False,
    )
    assert data is not None
    assert data.shape[0] == 38213
    assert data.shape[1] == 113
    assert type(data) is pd.DataFrame


def test_statcast_date_range_pitch_by_pitch_flipped_dates():
    df = pyb.statcast.statcast_date_range_pitch_by_pitch(
        start_dt=END_DT,
        end_dt=START_DT,
        return_pandas=False,
        extra_stats=False,
    )
    assert df is not None
    assert df.collect().shape == (0, 0)


def test_statcast_date_range_pitch_by_pitch_null_dates():
    df = pyb.statcast.statcast_date_range_pitch_by_pitch(
        start_dt=None,
        end_dt=None,
        return_pandas=False,
        extra_stats=False,
    )
    assert df is not None
    assert df.collect().shape == (0, 0)


def test_statcast_date_range_pitch_by_pitch_with_team():
    data = pyb.statcast.statcast_date_range_pitch_by_pitch(
        start_dt=START_DT,
        end_dt=END_DT,
        team="WSH",
        extra_stats=False,
        return_pandas=False,
    )
    assert isinstance(data, pl.LazyFrame)
    data = data.collect()
    assert isinstance(data, pl.DataFrame)
    assert data.shape[1] == 113


def test_statcast_batter():
    data = pyb.statcast.statcast_single_batter_range_pitch_by_pitch(
        start_dt=START_DT,
        end_dt=END_DT,
        player_id="547180",
        extra_stats=True,
        return_pandas=False,
    )
    assert isinstance(data, pl.LazyFrame)
    data = data.collect()
    assert isinstance(data, pl.DataFrame)
    assert data.shape[1] == 181
    assert data.shape[0] == 144
    assert len(data.select("batter").unique()) == 1
    assert data["batter"].unique().item() == 547180
    assert data.select(pl.col("game_date").min()).to_series().to_list()[0] == START_DT
    assert data.select(pl.col("game_date").max()).to_series().to_list()[0] == END_DT
    data = pyb.statcast.statcast_single_batter_range_pitch_by_pitch(
        start_dt=START_DT,
        end_dt=END_DT,
        player_id="547180",
        extra_stats=False,
        return_pandas=False,
    )
    assert isinstance(data, pl.LazyFrame)
    data = data.collect()
    assert isinstance(data, pl.DataFrame)
    assert data.shape[1] == 113
    assert data.shape[0] == 144
    assert len(data.select("batter").unique()) == 1


def test_statcast_pitcher():
    data = pyb.statcast.statcast_single_pitcher_range_pitch_by_pitch(
        start_dt=START_DT,
        end_dt=END_DT,
        player_id="671096",
        extra_stats=True,
        return_pandas=False,
    )
    assert isinstance(data, pl.LazyFrame)
    data = data.collect()
    assert isinstance(data, pl.DataFrame)
    assert data.shape[1] == 181
    assert data.shape[0] == 185
    assert len(data.select("pitcher").unique()) == 1


def test_statcast_pitcher_to_pandas():
    data1 = pyb.statcast.statcast_single_pitcher_range_pitch_by_pitch(
        start_dt=START_DT,
        end_dt=END_DT,
        player_id="671096",
        extra_stats=True,
        return_pandas=True,
    )
    assert isinstance(data1, pd.DataFrame)
    assert data1.shape[1] == 181
    assert data1.shape[0] == 185
    assert len(data1["pitcher"].unique()) == 1
    data2 = pyb.statcast.statcast_single_pitcher_range_pitch_by_pitch(
        start_dt=START_DT,
        end_dt=END_DT,
        player_id="671096",
        extra_stats=True,
        return_pandas=False,
    )
    data2 = data2.collect()
    assert isinstance(data2, pl.DataFrame)
    assert data2.shape[1] == 181
    assert data2.shape[0] == 185
    assert len(data2["pitcher"].unique()) == 1
    assert_frame_equal(pl.DataFrame(data1, schema=data2.schema), data2)
