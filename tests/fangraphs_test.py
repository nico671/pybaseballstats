import os
import sys

import polars as pl
import pytest
from polars.testing import assert_frame_equal, assert_series_equal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb


def test_fangraphs_batting_range_bad_inputs():
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            start_year=2024,
            end_year=2024,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date=None,
            end_date=None,
            start_year=None,
            end_year=None,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="04-01-2024",
            end_date="05-01-2024",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-05-01",
            end_date="2024-03-01",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_year=2024,
            end_year=2023,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_pa="q",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_pa=-1,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            fielding_position="notenum",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            active_roster_only="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            team="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            league="not al nl or empty",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=13,
            max_age=12,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=13,
            max_age=25,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=25,
            max_age=70,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            batting_hand="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=["invalid"],
        )


def test_fangraphs_batting_range_dates():
    df = pyb.fangraphs.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
    )
    assert df is not None
    assert df.shape[0] == 199
    assert df.shape[1] == 316
    assert df.select(pl.col("Season").n_unique()).item() == 1
    assert df.select(pl.col("Season").unique().first()).item() == 2024
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 199
    df1 = pyb.fangraphs.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        return_pandas=True,
    )
    assert df1 is not None
    assert df1.shape[0] == 199
    assert df1.shape[1] == 316
    assert_frame_equal(df, pl.DataFrame(df1, schema=df.schema))


def test_fangraphs_batting_range_years():
    df = pyb.fangraphs.fangraphs_batting_range(
        start_year=2023,
        end_year=2024,
    )
    assert df is not None
    assert df.shape[0] == 1801
    assert df.shape[1] == 322
    assert df.select(pl.col("SeasonMin").n_unique()).item() == 2
    assert df.select(pl.col("SeasonMax").n_unique()).item() == 2
    assert df.select(pl.col("SeasonMin").min().first()).item() == 2023
    assert df.select(pl.col("SeasonMax").max().first()).item() == 2024
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 1801


def test_fangraphs_batting_range_minpa():
    df = pyb.fangraphs.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        min_pa=10,
    )
    assert df is not None
    assert df.shape[0] == 339
    assert df.shape[1] == 316
    assert df.select(pl.col("PA").min()).item() >= 10
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 339
    df1 = pyb.fangraphs.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        min_pa="y",
    )
    assert df1 is not None
    assert df1.shape[0] == 199
    assert df1.shape[1] == 316
    assert df1.select(pl.col("xMLBAMID").n_unique()).item() == 199


def test_fangraphs_batting_range_fielding_position():
    df = pyb.fangraphs.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        fielding_position=pyb.fangraphs.FangraphsBattingPosTypes.CATCHER,
    )
    assert df is not None
    assert df.shape[0] == 16
    assert df.shape[1] == 316
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 16
    assert df.select(pl.col("Pos").n_unique()).item() == 1
    assert df.select(pl.col("Pos").first()).item() == "C"


def test_fangraphs_batting_range_team():
    df = pyb.fangraphs.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        team=pyb.fangraphs.FangraphsTeams.NATIONALS,
    )
    assert df is not None
    assert df.shape[0] == 5
    assert df.shape[1] == 316
    assert df.select(pl.col("Team").n_unique()).item() == 1
    assert df.select(pl.col("Team").first()).item() == "WSN"


def test_fangraphs_batting_range_league():
    df = pyb.fangraphs.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        league="al",
    )
    assert df is not None
    assert df.shape[0] == 97
    assert df.shape[1] == 316
    assert df.select(pl.col("Team").n_unique()).item() <= 15


def test_fangraphs_batting_range_age():
    df = pyb.fangraphs.fangraphs_batting_range(
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
    df = pyb.fangraphs.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        batting_hand="R",
    )
    assert df is not None
    assert df.shape[0] == 107
    assert df.shape[1] == 316
    assert df.select(pl.col("Bats").n_unique()).item() == 1
    assert df.select(pl.col("Bats").first()).item() == "R"
    df1 = pyb.fangraphs.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        batting_hand="S",
    )
    assert df1 is not None
    assert df1.shape[0] == 19
    assert df1.shape[1] == 316
    assert df1.select(pl.col("Bats").n_unique()).item() == 1
    assert df1.select(pl.col("Bats").first()).item() == "B"


def test_fangraphs_batting_range_split_seasons():
    df = pyb.fangraphs.fangraphs_batting_range(
        start_year=2016,
        end_year=2024,
        split_seasons=True,
        min_pa=10,
    )
    assert df is not None
    assert df.shape == (6026, 322)
    filtered = df.filter(pl.col("Name") == "Aaron Judge").sort("Season")
    assert filtered.shape == (9, 322)
    assert filtered.select(pl.col("Season").n_unique()).item() == 9
    assert filtered.select(pl.col("Season").unique().first()).item() == 2016
    assert filtered.select(pl.col("Season").unique().last()).item() == 2024


def test_fangraphs_pitching_range_badinputs():
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            start_year=2024,
            end_year=2024,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date=None,
            end_date=None,
            start_year=None,
            end_year=None,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="04-01-2024",
            end_year=2024,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-05-01",
            end_date="2024-03-01",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_year=2024,
            end_year=2023,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_ip="q",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_ip=-1,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            team="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            league="not al nl or empty",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=13,
            max_age=12,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=13,
            max_age=25,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            min_age=25,
            max_age=70,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            pitching_hand="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            starter_reliever="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_pitching_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=["invalid"],
        )


def test_fangraphs_pitching_range_dates():
    df = pyb.fangraphs.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
    )
    assert df is not None
    assert df.shape[0] == 89
    assert df.shape[1] == 380
    assert df.select(pl.col("season").n_unique()).item() == 1
    assert df.select(pl.col("season").unique().first()).item() == 2024
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 89
    df1 = pyb.fangraphs.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        return_pandas=True,
    )
    assert df1 is not None
    assert df1.shape[0] == 89
    assert df1.shape[1] == 380
    assert_frame_equal(df, pl.DataFrame(df1, schema=df.schema))


def test_fangraphs_pitching_range_years():
    df = pyb.fangraphs.fangraphs_pitching_range(
        start_year=2023,
        end_year=2024,
    )
    assert df is not None
    assert df.shape[0] == 1107
    assert df.shape[1] == 383
    assert df.select(pl.col("SeasonMin").n_unique()).item() == 2
    assert df.select(pl.col("SeasonMax").n_unique()).item() == 2
    assert df.select(pl.col("SeasonMin").min().first()).item() == 2023
    assert df.select(pl.col("SeasonMax").max().first()).item() == 2024
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 1107


def test_fangraphs_pitching_range_minip():
    df = pyb.fangraphs.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        min_ip=10,
    )
    assert df is not None
    assert df.shape[0] == 73
    assert df.shape[1] == 380
    assert df.select(pl.col("IP").min()).item() >= 10
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 73


def test_fangraphs_pitching_range_certain_stat_types():
    df = pyb.fangraphs.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        stat_types=[
            pyb.fangraphs.FangraphsPitchingStatType.ADVANCED,
            pyb.fangraphs.FangraphsPitchingStatType.STANDARD,
        ],
    )
    assert df is not None
    assert df.shape[0] == 89
    assert df.shape[1] == 49
    assert df.select(pl.col("season").n_unique()).item() == 1
    assert df.select(pl.col("season").unique().first()).item() == 2024
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 89


def test_fangraphs_pitching_range_team():
    df = pyb.fangraphs.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        team=pyb.fangraphs.FangraphsTeams.NATIONALS,
    )
    assert df is not None
    assert df.shape[0] == 3
    assert df.shape[1] == 380
    assert df.select(pl.col("Team").n_unique()).item() == 1
    assert df.select(pl.col("Team").first()).item() == "WSN"


def test_fangraphs_pitching_range_league():
    df = pyb.fangraphs.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        league="al",
    )
    assert df is not None
    assert df.shape[0] == 43
    assert df.shape[1] == 380
    assert df.select(pl.col("Team").n_unique()).item() <= 15


def test_fangraphs_pitching_range_age():
    df = pyb.fangraphs.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        min_age=20,
        max_age=25,
    )
    assert df is not None
    assert df.shape[0] == 11
    assert df.shape[1] == 380
    assert df.select(pl.col("Age").min()).item() >= 20
    assert df.select(pl.col("Age").max()).item() <= 25
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 11


def test_fangraphs_pitching_range_pitching_hand():
    df = pyb.fangraphs.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        pitching_hand="R",
    )
    assert df is not None
    assert df.shape[0] == 63
    assert df.shape[1] == 380
    assert df.select(pl.col("Throws").n_unique()).item() == 1
    assert df.select(pl.col("Throws").first()).item() == "R"
    df1 = pyb.fangraphs.fangraphs_pitching_range(
        start_year=1973,
        end_year=2025,
        pitching_hand="S",
        min_ip=0,
    )
    assert df1 is not None
    assert df1.shape[0] == 1
    assert df1.shape[1] == 383
    assert df1.select(pl.col("Throws").n_unique()).item() == 1
    assert df1.select(pl.col("Throws").first()).item() == "B"


def test_fangraphs_pitching_range_starter_reliever():
    df = pyb.fangraphs.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        starter_reliever="sta",
    )
    assert df is not None
    assert df.shape[0] == 87
    assert df.shape[1] == 380
    assert df.select(pl.col("GS").sum()).item() > 0
    assert_series_equal(
        df.select(pl.col("GS")).to_series(),
        df.select(pl.col("G")).to_series(),
        check_names=False,
    )
    df1 = pyb.fangraphs.fangraphs_pitching_range(
        start_date="2024-04-01",
        end_date="2024-04-10",
        starter_reliever="rel",
    )
    assert df1 is not None
    assert df1.shape[0] == 195
    assert df1.shape[1] == 380
    assert df1.select(pl.col("GS").sum()).item() == 0
    assert df1.select(pl.col("G").sum()).item() > 0


def test_fangraphs_pitching_range_split_seasons():
    df = pyb.fangraphs.fangraphs_pitching_range(
        start_year=2016,
        end_year=2024,
        split_seasons=True,
        min_ip=10,
    )
    assert df is not None
    assert df.shape == (5595, 383)
    filtered = df.filter(pl.col("Name") == "Aaron Nola").sort("Season")
    assert filtered.shape == (9, 383)
    assert filtered.select(pl.col("Season").n_unique()).item() == 9
    assert filtered.select(pl.col("Season").unique().first()).item() == 2016
    assert filtered.select(pl.col("Season").unique().last()).item() == 2024


def test_fangraphs_fielding_range_bad_inputs():
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_fielding_range(
            start_year=None,
            end_year=None,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_fielding_range(
            start_year=2024,
            end_year=2023,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_fielding_range(
            start_year=2024,
            end_year=2024,
            min_inn="q",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_fielding_range(
            start_year=2024,
            end_year=2024,
            min_inn=-1,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_fielding_range(
            start_year=2024,
            end_year=2024,
            fielding_position="notenum",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_fielding_range(
            start_year=2024,
            end_year=2024,
            active_roster_only="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_fielding_range(
            start_year=2024,
            end_year=2024,
            team="invalid",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_fielding_range(
            start_year=2024,
            end_year=2024,
            league="not al nl or empty",
        )
    with pytest.raises(ValueError):
        pyb.fangraphs.fangraphs_fielding_range(
            start_year=2024,
            end_year=2024,
            fielding_position="notenum",
        )


def test_fangraphs_fielding_range_years():
    df = pyb.fangraphs.fangraphs_fielding_range(
        start_year=2023,
        end_year=2024,
    )
    assert df is not None
    assert df.shape[0] == 93
    assert df.shape[1] == 73
    assert df.select(pl.col("SeasonMin").min().first()).item() == 2023
    assert df.select(pl.col("SeasonMax").max().first()).item() == 2024
    assert df.select(pl.col("xMLBAMID").n_unique()).item() == 93

    df1 = pyb.fangraphs.fangraphs_fielding_range(
        start_year=2023,
        end_year=2024,
        return_pandas=True,
    )
    assert df1 is not None
    assert df1.shape[0] == 93
    assert df1.shape[1] == 73
    assert_frame_equal(df, pl.DataFrame(df1, schema=df.schema))


def test_fangraphs_fielding_range_min_inn():
    df = pyb.fangraphs.fangraphs_fielding_range(
        start_year=2024,
        end_year=2024,
        min_inn=10,
    )
    assert df is not None
    assert df.shape[0] == 1794
    assert df.shape[1] == 73
    assert df.select(pl.col("Inn").min()).item() >= 10
    df1 = pyb.fangraphs.fangraphs_fielding_range(
        start_year=2024,
        end_year=2024,
        min_inn="y",
    )
    assert df1 is not None
    assert df1.shape[0] == 112
    assert df1.shape[1] == 73
    assert df1.select(pl.col("xMLBAMID").n_unique()).item() == 112
    assert df1.select(pl.col("Inn").min()).item() >= 899


def test_fangraphs_fielding_range_stat_types():
    df = pyb.fangraphs.fangraphs_fielding_range(
        start_year=2024,
        end_year=2024,
        stat_types=[
            pyb.fangraphs.FangraphsFieldingStatType.ADVANCED,
            pyb.fangraphs.FangraphsFieldingStatType.STANDARD,
        ],
    )
    assert df is not None
    assert df.shape[0] == 112
    assert df.shape[1] == 52
    for stat in [
        "Made0",
        "Prob0",
        "Made10",
        "Prob10",
        "Made40",
        "Prob40",
        "Made60",
        "Prob60",
        "Made90",
        "Prob90",
        "Made100",
        "Prob100",
        "CStrikes",
        "CFraming",
        "OAA",
        "rFRP",
        "aFRP",
        "bFRP",
        "tFRP",
        "fFRP",
        "FRP",
    ]:
        assert stat not in df.columns
    assert df.select(pl.col("Season").n_unique()).item() == 1
    assert df.select(pl.col("Season").unique().first()).item() == 2024


def test_fangraphs_fielding_range_team():
    df = pyb.fangraphs.fangraphs_fielding_range(
        start_year=2024,
        end_year=2024,
        team=pyb.fangraphs.FangraphsTeams.NATIONALS,
    )
    assert df is not None
    assert df.shape[0] == 4
    assert df.shape[1] == 73
    assert df.select(pl.col("TeamNameAbb").n_unique()).item() == 1
    assert df.select(pl.col("TeamNameAbb").first()).item() == "WSN"


def test_fangraphs_fielding_range_league():
    df = pyb.fangraphs.fangraphs_fielding_range(
        start_year=2024,
        end_year=2024,
        league="al",
    )
    assert df is not None
    assert df.shape[0] == 54
    assert df.shape[1] == 73
    assert (
        df.filter(pl.col("TeamNameAbb") != "2 Tms")
        .filter(pl.col("TeamNameAbb") != "3 Tms")
        .select(pl.col("TeamNameAbb").n_unique())
        .item()
        <= 15
    )


def test_fangraphs_fielding_range_pos():
    df = pyb.fangraphs.fangraphs_fielding_range(
        start_year=2024,
        end_year=2024,
        fielding_position=pyb.fangraphs.FangraphsBattingPosTypes.CATCHER,
    )
    assert df is not None
    assert df.shape[0] == 11
    assert df.shape[1] == 73
    assert df.select(pl.col("Pos").n_unique()).item() == 1
    assert df.select(pl.col("Pos").first()).item() == "C"
    df1 = pyb.fangraphs.fangraphs_fielding_range(
        start_year=2024,
        end_year=2024,
        fielding_position=pyb.fangraphs.FangraphsBattingPosTypes.FIRST_BASE,
    )
    assert df1 is not None
    assert df1.shape[0] == 17
    assert df1.shape[1] == 73
    assert df1.select(pl.col("Pos").n_unique()).item() == 1
    assert df1.select(pl.col("Pos").first()).item() == "1B"
