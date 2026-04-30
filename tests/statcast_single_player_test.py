import polars as pl
import pytest

import pybaseballstats.statcast_single_player as ssp

pytestmark = [
    pytest.mark.integration,
    pytest.mark.heavy,
    pytest.mark.data_dependent,
]

# 660271 is Shohei Ohtani's MLBAM player ID
# 605141 is Mookie Betts' MLBAM player ID

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
    # Mookie Betts
    df = ssp.single_player_season_stats(
        player_id=605141,
        season=2023,
        player_type="batter",
    )

    assert df.shape[0] == 1
    assert df.select(pl.col("player_id")).item() == 605141
    for col in ["player_name", "pa", "ba", "xwoba", "velocity", "barrels_total"]:
        assert col in df.columns


def test_single_player_season_stats_pitcher():
    # Shohei Ohtani
    df = ssp.single_player_season_stats(
        player_id=660271,
        season=2023,
        player_type="pitcher",
    )

    assert df.shape[0] == 1
    assert df.select(pl.col("player_id")).item() == 660271
    for col in ["player_name", "pa", "ba", "xwoba", "velocity", "barrels_total"]:
        assert col in df.columns
