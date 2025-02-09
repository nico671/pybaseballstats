import os
import sys

import pandas as pd
import polars as pl
import pytest

# Setup path to import pybaseballstats
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb


# Basic functionality tests for fangraphs_batting_range
def test_fangraphs_batting_range_output():
    # Test with Polars and Pandas output
    for return_pandas, df_type in [(False, pl.DataFrame), (True, pd.DataFrame)]:
        data = pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=None,
            return_pandas=return_pandas,
            pos="all",
            league="",
            qual="y",
            start_season=None,
            end_season=None,
        )
        assert data is not None
        assert data.shape[0] == 129
        assert data.shape[1] == 313
        assert isinstance(data, df_type)


# Test invalid inputs trigger ValueErrors
@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            start_date="2024-05-01",
            end_date="2024-04-01",
            stat_types=None,
            return_pandas=False,
            pos="all",
            league="",
            qual="y",
            start_season=None,
            end_season=None,
        ),
        dict(
            start_date=None,
            end_date=None,
            stat_types=None,
            return_pandas=False,
            pos="all",
            league="",
            qual="y",
            start_season=None,
            end_season=None,
        ),
        dict(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=[],
            return_pandas=False,
            pos="all",
            league="",
            qual="y",
            start_season=None,
            end_season=None,
        ),
    ],
)
def test_invalid_batting_range_inputs(kwargs):
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(**kwargs)


# Compare qualified vs. unqualified minimum at bats
def test_qual_vs_non_qual():
    data_qual = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        pos="all",
        league="",
        qual="y",
        start_season=None,
        end_season=None,
    )
    data_non_qual = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        pos="all",
        league="",
        qual="50",
        start_season=None,
        end_season=None,
    )
    assert data_qual is not None
    assert data_non_qual is not None
    # Typically, the qualified dataset is a subset
    assert data_qual.shape[0] < data_non_qual.shape[0]
    assert data_qual.shape[1] == data_non_qual.shape[1]


# Test handedness filtering using parameterization
@pytest.mark.parametrize(
    "handedness,expected_rows",
    [
        ("R", 71),
        ("L", 44),
        ("S", 14),
    ],
)
def test_handedness_filter(handedness, expected_rows):
    data = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        pos="all",
        league="",
        qual="y",
        start_season=None,
        end_season=None,
        handedness=handedness,
    )
    assert data is not None
    assert data.shape[0] == expected_rows
    assert data.shape[1] == 313


def test_active_roster_filter():
    data = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        pos="all",
        league="",
        qual="y",
        start_season=None,
        end_season=None,
        rost=1,
    )
    assert data is not None
    assert data.shape[0] == 123
    assert data.shape[1] == 313


# Pitching Tests
def test_fangraphs_pitching_range_output():
    # Test with both Polars and Pandas output
    for return_pandas, df_type in [(False, pl.DataFrame), (True, pd.DataFrame)]:
        data = pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=None,
            return_pandas=return_pandas,
            league="",
            qual="y",
            start_season=None,
            end_season=None,
        )
        assert data is not None
        assert data.shape[0] == 142  # Adjust based on actual data
        assert data.shape[1] == 286  # Adjust based on actual data
        assert isinstance(data, df_type)


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            start_date="2024-05-01",
            end_date="2024-04-01",  # Invalid date order
            stat_types=None,
            return_pandas=False,
            league="",
            qual="y",
        ),
        dict(
            start_date=None,
            end_date=None,
            stat_types=None,
            return_pandas=False,
            league="",
            qual="y",
        ),
        dict(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=[],  # Empty stat types
            return_pandas=False,
            league="",
            qual="y",
        ),
        dict(
            start_date="2024-04-01",
            end_date=None,  # Missing end_date
            stat_types=None,
            return_pandas=False,
            league="",
            qual="y",
        ),
    ],
)
def test_invalid_pitching_range_inputs(kwargs):
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(**kwargs)


def test_pitching_qual_vs_non_qual():
    # Compare qualified vs. unqualified minimum innings
    data_qual = pyb.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        league="",
        qual="y",
    )
    data_non_qual = pyb.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        league="",
        qual="20",  # 20 innings pitched minimum
    )
    assert data_qual is not None
    assert data_non_qual is not None
    assert (
        data_qual.shape[0] < data_non_qual.shape[0]
    )  # Qualified should be smaller subset
    assert data_qual.shape[1] == data_non_qual.shape[1]


def test_pitching_active_roster_filter():
    # Test active roster filtering
    data = pyb.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        league="",
        qual="y",
        rost=1,  # Active roster only
    )
    assert data is not None
    assert data.shape[0] == 135  # Adjust based on actual active roster count
    assert data.shape[1] == 286  # Adjust based on actual columns


@pytest.mark.parametrize(
    "starter_reliever,expected_rows",
    [
        ("all", 142),  # All pitchers
        ("sta", 68),  # Starters only
        ("rel", 74),  # Relievers only
    ],
)
def test_starter_reliever_filter(starter_reliever, expected_rows):
    data = pyb.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        league="",
        qual="y",
        starter_reliever=starter_reliever,
    )
    assert data is not None
    assert data.shape[0] == expected_rows
    assert data.shape[1] == 286


@pytest.mark.parametrize(
    "league,expected_rows",
    [
        ("", 142),  # All leagues
        ("nl", 74),  # National League
        ("al", 68),  # American League
    ],
)
def test_pitching_league_filter(league, expected_rows):
    data = pyb.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        league=league,
        qual="y",
    )
    assert data is not None
    assert data.shape[0] == expected_rows
    assert data.shape[1] == 286
