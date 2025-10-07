import polars as pl

from pybaseballstats import bref_single_player as bsp


def test_single_player_standard_batting():
    df = bsp.single_player_standard_batting("suzukse01")
    assert df.shape[0] >= 4
    assert df.shape[1] == 34
    assert df.head(4).select(pl.col("team_name").n_unique()).item() == 1
    assert df.head(4).select(pl.col("team_name").unique()).item() == "CHC"
    assert df.head(4).select(pl.col("age").min()).item() == 27
    assert df.head(4).select(pl.col("age").max()).item() == 30


def test_single_player_standard_pitching():
    df = bsp.single_player_standard_pitching("imanash01")
    assert df.shape[0] >= 2
    assert df.shape[1] == 36
    assert df.head(2).select(pl.col("team_name").n_unique()).item() == 1
    assert df.head(2).select(pl.col("team_name").unique()).item() == "CHC"
    assert df.head(2).select(pl.col("age").min()).item() == 30
    assert df.head(2).select(pl.col("age").max()).item() == 31


def test_single_player_standard_fielding():
    df = bsp.single_player_standard_fielding("suzukse01")
    assert df.shape[0] >= 15
    assert df.shape[1] == 26
    assert df.head(15).select(pl.col("team_name").n_unique()).item() == 1
    assert df.head(15).select(pl.col("team_name").unique()).item() == "CHC"
    assert df.head(15).select(pl.col("age").min()).item() == 27
    assert df.head(15).select(pl.col("age").max()).item() == 30
