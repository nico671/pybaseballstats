import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pandas as pd
import polars as pl
import pytest
from polars.testing import assert_frame_equal, assert_series_not_equal

import pybaseballstats as pyb

START_DT = "2023-04-01"
END_DT = "2023-04-02"


def test_statcast_date_range_pitch_by_pitch_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast.statcast_date_range_pitch_by_pitch(
            start_date=START_DT, end_date=END_DT, perspective="invalid"
        )
    with pytest.raises(ValueError):
        pyb.statcast.statcast_date_range_pitch_by_pitch(
            start_date=None, end_date=END_DT
        )
    with pytest.raises(ValueError):
        pyb.statcast.statcast_date_range_pitch_by_pitch(
            start_date=START_DT, end_date=None
        )
    with pytest.raises(ValueError):
        pyb.statcast.statcast_date_range_pitch_by_pitch(
            start_date=END_DT, end_date=START_DT, return_pandas=None
        )


def test_statcast_date_range_pitch_by_pitch_regular():
    df = pyb.statcast.statcast_date_range_pitch_by_pitch(
        start_date=START_DT, end_date=END_DT
    )
    assert df is not None
    assert isinstance(df, pl.LazyFrame)
    df = df.collect()
    assert df is not None
    assert df.shape == (8695, 113)
    assert df.select(pl.col("game_date").max()).item() == "2023-04-02"
    assert df.select(pl.col("game_date").min()).item() == "2023-04-01"
    df2 = pyb.statcast.statcast_date_range_pitch_by_pitch(
        start_date=START_DT, end_date=END_DT, return_pandas=True
    )
    assert df2 is not None
    assert isinstance(df2, pd.DataFrame)
    assert df2.shape == (8695, 113)
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_statcast_date_range_pitch_by_pitch_perspective():
    df = pyb.statcast.statcast_date_range_pitch_by_pitch(
        start_date=START_DT, end_date=END_DT, perspective="pitcher"
    )
    df2 = pyb.statcast.statcast_date_range_pitch_by_pitch(
        start_date=START_DT, end_date=END_DT, perspective="batter"
    )
    assert df is not None
    assert df2 is not None
    assert isinstance(df, pl.LazyFrame)
    assert isinstance(df2, pl.LazyFrame)
    df = df.collect()
    df2 = df2.collect()
    assert df.shape == df2.shape
    assert df.schema == df2.schema
    assert (
        df.select(pl.col("game_date").max()).item()
        == df2.select(pl.col("game_date").max()).item()
    )
    assert (
        df.select(pl.col("game_date").min()).item()
        == df2.select(pl.col("game_date").min()).item()
    )
    assert_series_not_equal(
        df.select(pl.col("player_name")).to_series(),
        df2.select(pl.col("player_name")).to_series(),
    )
