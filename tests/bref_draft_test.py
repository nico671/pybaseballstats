import os
import sys

import polars as pl
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb
from pybaseballstats.bref_draft import BREFTeams


def test_draft_order_by_year_round_badinputs():
    with pytest.raises(ValueError):
        pyb.bref_draft.draft_order_by_year_round(year=1964, draft_round=1)
    with pytest.raises(ValueError):
        pyb.bref_draft.draft_order_by_year_round(year=1965, draft_round=0)
    with pytest.raises(ValueError):
        pyb.bref_draft.draft_order_by_year_round(year=1965, draft_round=61)


def test_draft_order_by_year_round_regular():
    df = pyb.bref_draft.draft_order_by_year_round(year=2024, draft_round=1)
    assert df.shape[0] == 39
    assert df.shape[1] == 25
    assert df.select(pl.col("year_ID").n_unique()).item() == 1
    assert df.select(pl.col("draft_round").n_unique()).item() == 1
    assert df.select(pl.col("overall_pick").n_unique()).item() == df.shape[0]
    assert df.select(pl.col("round_pick").n_unique()).item() == df.shape[0]
    assert df.select(pl.col("player").n_unique()).item() == df.shape[0]


def test_franchise_draft_order_badinputs():
    with pytest.raises(ValueError):
        pyb.bref_draft.franchise_draft_order(year=1964, team=None)
    with pytest.raises(ValueError):
        pyb.bref_draft.franchise_draft_order(year=1965, team="FAKE")


def test_franchise_draft_order_regular():
    df = pyb.bref_draft.franchise_draft_order(year=2024, team=BREFTeams.NATIONALS)
    assert df.shape[0] == 21
    assert df.shape[1] == 24
    assert df.select(pl.col("year_ID").n_unique()).item() == 1
    assert df.select(pl.col("team_ID").n_unique()).item() == 1
    assert df.select(pl.col("overall_pick").n_unique()).item() == df.shape[0]
    assert (
        df.filter(pl.col("signed") == "N").select(pl.col("bonus").n_unique()).item()
        == 1
    )
