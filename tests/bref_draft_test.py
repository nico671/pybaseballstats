import polars as pl
import pytest

import pybaseballstats.bref_draft as bd


def test_draft_order_by_year_round():
    with pytest.raises(ValueError):
        bd.draft_order_by_year_round(year=1964, draft_round=1)
    with pytest.raises(ValueError):
        bd.draft_order_by_year_round(year=2023, draft_round=0)
    with pytest.raises(ValueError):
        bd.draft_order_by_year_round(year=2023, draft_round=61)
    df = bd.draft_order_by_year_round(year=2023, draft_round=1)
    assert df.shape[0] == 39
    assert df.shape[1] == 24
    assert df.select(pl.col("year_ID").unique()).item() == 2023
    assert df.select(pl.col("draft_round").unique()).item() == 1
    assert df.select(pl.col("overall_pick").min()).item() == 1
    assert df.select(pl.col("overall_pick").max()).item() == 39


def test_franchise_draft_order():
    with pytest.raises(ValueError):
        bd.franchise_draft_order(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bd.franchise_draft_order(team=bd.BREFTeams.ANGELS, year=1964)
    df = bd.franchise_draft_order(team=bd.BREFTeams.ANGELS, year=2023)
    assert df.shape[0] == 19
    assert df.shape[1] == 23
    assert df.select(pl.col("year_ID").unique()).item() == 2023
    assert df.select(pl.col("team_ID").unique()).item() == "Angels"
    assert df.select(pl.col("overall_pick").min()).item() == 11
    assert df.select(pl.col("overall_pick").max()).item() == 594
    assert df.select(pl.col("draft_round").min()).item() == 1
    assert df.select(pl.col("draft_round").max()).item() == 20
