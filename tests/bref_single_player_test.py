import os
import sys

import polars as pl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb

TEST_PLAYER_CODE = "bettsmo01"


def test_single_player_standard_batting():
    df = pyb.bref_single_player.single_player_standard_batting(
        player_code=TEST_PLAYER_CODE, return_pandas=False
    )
    assert isinstance(df, pl.DataFrame)
    assert df.shape == (12, 33)
    assert df.select(pl.col("team_name").n_unique()).item() == 2
    assert df.select(pl.col("age").n_unique()).item() == 12


def test_single_player_value_batting():
    df = pyb.bref_single_player.single_player_value_batting(
        player_code=TEST_PLAYER_CODE, return_pandas=False
    )
    assert isinstance(df, pl.DataFrame)
    assert df.shape == (12, 22)
    assert df.select(pl.col("team_name").n_unique()).item() == 2
    assert df.select(pl.col("age").n_unique()).item() == 12


def test_single_player_advanced_batting():
    df = pyb.bref_single_player.single_player_advanced_batting(
        player_code=TEST_PLAYER_CODE, return_pandas=False
    )
    assert isinstance(df, pl.DataFrame)
    assert df.shape == (12, 29)
    assert df.select(pl.col("team_name").n_unique()).item() == 2
    assert df.select(pl.col("age").n_unique()).item() == 12
