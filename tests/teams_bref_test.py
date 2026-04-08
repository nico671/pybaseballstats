import polars as pl
import pytest

import pybaseballstats.bref_teams as bt
from pybaseballstats.consts.bref_consts import resolve_bref_team_code


def test_schedule_results():
    with pytest.raises(ValueError):
        bt.game_by_game_schedule_results(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.game_by_game_schedule_results(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.game_by_game_schedule_results(team=None, year=2025)
    df = bt.game_by_game_schedule_results(team=bt.BREFTeams.ANGELS, year=2023)
    assert df.shape[0] == 162
    assert df.shape[1] == 21
    assert df.select(pl.col("team_ID").unique()).item() == "LAA"
    assert (
        df.with_columns(pl.col("team_game").cast(pl.Int128))
        .select(pl.col("team_game").max())
        .item()
        == 162
    )


def test_roster_and_appearances():
    with pytest.raises(ValueError):
        bt.roster_and_appearances(team="XXX", year=2023)
    with pytest.raises(AssertionError):
        bt.roster_and_appearances(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.roster_and_appearances(team=None, year=2025)
    df = bt.roster_and_appearances(team=bt.BREFTeams.ANGELS, year=2023)
    assert df.shape[0] == 66
    assert df.shape[1] == 27
    assert (
        df.with_columns(pl.col("games_started_all").cast(pl.Int64))
        .select(pl.col("games_started_all").max())
        .item()
        == 135
    )
    assert df.select(pl.col("name_display").n_unique()).item() == 66


def test_resolve_team_code_switches():
    assert resolve_bref_team_code(bt.BREFTeams.ANGELS, 2004) == "ANA"
    assert resolve_bref_team_code(bt.BREFTeams.ANGELS, 2005) == "LAA"
    assert resolve_bref_team_code(bt.BREFTeams.MARLINS, 2011) == "FLA"
    assert resolve_bref_team_code(bt.BREFTeams.MARLINS, 2012) == "MIA"
    assert resolve_bref_team_code(bt.BREFTeams.RAYS, 2007) == "TBD"
    assert resolve_bref_team_code(bt.BREFTeams.RAYS, 2008) == "TBR"
    assert resolve_bref_team_code(bt.BREFTeams.NATIONALS, 2004) == "MON"
    assert resolve_bref_team_code(bt.BREFTeams.NATIONALS, 2005) == "WSN"
    assert resolve_bref_team_code(bt.BREFTeams.ATHLETICS, 2024) == "OAK"
    assert resolve_bref_team_code(bt.BREFTeams.ATHLETICS, 2025) == "ATH"
    assert resolve_bref_team_code(bt.BREFTeams.BRAVES, 1952) == "BSN"
    assert resolve_bref_team_code(bt.BREFTeams.BRAVES, 1953) == "MLN"
    assert resolve_bref_team_code(bt.BREFTeams.BRAVES, 1966) == "ATL"
