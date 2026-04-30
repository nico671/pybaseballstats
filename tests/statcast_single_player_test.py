import polars as pl
import pytest

import pybaseballstats.statcast_single_player as ssp

pytestmark = [
    pytest.mark.integration,
    pytest.mark.heavy,
    pytest.mark.data_dependent,
]

def test_single_player_season_stats_bad_inputs():
    with pytest.raises(TypeError):
        ssp.single_player_season_stats(
            player_id="660271", season=2023, player_type="batter"
        )
    with pytest.raises(TypeError):
        ssp.single_player_season_stats(
            player_id=660271, season="2023", player_type="batter"
        )
    with pytest.raises(ValueError):
        ssp.single_player_season_stats(
            player_id=660271, season=1900, player_type="batter"
        )
    with pytest.raises(ValueError):
        ssp.single_player_season_stats(
            player_id=660271, season=2023, player_type="fielder"
        )


def test_single_player_season_stats_batter():
    # Shohei Ohtani
    df = ssp.single_player_season_stats(
        player_id=660271,
        season=2024,
        player_type="batter",
    )

    assert df.shape[0] == 1
    assert df.select(pl.col("player_id")).item() == 660271
    for col in ["player_name", "pa", "ba", "xwoba", "velocity", "barrels_total"]:
        assert col in df.columns
    assert df.select(pl.col("player_name")).item() == "Ohtani, Shohei"
    assert df.select(pl.col("pa")).item() == 731
    assert df.select(pl.col("abs")).item() == 636
    assert df.select(pl.col("hits")).item() == 197
    assert df.select(pl.col("hrs")).item() == 54
    assert df.select(pl.col("ba")).item() == 0.31
    assert df.select(pl.col("slg")).item() == 0.646
    assert df.select(pl.col("woba")).item() == 0.431
    assert df.select(pl.col("xwoba")).item() == 0.444


def test_single_player_season_stats_pitcher():
    # Yoshinobu Yamamoto
    df = ssp.single_player_season_stats(
        player_id=808967,
        season=2025,
        player_type="pitcher",
    )

    assert df.shape[0] == 1
    assert df.select(pl.col("player_id")).item() == 808967
    for col in ["player_name", "pa", "ba", "xwoba", "velocity", "barrels_total"]:
        assert col in df.columns
    assert df.select(pl.col("player_name")).item() == "Yamamoto, Yoshinobu"
    assert df.select(pl.col("pa")).item() == 684
    assert df.select(pl.col("abs")).item() == 619
    assert df.select(pl.col("hits")).item() == 113
    assert df.select(pl.col("hrs")).item() == 14
    assert df.select(pl.col("ba")).item() == 0.183
    assert df.select(pl.col("slg")).item() == 0.283
    assert df.select(pl.col("woba")).item() == 0.244
    assert df.select(pl.col("xwoba")).item() == 0.259
