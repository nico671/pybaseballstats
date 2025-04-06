import os
import sys
from datetime import date

import polars as pl
import pytest
from polars.testing import assert_frame_equal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb


def test_illegal_player_lookup():
    with pytest.raises(ValueError):
        pyb.retrosheet.player_lookup(first_name=None, last_name=None)


def test_player_lookup():
    # firstname only
    df1 = pyb.retrosheet.player_lookup(first_name="mookie", last_name="BETTS")
    assert len(df1) > 0
    assert_frame_equal(
        df1,
        pyb.retrosheet.player_lookup(first_name="mookie", last_name="betts"),
    )


def test_player_lookup_strip_accents():
    assert_frame_equal(
        pyb.retrosheet.player_lookup(first_name="mookie", last_name="betts"),
        pyb.retrosheet.player_lookup(
            first_name="möökïë", last_name="bëtts", strip_accents=True
        ),
    )


def test_ejections_data_badinputs():
    with pytest.raises(ValueError):
        pyb.retrosheet.retrosheet_ejections_data(
            start_date="2023-01-01",
        )
    with pytest.raises(ValueError):
        pyb.retrosheet.retrosheet_ejections_data(
            end_date="2023-01-01",
        )
    with pytest.raises(ValueError):
        pyb.retrosheet.retrosheet_ejections_data(
            inning=21,
        )


def test_ejections_data_dates():
    df = pyb.retrosheet.retrosheet_ejections_data(
        start_date="01/01/2023",
        end_date="12/31/2023",
    )
    assert df is not None
    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] == 247
    assert df.shape[1] == 11
    assert df.select(pl.col("DATE").max()).item() == date(2023, 10, 20)
    assert df.select(pl.col("DATE").min()).item() == date(2023, 4, 4)

    df2 = pyb.retrosheet.retrosheet_ejections_data(
        start_date="01/01/2023",
        end_date="12/31/2023",
        return_pandas=True,
    )
    assert df2 is not None
    assert df2.shape[0] == 247
    assert df2.shape[1] == 11
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_ejections_data_ejectee_name():
    df = pyb.retrosheet.retrosheet_ejections_data(
        start_date="01/01/2023",
        end_date="12/31/2023",
        ejectee_name="Harper",
    )
    assert df is not None
    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] == 4
    assert df.shape[1] == 11
    assert df.select(pl.col("EJECTEENAME").first()).item() == "Bryce Harper"
    assert df.select(pl.col("EJECTEE").n_unique()).item() == 1

    df2 = pyb.retrosheet.retrosheet_ejections_data(
        start_date="01/01/2023",
        end_date="12/31/2023",
        ejectee_name="Mike",
    )
    assert df2 is not None
    assert isinstance(df2, pl.DataFrame)
    assert df2.shape[0] == 5
    assert df2.shape[1] == 11
    assert df2.select(pl.col("EJECTEENAME").n_unique()).item() == 5


def test_ejections_data_umpire_name():
    df = pyb.retrosheet.retrosheet_ejections_data(
        start_date="01/01/2023",
        end_date="12/31/2023",
        umpire_name="Hernandez",
    )
    assert df is not None
    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] == 1
    assert df.shape[1] == 11
    assert df.select(pl.col("UMPIRENAME").first()).item() == "Angel Hernandez"
    assert df.select(pl.col("UMPIRE").n_unique()).item() == 1

    df2 = pyb.retrosheet.retrosheet_ejections_data(
        start_date="01/01/2023",
        end_date="12/31/2023",
        umpire_name="Miller",
    )
    assert df2 is not None
    assert isinstance(df2, pl.DataFrame)
    assert df2.shape[0] == 13
    assert df2.shape[1] == 11
    assert df2.select(pl.col("UMPIRENAME").n_unique()).item() == 2


def test_ejections_data_inning():
    df = pyb.retrosheet.retrosheet_ejections_data(
        start_date="01/01/2023",
        end_date="12/31/2023",
        inning=1,
    )
    assert df is not None
    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] == 14
    assert df.shape[1] == 11
    assert df.select(pl.col("INNING").unique()).item() == 1
    assert df.select(pl.col("INNING").n_unique()).item() == 1

    df2 = pyb.retrosheet.retrosheet_ejections_data(
        inning=-1,
    )
    assert df2 is not None
    assert isinstance(df2, pl.DataFrame)
    assert df2.shape[0] == 887
    assert df2.shape[1] == 11
    assert df2.select(pl.col("INNING").n_unique()).item() == 1
    assert df2.select(pl.col("INNING").unique()).item() == -1
