import os
import sys

import polars as pl
import pytest
from polars.testing import assert_frame_equal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb


def test_fangraphs_single_game_play_by_play_badinputs():
    with pytest.raises(ValueError):
        pyb.fangraphs_single_game.fangraphs_single_game_play_by_play(
            "06-20-2024", pyb.fangraphs_single_game.FangraphsSingleGameTeams.White_Sox
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_single_game.fangraphs_single_game_play_by_play(
            "2024-06-20",
            "whitesox",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_single_game.fangraphs_single_game_play_by_play(
            "1900-06-20",
            pyb.fangraphs_single_game.FangraphsSingleGameTeams.White_Sox,
        )


def test_fangraphs_single_game_play_by_play_regular():
    df = pyb.fangraphs_single_game.fangraphs_single_game_play_by_play(
        "2024-06-20", pyb.fangraphs_single_game.FangraphsSingleGameTeams.White_Sox
    )
    assert df is not None
    assert df.shape[0] == 83
    assert df.shape[1] == 12
    assert isinstance(df, pl.DataFrame)
    assert df.select(pl.col("Outs").n_unique()).item() == 3
    assert (
        df.select(pl.col("Win Expectancy").max()).item() == 100.0
        or df.select(pl.col("Win Expectancy").min()).item() == 0.0
    )

    df2 = pyb.fangraphs_single_game.fangraphs_single_game_play_by_play(
        "2024-06-20",
        pyb.fangraphs_single_game.FangraphsSingleGameTeams.White_Sox,
        return_pandas=True,
    )

    assert df2 is not None
    assert df2.shape[0] == 83
    assert df2.shape[1] == 12
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))
