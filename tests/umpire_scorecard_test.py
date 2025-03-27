import os
import sys

import pandas as pd
import polars as pl
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pybaseballstats.umpire_scorecard import (
    team_umpire_stats_date_range,
    umpire_games_date_range,
    umpire_stats_date_range,
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
    assert data.select(pl.col("Date").min()).item() == "2024-04-01"
    assert data.select(pl.col("Date").max()).item() == "2024-04-10"
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
        end_date="2024-08-10",
        season_type="*",
        home_team=UmpireScorecardTeams.WSH,
        away_team=UmpireScorecardTeams.NYM,
        umpire_name="",
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 7
    assert data.shape[1] == 33
    assert type(data) is pl.DataFrame
    assert data.select(pl.col("Home Team").first()).item() == "WSH"
    assert data.select(pl.col("Away Team").first()).item() == "NYM"


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
    )
    assert data is not None
    assert data.shape[0] == 2
    assert data.shape[1] == 33
    assert type(data) is pl.DataFrame
    assert data.select(pl.col("Umpire").unique()).item() == "Vic Carapazza"


def test_umpire_games_date_range_custom_season_type():
    df1 = umpire_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="P",
        home_team=UmpireScorecardTeams.ALL,
        away_team=UmpireScorecardTeams.ALL,
        umpire_name="",
    )
    assert df1 is not None
    assert df1.shape[0] == 0
    assert df1.shape[1] == 0
    assert type(df1) is pl.DataFrame

    df2 = umpire_games_date_range(
        start_date="2024-04-01",
        end_date="2024-11-10",
        season_type="P",
        home_team=UmpireScorecardTeams.ALL,
        away_team=UmpireScorecardTeams.ALL,
        umpire_name="",
    )
    assert df2 is not None
    assert df2.shape[0] == 43
    assert df2.shape[1] == 33
    assert type(df2) is pl.DataFrame
    assert set(df2.select(pl.col("type").unique()).to_series().to_list()) == set(
        [
            "D",
            "F",
            "L",
            "W",
        ]
    )


# Test umpire_stats_date_range
def test_umpire_stats_date_range_badinputs():
    with pytest.raises(ValueError):
        umpire_stats_date_range(
            start_date="2024-05-01",
            end_date="2024-04-01",
            season_type="*",
            home_team=UmpireScorecardTeams.ALL,
            away_team=UmpireScorecardTeams.ALL,
            return_pandas=False,
        )

    with pytest.raises(ValueError):
        umpire_stats_date_range(
            start_date=None,
            end_date=None,
            season_type="*",
            home_team=UmpireScorecardTeams.ALL,
            away_team=UmpireScorecardTeams.ALL,
            return_pandas=False,
        )
    with pytest.raises(ValueError):
        umpire_stats_date_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            season_type="postseason_only",
            home_team=UmpireScorecardTeams.ALL,
            away_team=UmpireScorecardTeams.ALL,
            return_pandas=False,
        )


def test_umpire_stats_date_range_regular():
    data = umpire_stats_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        home_team=UmpireScorecardTeams.ALL,
        away_team=UmpireScorecardTeams.ALL,
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 74
    assert data.shape[1] == 20
    assert type(data) is pl.DataFrame

    data = umpire_stats_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        home_team=UmpireScorecardTeams.ALL,
        away_team=UmpireScorecardTeams.ALL,
        return_pandas=True,
    )
    assert data is not None
    assert data.shape[0] == 74
    assert data.shape[1] == 20
    assert type(data) is pd.DataFrame


def test_umpire_stats_date_range_custom_team():
    data = umpire_stats_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        home_team=UmpireScorecardTeams.WSH,
        away_team=UmpireScorecardTeams.ALL,
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 6
    assert data.shape[1] == 20
    assert type(data) is pl.DataFrame

    data = umpire_stats_date_range(
        start_date="2024-04-01",
        end_date="2024-09-10",
        season_type="*",
        home_team=UmpireScorecardTeams.WSH,
        away_team=UmpireScorecardTeams.CHC,
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 3
    assert data.shape[1] == 20
    assert type(data) is pl.DataFrame


def test_umpire_stats_date_range_custom_szn_type():
    data = umpire_stats_date_range(
        start_date="2024-04-01",
        end_date="2024-09-10",
        season_type="R",
        home_team=UmpireScorecardTeams.ALL,
        away_team=UmpireScorecardTeams.ALL,
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 90
    assert data.shape[1] == 20
    assert type(data) is pl.DataFrame


# Test team_umpire_stats_date_range


def test_team_umpire_stats_date_range_bad_inputs():
    with pytest.raises(ValueError):
        data = team_umpire_stats_date_range(
            start_date="2024-05-01",
            end_date="2024-04-01",
            season_type="*",
            team=UmpireScorecardTeams.ALL,
            home_away="*",
            stadium=UmpireScorecardTeams.ALL,
            umpire_name="",
            return_pandas=False,
        )
    with pytest.raises(ValueError):
        data = team_umpire_stats_date_range(
            start_date=None,
            end_date=None,
            season_type="*",
            team=UmpireScorecardTeams.ALL,
            home_away="*",
            stadium=UmpireScorecardTeams.ALL,
            umpire_name="",
            return_pandas=False,
        )
    with pytest.raises(ValueError):
        data = team_umpire_stats_date_range(  # noqa: F841
            start_date="2024-04-01",
            end_date="2024-05-01",
            season_type="postseason_only",
            team=UmpireScorecardTeams.ALL,
            home_away="*",
            stadium=UmpireScorecardTeams.ALL,
            umpire_name="",
            return_pandas=False,
        )
    with pytest.raises(ValueError):
        data = team_umpire_stats_date_range(  # noqa: F841
            start_date="2024-04-01",
            end_date="2024-05-01",
            season_type="*",
            team=UmpireScorecardTeams.ALL,
            home_away="both",
            stadium=UmpireScorecardTeams.ALL,
            umpire_name="",
            return_pandas=False,
        )


def test_team_umpire_stats_date_range_regular():
    data = team_umpire_stats_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        team=UmpireScorecardTeams.ALL,
        home_away="*",
        stadium=UmpireScorecardTeams.ALL,
        umpire_name="",
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 30
    assert data.shape[1] == 13
    assert type(data) is pl.DataFrame

    data = team_umpire_stats_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        team=UmpireScorecardTeams.ALL,
        home_away="*",
        stadium=UmpireScorecardTeams.ALL,
        umpire_name="",
        return_pandas=True,
    )
    assert data is not None
    assert data.shape[0] == 30
    assert data.shape[1] == 13
    assert type(data) is pd.DataFrame


def test_team_umpire_stats_date_range_custom_team():
    data = team_umpire_stats_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        team=UmpireScorecardTeams.WSH,
        home_away="*",
        stadium=UmpireScorecardTeams.ALL,
        umpire_name="",
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 4
    assert data.shape[1] == 13
    assert type(data) is pl.DataFrame


def test_team_umpire_stats_date_range_custom_stadium():
    data = team_umpire_stats_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        team=UmpireScorecardTeams.ALL,
        home_away="*",
        stadium=UmpireScorecardTeams.WSH,
        umpire_name="",
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 3
    assert data.shape[1] == 13
    assert type(data) is pl.DataFrame


def test_team_umpire_stats_date_range_custom_ump_name():
    data = team_umpire_stats_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        team=UmpireScorecardTeams.ALL,
        home_away="*",
        stadium=UmpireScorecardTeams.ALL,
        umpire_name="blagh",
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 0
    assert data.shape[1] == 0
    assert type(data) is pl.DataFrame

    data = team_umpire_stats_date_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        season_type="*",
        team=UmpireScorecardTeams.ALL,
        home_away="*",
        stadium=UmpireScorecardTeams.ALL,
        umpire_name="Vic Carapazza",
        return_pandas=False,
    )
    assert data is not None
    assert data.shape[0] == 4
    assert data.shape[1] == 13
    assert type(data) is pl.DataFrame
