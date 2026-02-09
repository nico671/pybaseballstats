import polars as pl
import pytest

import pybaseballstats.statcast_leaderboards as sl


def test_park_factor_dimensions():
    with pytest.raises(ValueError):
        sl.park_factor_dimensions(season=2025, metric="invalid_metric")
    with pytest.raises(ValueError):
        sl.park_factor_dimensions(season=1900, metric="distance")
    df_distance = sl.park_factor_dimensions(season=2025, metric="distance")
    assert df_distance.shape == (32, 13)
    assert (
        df_distance.filter(pl.col("Team") == "Rockies")
        .select(pl.col("lf_line_distance_ft"))
        .item()
        == 347
    )
    assert (
        df_distance.filter(pl.col("Team") == "Rockies")
        .select(pl.col("playing_field_area_sq_ft"))
        .item()
        == 116729
    )
    assert df_distance.select(pl.col("Team").n_unique()).item() == 32
    df_height = sl.park_factor_dimensions(season=2025, metric="height")
    assert df_height.shape == (32, 13)
    assert (
        df_height.filter(pl.col("Team") == "Red Sox")
        .select(pl.col("lf_line_height_ft"))
        .item()
        == 37
    )
    assert (
        df_height.filter(pl.col("Team") == "Red Sox")
        .select(pl.col("playing_field_area_sq_ft"))
        .item()
        == 102935
    )
    assert df_height.select(pl.col("Team").n_unique()).item() == 32
