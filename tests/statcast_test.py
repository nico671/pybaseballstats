import polars as pl
import pytest

import pybaseballstats.statcast as sc


def test_pitch_by_pitch_data_errors():
    with pytest.raises(ValueError):
        sc.pitch_by_pitch_data(start_date=None, end_date="2023-07-01")
    with pytest.raises(ValueError):
        sc.pitch_by_pitch_data(start_date="2023-07-01", end_date=None)
    df = sc.pitch_by_pitch_data(start_date="2023-07-01", end_date="2023-07-02")
    assert df is not None
    assert isinstance(df, pl.LazyFrame)


def test_pitch_by_pitch_data_general():
    df = sc.pitch_by_pitch_data(
        start_date="2023-07-01", end_date="2023-07-03", force_collect=True
    )
    assert df is not None
    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] == 12201
    assert df.shape[1] == 118
    assert df.select(pl.col("game_date").min()).item() == "2023-07-01"
    assert df.select(pl.col("game_date").max()).item() == "2023-07-03"
    assert df.select(pl.col("game_pk").n_unique()).item() == 41
    assert df.select(pl.col("player_name").n_unique()).item() == 296
