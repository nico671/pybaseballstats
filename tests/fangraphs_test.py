import os
import sys

import pandas as pd
import polars as pl
import pytest

from pybaseballstats.utils.consts import FangraphsBattingPosTypes

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
            pos=FangraphsBattingPosTypes.ALL,
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
            pos=FangraphsBattingPosTypes.ALL,
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
            pos=FangraphsBattingPosTypes.ALL,
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
            pos=FangraphsBattingPosTypes.ALL,
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
        pos=FangraphsBattingPosTypes.ALL,
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
        pos=FangraphsBattingPosTypes.ALL,
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
        league=pyb.FangraphsLeagueTypes.ALL,
        team=pyb.FangraphsTeams.ALL,
        rost=0,
        handedness="",
        stat_split=pyb.FangraphsStatSplitTypes.PLAYER,
    )
    assert data is not None
    assert data.shape[0] == 58
    assert data.shape[1] == 25


def test_fangraphs_pitching_range_multiple_stat_type():
    data = pyb.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=[
            pyb.FangraphsPitchingStatType.STANDARD,
            pyb.FangraphsPitchingStatType.STATCAST,
        ],
        return_pandas=False,
        league=pyb.FangraphsLeagueTypes.ALL,
        team=pyb.FangraphsTeams.ALL,
        rost=0,
        handedness="",
        stat_split=pyb.FangraphsStatSplitTypes.PLAYER,
    )
    assert data is not None
    assert data.shape[0] == 58
    assert data.shape[1] == 34


def test_fangraphs_pitching_range_starter_reliever():
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=None,
            return_pandas=False,
            starter_reliever="invalid",
            league=pyb.FangraphsLeagueTypes.ALL,
            team=pyb.FangraphsTeams.ALL,
            rost=0,
            handedness="",
            stat_split=pyb.FangraphsStatSplitTypes.PLAYER,
        )

    data = pyb.fangraphs_pitching_range(
        start_season="2024",
        end_season="2024",
        stat_types=None,
        return_pandas=False,
        starter_reliever="sta",
        league=pyb.FangraphsLeagueTypes.ALL,
        team=pyb.FangraphsTeams.ALL,
        rost=0,
        handedness="",
        stat_split=pyb.FangraphsStatSplitTypes.PLAYER,
    )
    assert data is not None
    assert data.shape[0] == 57
    assert data.shape[1] == 375
    data2 = pyb.fangraphs_pitching_range(
        start_season="2024",
        end_season="2024",
        stat_types=None,
        return_pandas=False,
        starter_reliever="rel",
        league=pyb.FangraphsLeagueTypes.ALL,
        team=pyb.FangraphsTeams.ALL,
        rost=0,
        handedness="",
        stat_split=pyb.FangraphsStatSplitTypes.PLAYER,
    )
    assert data2 is not None
    assert data2.shape[0] == 169
    assert data2.shape[1] == 375


# fangraphs_fielding_range
def test_fangraphs_fielding_range():
    data = pyb.fangraphs_fielding_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        league=pyb.FangraphsLeagueTypes.ALL,
        team=pyb.FangraphsTeams.ALL,
        rost=0,
        pos=FangraphsBattingPosTypes.ALL,
    )
    assert data is not None
    assert data.shape[0] == 112
    assert data.shape[1] == 46


def test_fangraphs_fielding_range_invalid_pos():
    with pytest.raises(AttributeError):
        pyb.fangraphs_fielding_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=None,
            return_pandas=False,
            league=pyb.FangraphsLeagueTypes.ALL,
            team=pyb.FangraphsTeams.ALL,
            rost=0,
            pos="invalid",
        )


def test_fangraphs_fielding_range_invalid_stat_types():
    with pytest.raises(AttributeError):
        pyb.fangraphs_fielding_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=["invalid"],
            return_pandas=False,
            league=pyb.FangraphsLeagueTypes.ALL,
            team=pyb.FangraphsTeams.ALL,
            rost=0,
            pos=FangraphsBattingPosTypes.ALL,
        )


def test_fangreaphs_fielding_range_bad_inputs():
    with pytest.raises(ValueError):
        pyb.fangraphs_fielding_range(
            start_date="2024-05-01",
            end_date="2024-04-01",
            stat_types=None,
            return_pandas=False,
            league=pyb.FangraphsLeagueTypes.ALL,
            team=pyb.FangraphsTeams.ALL,
            rost=0,
            pos=FangraphsBattingPosTypes.ALL,
        )
