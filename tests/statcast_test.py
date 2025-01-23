# content of test_sample.py
import pandas as pd
import polars as pl

import pybaseballstats as pyb


# STATCAST_SINGLE_GAME_TESTS
def test_statcast_single_game_game_pk_not_correct():
    data = pyb.statcast_single_game(
        game_pk=100000000000, return_pandas=False, extra_stats=False
    ).collect()
    assert data is not None
    assert data.shape[0] == 0
    assert data.shape[1] == 113
    assert type(data) is pl.DataFrame


def test_statcast_single_game_pk_not_correct_to_pandas():
    data = pyb.statcast_single_game(
        game_pk=100000000000, return_pandas=True, extra_stats=False
    )
    assert data is not None
    assert data.shape[0] == 0
    assert data.shape[1] == 113
    assert type(data) is pd.DataFrame


def test_statcast_single_game_game_pk_correct():
    data = pyb.statcast_single_game(game_pk=634, return_pandas=False, extra_stats=False)
    assert type(data) is pl.LazyFrame
    data = data.collect()
    assert data is not None
    assert data.shape[0] > 0
    assert data.shape[1] == 113
    assert type(data) is pl.DataFrame


def test_statcast_single_game_game_pk_correct_extra_stats():
    data = pyb.statcast_single_game(
        game_pk=634, return_pandas=False, extra_stats=True
    ).collect()
    assert data is not None
    assert data.shape[0] > 0
    assert data.shape[1] > 113
    assert type(data) is pl.DataFrame
