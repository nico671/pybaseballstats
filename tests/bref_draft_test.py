import polars as pl
import pytest
from polars.testing import assert_frame_equal

import pybaseballstats as pyb


def test_amateur_draft_order_badinputs():
    with pytest.raises(ValueError):
        pyb.amateur_draft_order(year=1964, draft_round=1)
    with pytest.raises(ValueError):
        pyb.amateur_draft_order(year=1965, draft_round=0)
    with pytest.raises(ValueError):
        pyb.amateur_draft_order(year=1965, draft_round=101)


def test_amateur_draft_order_regular():
    df = pyb.amateur_draft_order(year=2024, draft_round=1)
    assert df.shape[0] == 39
    assert df.shape[1] == 23
    df2 = pyb.amateur_draft_order(2024, 1, return_pandas=True)
    assert df2.shape[0] == 39
    assert df2.shape[1] == 23
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_franchise_draft_order_badinputs():
    with pytest.raises(ValueError):
        pyb.franchise_draft_order(year=1964, team="ATL")
    with pytest.raises(ValueError):
        pyb.franchise_draft_order(year=1965, team="FAKE")


def test_franchise_draft_order_regular():
    df = pyb.franchise_draft_order(year=2024, team="ATL")
    assert df.shape[0] == 20
    assert df.shape[1] == 23
    assert df.select(pl.col("year_ID")).to_series().to_list() == [2024] * 20
    df2 = pyb.franchise_draft_order(year=2024, team="ATL", return_pandas=True)
    assert df2.shape[0] == 20
    assert df2.shape[1] == 23
    assert df2["year_ID"].tolist() == [2024] * 20
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))
