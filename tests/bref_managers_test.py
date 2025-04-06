import os
import sys

import polars as pl
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb

TEST_YEAR = 2023


def test_managers_basic_data_bad_inputs():
    with pytest.raises(ValueError):
        pyb.bref_managers.managers_basic_data(1870)
    with pytest.raises(TypeError):
        pyb.bref_managers.managers_basic_data("2023")
    with pytest.raises(ValueError):
        pyb.bref_managers.managers_basic_data(None)


def test_managers_basic_data():
    df = pyb.bref_managers.managers_basic_data(TEST_YEAR)

    assert isinstance(df, pl.DataFrame)
    assert df.shape == (31, 15)
    assert df.select(pl.col("manager").n_unique()).item() == 31
    assert df.select(pl.col("team_ID").n_unique()).item() == 30
    assert df.select(pl.col("finish").max()).item() == 5.0
    assert df.select(pl.col("finish").min()).item() == 1.0


def test_manager_tendencies_data_bad_inputs():
    with pytest.raises(ValueError):
        pyb.bref_managers.manager_tendencies_data(1870)
    with pytest.raises(TypeError):
        pyb.bref_managers.manager_tendencies_data("2023")
    with pytest.raises(ValueError):
        pyb.bref_managers.manager_tendencies_data(None)


def test_manager_tendencies_data():
    df = pyb.bref_managers.manager_tendencies_data(TEST_YEAR)

    assert isinstance(df, pl.DataFrame)
    assert df.shape == (31, 26)
    assert df.select(pl.col("manager").n_unique()).item() == 31
    assert df.select(pl.col("team_ID").n_unique()).item() == 30
    assert df.select(pl.col("manager_games").max()).item() == 162
    assert df.select(pl.col("manager_games").min()).item() == 3
