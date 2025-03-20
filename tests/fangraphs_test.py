import os
import sys

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from pybaseballstats.utils.consts import FangraphsBattingPosTypes

# 15th test
# Setup path to import pybaseballstats
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb


def test_fangraphs_batting_range_bad_inputs():
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            start_year=2024,
            end_year=2024,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date=None,
            end_date=None,
            start_year=None,
            end_year=None,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="04-01-2024",
            end_date="05-01-2024",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-05-01",
            end_date="2024-03-01",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_year=2024,
            end_year=2023,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_pa="q",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_pa=-1,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            fielding_position="notenum",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            active_roster_only="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            team="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            league="not al nl or empty",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=13,
            max_age=12,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=13,
            max_age=25,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=25,
            max_age=70,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            batting_hand="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=["invalid"],
        )


def test_fangraphs_batting_range_dates():
    df = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
    )
    assert df is not None
    assert df.shape[0] == 199
    assert df.shape[1] == 316
    assert df.select(pl.col("Season").n_unique()).item() == 1
    assert df.select(pl.col("Season").unique().first()).item() == 2024
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 199
    df1 = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        return_pandas=True,
    )
    assert df1 is not None
    assert df1.shape[0] == 199
    assert df1.shape[1] == 316
    assert_frame_equal(df, pl.DataFrame(df1, schema=df.schema))


def test_fangraphs_batting_range_years():
    df = pyb.fangraphs_batting_range(
        start_year=2023,
        end_year=2024,
    )
    assert df is not None
    assert df.shape[0] == 115
    assert df.shape[1] == 322
    assert df.select(pl.col("SeasonMin").n_unique()).item() == 1
    assert df.select(pl.col("SeasonMax").n_unique()).item() == 1
    assert df.select(pl.col("SeasonMin").min().first()).item() == 2023
    assert df.select(pl.col("SeasonMax").max().first()).item() == 2024
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 115


def test_fangraphs_batting_range_minpa():
    df = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        min_pa=10,
    )
    assert df is not None
    assert df.shape[0] == 339
    assert df.shape[1] == 316
    assert df.select(pl.col("PA").min()).item() >= 10
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 339
    df1 = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        min_pa="y",
    )
    assert df1 is not None
    assert df1.shape[0] == 199
    assert df1.shape[1] == 316
    assert df1.select(pl.col("xMLBAMID").n_unique()).item() == 199


def test_fangraphs_batting_range_fielding_position():
    df = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        fielding_position=FangraphsBattingPosTypes.CATCHER,
    )
    assert df is not None
    assert df.shape[0] == 16
    assert df.shape[1] == 316
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 16
    assert df.select(pl.col("Pos").n_unique()).item() == 1
    assert df.select(pl.col("Pos").first()).item() == "C"


def test_fangraphs_batting_range_active_roster_only():
    df = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        active_roster_only=True,
    )
    assert df is not None
    assert df.shape[0] == 177
    assert df.shape[1] == 316


def test_fangraphs_batting_range_team():
    df = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        team=pyb.FangraphsTeams.NATIONALS,
    )
    assert df is not None
    assert df.shape[0] == 5
    assert df.shape[1] == 316
    assert df.select(pl.col("Team").n_unique()).item() == 1
    assert df.select(pl.col("Team").first()).item() == "WSN"


def test_fangraphs_batting_range_league():
    df = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        league="al",
    )
    assert df is not None
    assert df.shape[0] == 97
    assert df.shape[1] == 316
    assert df.select(pl.col("Team").n_unique()).item() <= 15


def test_fangraphs_batting_range_age():
    df = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        min_age=20,
        max_age=25,
    )
    assert df is not None
    assert df.shape[0] == 54
    assert df.shape[1] == 316
    assert df.select(pl.col("Age").min()).item() >= 20
    assert df.select(pl.col("Age").max()).item() <= 25
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 54


def test_fangraphs_batting_range_handedness():
    df = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        batting_hand="R",
    )
    assert df is not None
    assert df.shape[0] == 107
    assert df.shape[1] == 316
    assert df.select(pl.col("Bats").n_unique()).item() == 1
    assert df.select(pl.col("Bats").first()).item() == "R"
    df1 = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        batting_hand="S",
    )
    assert df1 is not None
    assert df1.shape[0] == 19
    assert df1.shape[1] == 316
    assert df1.select(pl.col("Bats").n_unique()).item() == 1
    assert df1.select(pl.col("Bats").first()).item() == "B"


def test_fangraphs_pitching_range_badinputs():
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            start_year=2024,
            end_year=2024,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date=None,
            end_date=None,
            start_year=None,
            end_year=None,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="04-01-2024",
            end_year=2024,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-05-01",
            end_date="2024-03-01",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_year=2024,
            end_year=2023,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_ip="q",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_ip=-1,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            team="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            league="not al nl or empty",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=13,
            max_age=12,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=13,
            max_age=25,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=25,
            max_age=70,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            pitching_hand="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            starter_reliever="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=["invalid"],
        )


def test_fangraphs_pitching_range_dates():
    df = pyb.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
    )
    assert df is not None
    assert df.shape[0] == 89
    assert df.shape[1] == 380
    assert df.select(pl.col("season").n_unique()).item() == 1
    assert df.select(pl.col("season").unique().first()).item() == 2024
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 89
    df1 = pyb.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        return_pandas=True,
    )
    assert df1 is not None
    assert df1.shape[0] == 89
    assert df1.shape[1] == 380
    assert_frame_equal(df, pl.DataFrame(df1, schema=df.schema))


def test_fangraphs_pitching_range_years():
    df = pyb.fangraphs_pitching_range(
        start_year=2023,
        end_year=2024,
    )
    assert df is not None
    assert df.shape[0] == 46
    assert df.shape[1] == 383
    assert df.select(pl.col("SeasonMin").n_unique()).item() == 1
    assert df.select(pl.col("SeasonMax").n_unique()).item() == 1
    assert df.select(pl.col("SeasonMin").min().first()).item() == 2023
    assert df.select(pl.col("SeasonMax").max().first()).item() == 2024
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 46
