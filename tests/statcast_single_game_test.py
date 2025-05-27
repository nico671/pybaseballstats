import os
import sys

import pandas as pd
import polars as pl
import pytest
from polars.testing import assert_frame_equal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb


def test_statcast_single_game_game_pk_not_correct():
    data = pyb.statcast_single_game.statcast_single_game_pitch_by_pitch(
        game_pk=0,
    )
    assert data is not None
    assert data.shape[0] == 0
    assert data.shape[1] == 118
    assert type(data) is pl.DataFrame


def test_statcast_single_game_game_pk_correct():
    data = pyb.statcast_single_game.statcast_single_game_pitch_by_pitch(
        game_pk=634, return_pandas=False
    )
    assert data is not None
    assert type(data) is pl.DataFrame
    assert data.shape[0] == 303
    assert data.shape[1] == 118
    assert data.select(pl.col("game_pk").n_unique()).item() == 1
    assert data.select(pl.col("game_pk").unique()).item() == 634
    assert data.select(pl.col("game_date").n_unique()).item() == 1
    assert data.select(pl.col("game_date").unique()).item() == "1999-07-21"

    df2 = pyb.statcast_single_game.statcast_single_game_pitch_by_pitch(
        game_pk=634, return_pandas=True
    )
    assert df2 is not None
    assert type(df2) is pd.DataFrame
    assert df2.shape[0] == 303
    assert df2.shape[1] == 118
    assert_frame_equal(data, pl.DataFrame(df2, schema=data.schema))


# single game ev test


def test_statcast_single_game_ev_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_single_game.get_statcast_single_game_exit_velocity(
            game_pk=745340, game_date="2024/05/10"
        )


def test_statcast_single_game_ev():
    df = pyb.statcast_single_game.get_statcast_single_game_exit_velocity(
        game_pk=745340,
        game_date="2024-05-10",
        return_pandas=False,
    )
    assert df is not None
    assert type(df) is pl.DataFrame
    assert df.shape[0] == 55
    assert df.shape[1] == 12
    assert df.select(pl.col("num_pa").max()).item() == 71
    assert df.select(pl.col("num_pa").min()).item() == 1
    assert df.select(pl.col("batter_name").n_unique()).item() == 20


def test_statcast_single_game_pv_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_single_game.get_statcast_single_game_pitch_velocity(
            game_pk=745340, game_date="2024/05/10"
        )


def test_statcast_single_game_pv():
    df = pyb.statcast_single_game.get_statcast_single_game_pitch_velocity(
        game_pk=745340,
        game_date="2024-05-10",
        return_pandas=False,
    )
    assert df is not None
    assert type(df) is pl.DataFrame
    assert df.shape[0] == 287
    assert df.shape[1] == 13
    assert df.select(pl.col("game_pa_number").max()).item() == 73
    assert df.select(pl.col("game_pa_number").min()).item() == 1
    assert df.select(pl.col("pitcher_name").n_unique()).item() == 8
    assert df.select(pl.col("game_pitch_number").max()).item() == 333
    assert df.select(pl.col("game_pitch_number").min()).item() == 4


def test_statcast_single_game_wp_badinputs():
    with pytest.raises(ValueError):
        pyb.statcast_single_game.get_statcast_single_game_wp_table(
            game_pk=745340, game_date="2024/05/10"
        )


def test_statcast_single_game_wp():
    df = pyb.statcast_single_game.get_statcast_single_game_wp_table(
        game_pk=745340,
        game_date="2024-05-10",
        return_pandas=False,
    )
    assert df is not None
    assert type(df) is pl.DataFrame
    assert df.shape[0] == 74
    assert df.shape[1] == 8
    assert df.select(pl.col("game_pa_number").max()).item() == 73
    assert df.select(pl.col("game_pa_number").min()).item() == 0
    assert df.select(pl.col("pitcher_name").n_unique()).item() == 9
    assert df.select(pl.col("Home WP%").min()).item() == 0.0
    assert df.select(pl.col("Away WP%").max()).item() == 100.0
