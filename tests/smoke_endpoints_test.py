import polars as pl
import pytest

import pybaseballstats.bref_teams as bt
import pybaseballstats.retrosheet as rs
import pybaseballstats.statcast_single_game as ssg
import pybaseballstats.umpire_scorecards as us

pytestmark = pytest.mark.smoke


def test_smoke_bref_schedule_endpoint_contract():
    """Minimal BREF smoke check for endpoint reachability + schema shape."""
    df = bt.game_by_game_schedule_results(team=bt.BREFTeams.YANKEES, year=2025)
    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] > 0
    assert {"team_ID", "team_game", "date_game"}.issubset(set(df.columns))


def test_smoke_statcast_single_game_endpoint_contract():
    """Minimal Statcast smoke check via available game PK endpoint."""
    game_pks = ssg.get_available_game_pks_for_date("2025-08-13")
    assert isinstance(game_pks, list)
    assert len(game_pks) > 0
    required_keys = {"game_pk", "home_team", "away_team"}
    assert required_keys.issubset(set(game_pks[0].keys()))


def test_smoke_retrosheet_lookup_contract():
    """Minimal Retrosheet smoke check for player lookup endpoint and columns."""
    df = rs.player_lookup(first_name="Babe", last_name="Ruth")
    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] > 0
    assert {"key_bbref", "key_retro", "name_last"}.issubset(set(df.columns))


def test_smoke_umpire_scorecards_contract():
    """Minimal Umpire Scorecards smoke check using a short date window."""
    df = us.game_data(start_date="2026-03-25", end_date="2026-03-27")
    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] > 0
    assert {"date", "umpire", "home_team", "away_team"}.issubset(set(df.columns))
