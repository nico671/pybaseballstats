import os
import sys

import pandas as pd
import polars as pl
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb

START_DT = "2024-04-01"
END_DT = "2024-04-10"


# STATCAST_SINGLE_GAME_TESTS
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
