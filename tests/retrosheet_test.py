from datetime import datetime

import polars as pl
import pytest

import pybaseballstats.retrosheet as rs
from pybaseballstats.utils.retrosheet_utils import _clear_people_cache


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
    with pytest.raises(ValueError):
        rs.player_lookup(first_name="Babe", fuzzy=True, fuzzy_threshold=150)


def test_player_lookup():
    # # normal test looking up babe ruth
    # df = rs.player_lookup(first_name="Babe", last_name="Ruth")
    # assert df.shape[0] == 1
    # assert df.shape[1] == 6
    # assert df.select(pl.col("key_fangraphs").unique()).item() == 1011327
    # assert df.select(pl.col("name_first").unique()).item() == "babe"
    # assert df.select(pl.col("name_last").unique()).item() == "ruth"
    # assert df.select(pl.col("key_mlbam").unique()).item() == 121578
    # assert df.select(pl.col("key_retro").unique()).item() == "ruthb101"
    # assert df.select(pl.col("key_bbref").unique()).item() == "ruthba01"
    # test looking up babe ruth with accents stripped
    df = rs.player_lookup(first_name="Bábé", last_name="Rúth", strip_accents=True)

    assert df.shape[0] == 1
    assert df.shape[1] == 10
    assert df.select(pl.col("key_fangraphs").unique()).item() == 1011327
    assert df.select(pl.col("name_first").unique()).item() == "Babe"
    assert df.select(pl.col("name_last").unique()).item() == "Ruth"
    assert df.select(pl.col("key_mlbam").unique()).item() == 121578
    assert df.select(pl.col("key_retro").unique()).item() == "ruthb101"
    assert df.select(pl.col("key_bbref").unique()).item() == "ruthba01"


def test_player_lookup_fuzzy():
    # test looking up babe ruth with fuzzy matching
    df = rs.player_lookup(
        first_name="Babe", last_name="Ruth", fuzzy=True, fuzzy_threshold=80
    )

    assert df.shape[0] >= 32
    assert df.shape[1] == 11
    assert (
        df.select(pl.col("key_fangraphs").unique()).to_series().to_list().count(1011327)
        == 1
    )
    assert (
        df.select(pl.col("name_first").unique()).to_series().to_list().count("Babe")
        == 1
    )
    assert (
        df.select(pl.col("name_last").unique()).to_series().to_list().count("Ruth") == 1
    )
    assert (
        df.select(pl.col("key_mlbam").unique()).to_series().to_list().count(121578) == 1
    )
    assert (
        df.select(pl.col("key_retro").unique()).to_series().to_list().count("ruthb101")
        == 1
    )
    assert (
        df.select(pl.col("key_bbref").unique()).to_series().to_list().count("ruthba01")
        == 1
    )
    df = rs.player_lookup(
        first_name=None, last_name="Miller", fuzzy=True, fuzzy_threshold=80
    )
    assert df.shape[0] >= 102
    assert df.shape[1] == 11


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


def test_ejections_data_just_dates():
    df = rs.ejections_data(start_date="04/01/2023", end_date="10/01/2023")
    assert df.shape[0] == 243
    assert df.shape[1] == 11
    assert (
        df.select(pl.col("DATE").min()).item()
        >= datetime.strptime("04/01/2023", "%m/%d/%Y").date()
    )
    assert (
        df.select(pl.col("DATE").max()).item()
        <= datetime.strptime("10/01/2023", "%m/%d/%Y").date()
    )
    assert df.select(pl.col("UMPIRE").n_unique()).item() == 78
    assert df.select(pl.col("TEAM").n_unique()).item() == 30
    assert df.select(pl.col("INNING").n_unique()).item() == 12


def test_ejection_data_ejectee_name():
    df = rs.ejections_data(
        start_date="04/01/2016", end_date="10/01/2025", ejectee_name="Machado"
    )
    assert df.shape[0] == 8
    assert df.shape[1] == 11
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
    assert df.select(pl.col("UMPIRE").n_unique()).item() == 8
    assert df.select(pl.col("TEAM").n_unique()).item() == 2
    df = rs.ejections_data(
        start_date="04/01/2016", end_date="10/01/2025", ejectee_name="sdvjbs"
    )
    assert df.shape[0] == 0
    assert df.shape[1] == 11


def test_ejection_data_umpire_name():
    df = rs.ejections_data(
        start_date="04/01/2016", end_date="10/01/2025", umpire_name="Alfonso Marquez"
    )
    assert df.shape[0] == 22
    assert df.shape[1] == 11
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
    assert df.select(pl.col("EJECTEENAME").n_unique()).item() == 21
    df = rs.ejections_data(
        start_date="04/01/2016", end_date="10/01/2025", umpire_name="sdvjbs"
    )
    assert df.shape[0] == 0
    assert df.shape[1] == 11


def test_ejection_data_inning():
    df = rs.ejections_data(start_date="04/01/2016", end_date="10/01/2025", inning=7)
    assert df.shape[0] == 248
    assert df.shape[1] == 11
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
