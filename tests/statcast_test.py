import polars as pl
import pytest

import pybaseballstats.statcast as sc


def test_pitch_by_pitch_data_errors():
    """Test error handling in pitch_by_pitch_data."""
    with pytest.raises(ValueError):
        sc.pitch_by_pitch_data(start_date=None, end_date="2023-07-01")
    with pytest.raises(ValueError):
        sc.pitch_by_pitch_data(start_date="2023-07-01", end_date=None)

    df = sc.pitch_by_pitch_data(start_date="2023-07-01", end_date="2023-07-02")
    assert df is not None
    assert isinstance(df, pl.LazyFrame)


def test_pitch_by_pitch_data_general():
    """Test general functionality of pitch_by_pitch_data."""
    df = sc.pitch_by_pitch_data(
        start_date="2023-07-01", end_date="2023-07-03", force_collect=True
    )
    assert df is not None
    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] == 12227
    assert df.shape[1] == 118
    assert df.select(pl.col("game_date").min()).item() == "2023-07-01"
    assert df.select(pl.col("game_date").max()).item() == "2023-07-03"
    assert df.select(pl.col("game_pk").n_unique()).item() == 41
    assert df.select(pl.col("player_name").n_unique()).item() == 296


def test_pitch_by_pitch_data_team_none_returns_all():
    """Ensure no filtering is applied when team is None."""
    df = sc.pitch_by_pitch_data(
        start_date="2023-07-03", end_date="2023-07-03", team=None, force_collect=True
    )
    assert df is not None
    assert isinstance(df, pl.DataFrame)
    assert df.select(pl.col("home_team").n_unique()).item() > 1
    assert df.select(pl.col("away_team").n_unique()).item() > 1


def test_pitch_by_pitch_data_team_filtering():
    """Test team filtering of pitch_by_pitch_data."""
    df = sc.pitch_by_pitch_data(
        start_date="2023-07-01",
        end_date="2023-07-03",
        team=sc.StatcastTeams.DODGERS,
        force_collect=True,
    )
    assert df is not None
    assert isinstance(df, pl.DataFrame)
    assert df.shape[1] == 118
    assert df.select(pl.col("game_date").min()).item() == "2023-07-01"
    assert df.select(pl.col("game_date").max()).item() == "2023-07-03"

    dodgers_games = (pl.col("home_team") == "LAD") | (pl.col("away_team") == "LAD")
    assert df.filter(
        ~dodgers_games
    ).is_empty()  # Filters out non Dodger rows and there should be none
    assert df.shape[0] > 0


def test_pitch_by_pitch_data_invalid_team():
    """Tests for AttributeError exception to be raised when you try to access a nonexistent enum member"""
    with pytest.raises(AttributeError):
        sc.pitch_by_pitch_data(
            start_date="2023-07-01",
            end_date="2023-07-03",
            team=sc.StatcastTeams.METZ,
        )
