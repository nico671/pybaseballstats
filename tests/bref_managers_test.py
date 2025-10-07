import polars as pl
import pytest

import pybaseballstats.bref_managers as bm


def test_manager_basic_data():
    with pytest.raises(ValueError):
        bm.managers_basic_data(year=None)
    with pytest.raises(TypeError):
        bm.managers_basic_data(year="2023")
    with pytest.raises(ValueError):
        bm.managers_basic_data(year=1800)
    df = bm.managers_basic_data(year=2025)
    assert df.shape[0] == 34
    assert df.shape[1] == 15
    assert df.select(pl.col("manager").n_unique()).item() == 34
    assert df.select(pl.col("team_ID").n_unique()).item() == 30
    assert df.select(pl.col("G").min()).item() == 38
    assert df.select(pl.col("G").max()).item() == 162
    assert df.select(pl.col("W").min()).item() == 7
    assert df.select(pl.col("W").max()).item() == 97
    assert df.select(pl.col("mgr_ejections").max()).item() == 7


def test_manager_tendencies_data():
    with pytest.raises(ValueError):
        bm.managers_tendencies_data(year=None)
    with pytest.raises(TypeError):
        bm.managers_tendencies_data(year="2023")
    with pytest.raises(ValueError):
        bm.managers_tendencies_data(year=1800)
    df = bm.managers_tendencies_data(year=2025)
    assert df.shape[0] == 34
    assert df.shape[1] == 26
    assert df.select(pl.col("manager").n_unique()).item() == 34
    assert df.select(pl.col("team_ID").n_unique()).item() == 30
    assert df.select(pl.col("manager_games").min()).item() == 38
    assert df.select(pl.col("manager_games").max()).item() == 162
