import polars as pl
import pytest

import pybaseballstats.fangraphs_single_game as fsg


def test_fangraphs_single_game_play_by_play_errors():
    with pytest.raises(ValueError):
        fsg.fangraphs_single_game_play_by_play(date="2023/07/04", team="NYY")
    with pytest.raises(ValueError):
        fsg.fangraphs_single_game_play_by_play(
            date="2050-01-01", team=fsg.FangraphsSingleGameTeams.Angels
        )
    with pytest.raises(ValueError):
        fsg.fangraphs_single_game_play_by_play(
            date="1970-01-01", team=fsg.FangraphsSingleGameTeams.Angels
        )
    with pytest.raises(ValueError):
        fsg.fangraphs_single_game_play_by_play(date="2023-07-04", team=None)
    with pytest.raises(AssertionError):
        fsg.fangraphs_single_game_play_by_play(
            date="2023-11-04", team=fsg.FangraphsSingleGameTeams.Angels
        )


def test_fangraphs_single_game_play_by_play():
    df = fsg.fangraphs_single_game_play_by_play(
        date="2024-09-13", team=fsg.FangraphsSingleGameTeams.Angels
    )
    assert df.shape[0] == 76
    assert df.shape[1] == 12
    assert df.columns == [
        "Pitcher",
        "Player",
        "Inning",
        "Outs",
        "Base State",
        "Score",
        "Play",
        "Leverage Index",
        "RE",
        "Win Expectancy",
        "Win Probability Added",
        "Run Expectancy",
    ]
    assert df.filter(pl.col("Play").str.contains("scored")).shape[0] == 5
    assert df.select(pl.col("Inning").min()).item() == 1
    assert df.select(pl.col("Inning").max()).item() == 9
