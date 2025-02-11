import os
import sys

import pandas as pd
import polars as pl
import pytest

# 15th test
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
        qual="100",
        start_season=None,
        end_season=None,
    )
    assert data_qual is not None
    assert data_non_qual is not None
    # Typically, the qualified dataset is a subset
    assert data_qual.shape[0] < data_non_qual.shape[0]
    assert data_qual.shape[1] == data_non_qual.shape[1]


# FANGRAPHS_PITCHING_RANGE
def test_fangraphs_pitching_range_dates():
    data = pyb.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        starter_reliever="all",
        league=pyb.FangraphsLeagueTypes.ALL,
        team=pyb.FangraphsTeams.ALL,
        rost=0,
        handedness="",
        stat_split=pyb.FangraphsStatSplitTypes.PLAYER,
    )
    assert data is not None
    assert data.shape[0] == 58
    assert data.shape[1] == 375


def test_fangraphs_pitching_range_seasons():
    data = pyb.fangraphs_pitching_range(
        start_season="2024",
        end_season="2024",
        stat_types=None,
        return_pandas=False,
        starter_reliever="all",
        league=pyb.FangraphsLeagueTypes.ALL,
        team=pyb.FangraphsTeams.ALL,
        rost=0,
        handedness="",
        stat_split=pyb.FangraphsStatSplitTypes.PLAYER,
    )
    assert data is not None
    assert data.shape[0] == 58
    assert data.shape[1] == 375


def test_fangraphs_pitching_range_one_stat_type():
    data = pyb.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=[pyb.FangraphsPitchingStatType.STANDARD],
        return_pandas=False,
        starter_reliever="all",
        league=pyb.FangraphsLeagueTypes.ALL,
        team=pyb.FangraphsTeams.ALL,
        rost=0,
        handedness="",
        stat_split=pyb.FangraphsStatSplitTypes.PLAYER,
    )
    assert data is not None
    assert data.shape[0] == 58
    assert data.shape[1] == 6


def test_fangraphs_pitching_range_multiple_stat_type():
    data = pyb.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=[
            pyb.FangraphsPitchingStatType.STANDARD,
            pyb.FangraphsPitchingStatType.STATCAST,
        ],
        return_pandas=False,
        starter_reliever="all",
        league=pyb.FangraphsLeagueTypes.ALL,
        team=pyb.FangraphsTeams.ALL,
        rost=0,
        handedness="",
        stat_split=pyb.FangraphsStatSplitTypes.PLAYER,
    )
    assert data is not None
    assert data.shape[0] == 58
    assert data.shape[1] == 6


# start_date: str = None,
#     end_date: str = None,
#     start_season: str = None,
#     end_season: str = None,
#     stat_types: List[FangraphsPitchingStatType] = None,
#     starter_reliever: str = "all",  # stats in url (sta, rel, all)
#     return_pandas: bool = False,
#     league: FangraphsLeagueTypes = FangraphsLeagueTypes.ALL,
#     team: FangraphsTeams = FangraphsTeams.ALL,
#     rost: int = 0,
#     handedness: str = "",
#     stat_split: FangraphsStatSplitTypes = FangraphsStatSplitTypes.PLAYER,
