import os
import sys

import pandas as pd
import polars as pl
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb

START_DT = "2024-04-01"
END_DT = "2024-04-10"


def test_statcast_single_game_game_pk_not_correct():
    data = pyb.statcast_single_game(
        game_pk=100000000000, return_pandas=False, extra_stats=False
    ).collect()
    assert data is not None
    assert data.shape[0] == 0
    assert data.shape[1] == 113
    assert type(data) is pl.DataFrame


def test_statcast_single_game_game_pk_correct():
    data = pyb.statcast_single_game(game_pk=634, return_pandas=False, extra_stats=False)
    assert type(data) is pl.LazyFrame
    data = data.collect()
    assert data is not None
    assert data.shape[0] == 303
    assert data.shape[1] == 113
    assert type(data) is pl.DataFrame


def test_statcast_single_game_game_pk_correct_extra_stats():
    data = pyb.statcast_single_game(
        game_pk=634, return_pandas=False, extra_stats=True
    ).collect()
    assert data is not None
    assert data.shape[0] == 303
    assert data.shape[1] == 249
    assert type(data) is pl.DataFrame


## STATCAST_DATE_RANGE_TESTS
def test_statcast_date_range():
    data = pyb.statcast_date_range(
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
    assert type(data) is pl.DataFrame


def test_statcast_date_range_extra_stats():
    data = pyb.statcast_date_range(
        start_dt=START_DT,
        end_dt=END_DT,
        return_pandas=False,
        extra_stats=True,
    ).collect()
    assert data is not None
    assert data.shape[0] == 38213
    assert data.shape[1] == 249
    assert type(data) is pl.DataFrame


def test_statcast_date_range_return_pandas():
    data = pyb.statcast_date_range(
        start_dt=START_DT,
        end_dt=END_DT,
        return_pandas=True,
        extra_stats=False,
    )
    assert data is not None
    assert data.shape[0] == 38213
    assert data.shape[1] == 113
    assert type(data) is pd.DataFrame


def test_statcast_date_range_flipped_dates():
    with pytest.raises(ValueError):
        pyb.statcast_date_range(
            start_dt=END_DT,
            end_dt=START_DT,
            return_pandas=False,
            extra_stats=False,
        )


def test_statcast_date_range_null_dates():
    with pytest.raises(ValueError):
        pyb.statcast_date_range(
            start_dt=None,
            end_dt=None,
            return_pandas=False,
            extra_stats=False,
        )


def test_statcast_date_range_with_team():
    data = pyb.statcast_date_range(
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


def test_statcast_single_game_return_pandas_extra_stats():
    data = pyb.statcast_single_game(game_pk=634, extra_stats=True, return_pandas=True)
    assert isinstance(data, pd.DataFrame)
    assert data.shape[0] == 303
    assert data.shape[1] == 249


# STATCAST_BATTER_RANGE_TESTS


def test_statcast_batter_bad_inputs():
    with pytest.raises(ValueError):
        pyb.statcast_single_batter_range(
            start_dt=END_DT,
            end_dt=START_DT,
            player_id=0,
            extra_stats=False,
            return_pandas=False,
        )
    with pytest.raises(ValueError):
        pyb.statcast_single_batter_range(
            start_dt=None,
            end_dt=END_DT,
            player_id=677772,
            extra_stats=False,
            return_pandas=False,
        )


def test_statcast_batter():
    data = pyb.statcast_single_batter_range(
        start_dt="2024-04-01",
        end_dt="2024-06-01",
        player_id="547180",
        extra_stats=True,
        return_pandas=False,
    )
    assert isinstance(data, pl.LazyFrame)
    data = data.collect()
    assert isinstance(data, pl.DataFrame)
    assert data.shape[1] == 181
    assert data.shape[0] == 872
    assert len(data.select("batter").unique()) == 1
    data = pyb.statcast_single_batter_range(
        start_dt="2024-04-01",
        end_dt="2024-06-01",
        player_id="547180",
        extra_stats=False,
        return_pandas=False,
    )
    assert isinstance(data, pl.LazyFrame)
    data = data.collect()
    assert isinstance(data, pl.DataFrame)
    assert data.shape[1] == 113
    assert data.shape[0] == 872
    assert len(data.select("batter").unique()) == 1


def test_statcast_pitcher():
    data = pyb.statcast_single_pitcher_range(
        start_dt="2024-04-01",
        end_dt="2024-06-01",
        player_id="671096",
        extra_stats=True,
        return_pandas=False,
    )
    assert isinstance(data, pl.LazyFrame)
    data = data.collect()
    assert isinstance(data, pl.DataFrame)
    assert data.shape[1] == 181
    assert data.shape[0] == 1009
    assert len(data.select("pitcher").unique()) == 1
