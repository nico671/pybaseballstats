import os
import sys

import pandas as pd
import polars as pl
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pybaseballstats.umpire_scorecard import (
    umpire_games_date_range,
)
from pybaseballstats.utils.umpire_scorecard_utils import UmpireScorecardTeams


# Test umpire_games_date_range
def test_umpire_games_date_range_badinputs():
    with pytest.raises(ValueError):
        umpire_games_date_range(
            start_date="2024-05-01",
            end_date="2024-04-01",
            season_type="*",
            home_team=UmpireScorecardTeams.ALL,
            away_team=UmpireScorecardTeams.ALL,
            umpire_name="",
            return_pandas=False,
        )

    with pytest.raises(ValueError):
        umpire_games_date_range(
            start_date=None,
            end_date=None,
            season_type="*",
            home_team=UmpireScorecardTeams.ALL,
            away_team=UmpireScorecardTeams.ALL,
            umpire_name="",
            return_pandas=False,
        )
    with pytest.raises(ValueError):
        umpire_games_date_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            season_type="postseason_only",
            home_team=UmpireScorecardTeams.ALL,
            away_team=UmpireScorecardTeams.ALL,
            umpire_name="",
            return_pandas=False,
        )


def test_umpire_games_date_range_regular():
    data = umpire_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        home_team=UmpireScorecardTeams.ALL,
        away_team=UmpireScorecardTeams.ALL,
        umpire_name="",
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 129
    assert data.shape[1] == 33
    assert type(data) is pl.DataFrame

    data = umpire_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        home_team=UmpireScorecardTeams.ALL,
        away_team=UmpireScorecardTeams.ALL,
        umpire_name="",
        return_pandas=True,
    )
    assert data is not None
    assert data.shape[0] == 129
    assert data.shape[1] == 33
    assert type(data) is pd.DataFrame


def test_umpire_games_date_range_custom_team():
    data = umpire_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        home_team=UmpireScorecardTeams.WSH,
        away_team=UmpireScorecardTeams.ALL,
        umpire_name="",
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 6
    assert data.shape[1] == 33
    assert type(data) is pl.DataFrame


def test_umpire_games_date_range_custom_umpire():
    data = umpire_games_date_range(
        start_date="2024-09-28",
        end_date="2024-09-30",
        season_type="*",
        home_team=UmpireScorecardTeams.ALL,
        away_team=UmpireScorecardTeams.ALL,
        umpire_name="blagh",
        return_pandas=True,
    )
    assert data is not None
    assert data.shape[0] == 0
    assert data.shape[1] == 0
    assert type(data) is pd.DataFrame

    data = umpire_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        home_team=UmpireScorecardTeams.ALL,
        away_team=UmpireScorecardTeams.ALL,
        umpire_name="Vic Carapazza",
        return_pandas=True,
    )
    print(data)
    assert data is not None
    assert data.shape[0] == 2
    assert data.shape[1] == 33
    assert type(data) is pd.DataFrame
