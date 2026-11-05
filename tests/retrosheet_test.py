from datetime import datetime

import polars as pl
import pytest
from live_assertions import assert_live_frame

import pybaseballstats.retrosheet as rs
from pybaseballstats._utils import retrosheet_utils
from pybaseballstats._utils.retrosheet_utils import _clear_people_cache


def setup_module():
    """Clear cache before tests."""
    _clear_people_cache()


def test_player_lookup_errors():
    with pytest.raises(ValueError):
        rs.player_lookup()
    with pytest.raises(ValueError):
        rs.player_lookup(first_name=None, last_name=None)
    with pytest.raises(TypeError):
        rs.player_lookup(first_name=123, last_name="Ruth")
    with pytest.raises(TypeError):
        rs.player_lookup(first_name="Babe", last_name=456)


@pytest.mark.live
def test_player_lookup():
    df = rs.player_lookup(first_name="Bábé", last_name="Rúth", strip_accents=True)

    assert df.height == 1
    assert_live_frame(
        df,
        columns=(
            "key_fangraphs",
            "name_first",
            "name_last",
            "key_mlbam",
            "key_retro",
            "key_bbref",
        ),
        unique_by=("key_retro",),
    )
    assert df.select(pl.col("key_fangraphs").unique()).item() == 1011327
    assert df.select(pl.col("name_first").unique()).item() == "Babe"
    assert df.select(pl.col("name_last").unique()).item() == "Ruth"
    assert df.select(pl.col("key_mlbam").unique()).item() == 121578
    assert df.select(pl.col("key_retro").unique()).item() == "ruthb101"
    assert df.select(pl.col("key_bbref").unique()).item() == "ruthba01"


@pytest.mark.live
def test_ejections_data_errors():
    with pytest.raises(ValueError):
        rs.ejections_data(start_date="2023-04-01", end_date="10/01/2023")
    with pytest.raises(ValueError):
        rs.ejections_data(start_date="04/01/2023", end_date="2023-10-01")
    with pytest.raises(ValueError):
        rs.ejections_data(start_date="10/01/2023", end_date="04/01/2023")
    with pytest.raises(ValueError):
        rs.ejections_data(inning=-2)
    with pytest.raises(ValueError):
        rs.ejections_data(inning=21)


@pytest.mark.live
def test_ejections_data_just_dates():
    df = rs.ejections_data(start_date="04/01/2023", end_date="10/01/2023")
    assert_live_frame(
        df,
        columns=("DATE", "EJECTEENAME", "UMPIRENAME", "UMPIRE", "TEAM", "INNING"),
        counts=("INNING",),
    )
    assert (
        df.select(pl.col("DATE").min()).item()
        >= datetime.strptime("04/01/2023", "%m/%d/%Y").date()
    )
    assert (
        df.select(pl.col("DATE").max()).item()
        <= datetime.strptime("10/01/2023", "%m/%d/%Y").date()
    )
    assert df["UMPIRE"].null_count() == 0
    assert df["TEAM"].null_count() == 0
    assert df["INNING"].null_count() == 0


@pytest.mark.live
def test_ejection_data_ejectee_name():
    df = rs.ejections_data(
        start_date="04/01/2016", end_date="10/01/2025", ejectee_name="Machado"
    )
    assert_live_frame(
        df,
        columns=("DATE", "EJECTEENAME", "UMPIRENAME", "UMPIRE", "TEAM", "INNING"),
        counts=("INNING",),
    )
    assert (
        df.select(pl.col("DATE").min()).item()
        >= datetime.strptime("04/01/2016", "%m/%d/%Y").date()
    )
    assert (
        df.select(pl.col("DATE").max()).item()
        <= datetime.strptime("10/01/2025", "%m/%d/%Y").date()
    )
    assert df.select(pl.col("EJECTEENAME").n_unique()).item() == 1
    assert df.select(pl.col("EJECTEENAME").unique()).item() == "Manny Machado"
    assert df["UMPIRE"].null_count() == 0
    assert df["TEAM"].null_count() == 0
    df = rs.ejections_data(
        start_date="04/01/2016", end_date="10/01/2025", ejectee_name="sdvjbs"
    )
    assert df.shape[0] == 0
    assert {"DATE", "EJECTEENAME", "UMPIRENAME", "INNING"} <= set(df.columns)


@pytest.mark.live
def test_ejection_data_umpire_name():
    df = rs.ejections_data(
        start_date="04/01/2016", end_date="10/01/2025", umpire_name="Alfonso Marquez"
    )
    assert_live_frame(
        df,
        columns=("DATE", "EJECTEENAME", "UMPIRENAME", "UMPIRE", "TEAM", "INNING"),
        counts=("INNING",),
    )
    assert (
        df.select(pl.col("DATE").min()).item()
        >= datetime.strptime("04/01/2016", "%m/%d/%Y").date()
    )
    assert (
        df.select(pl.col("DATE").max()).item()
        <= datetime.strptime("10/01/2025", "%m/%d/%Y").date()
    )
    assert df.select(pl.col("UMPIRE").n_unique()).item() == 1
    assert df.select(pl.col("UMPIRENAME").unique()).item() == "Alfonso Marquez"
    assert df["EJECTEENAME"].null_count() == 0
    df = rs.ejections_data(
        start_date="04/01/2016", end_date="10/01/2025", umpire_name="sdvjbs"
    )
    assert df.shape[0] == 0
    assert {"DATE", "EJECTEENAME", "UMPIRENAME", "INNING"} <= set(df.columns)


@pytest.mark.live
def test_ejection_data_inning():
    df = rs.ejections_data(start_date="04/01/2016", end_date="10/01/2025", inning=7)
    assert_live_frame(
        df,
        columns=("DATE", "EJECTEENAME", "UMPIRENAME", "UMPIRE", "TEAM", "INNING"),
        counts=("INNING",),
    )
    assert (
        df.select(pl.col("DATE").min()).item()
        >= datetime.strptime("04/01/2016", "%m/%d/%Y").date()
    )
    assert (
        df.select(pl.col("DATE").max()).item()
        <= datetime.strptime("10/01/2025", "%m/%d/%Y").date()
    )
    assert df.select(pl.col("INNING").n_unique()).item() == 1
    assert df.select(pl.col("INNING").unique()).item() == 7


def test_strip_accents():
    assert retrosheet_utils._strip_accents("Bábé Rúth") == "Babe Ruth"
