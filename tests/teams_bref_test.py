import polars as pl
import pytest

import pybaseballstats.bref_teams as bt
from pybaseballstats.utils.bref_utils import resolve_bref_team_code


# region random function tests
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


# endregion


# region helper function tests
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


# endregion


# region batting function tests
def test_standard_batting():
    with pytest.raises(ValueError):
        bt.standard_batting(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.standard_batting(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.standard_batting(team=None, year=2025)
    df = bt.standard_batting(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 22
    assert df.shape[1] == 32
    assert df.select(pl.col("name_display").n_unique()).item() == 22
    assert df.select(pl.col("war").max()).item() == 9.699999809265137


def test_value_batting():
    with pytest.raises(ValueError):
        bt.value_batting(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.value_batting(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.value_batting(team=None, year=2025)
    df = bt.value_batting(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 22
    assert df.shape[1] == 20
    assert df.select(pl.col("name_display").n_unique()).item() == 22
    assert df.select(pl.col("pa").max()).item() == 679


def test_advanced_batting():
    with pytest.raises(ValueError):
        bt.advanced_batting(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.advanced_batting(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.advanced_batting(team=None, year=2025)
    df = bt.advanced_batting(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 22
    assert df.shape[1] == 27
    assert df.select(pl.col("name_display").n_unique()).item() == 22
    assert df.select(pl.col("roba").max()).item() == 0.460999995470047


def test_sabermetric_batting():
    with pytest.raises(ValueError):
        bt.sabermetric_batting(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.sabermetric_batting(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.sabermetric_batting(team=None, year=2025)
    df = bt.sabermetric_batting(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 22
    assert df.shape[1] == 25
    assert df.select(pl.col("player").n_unique()).item() == 22
    assert df.select(pl.col("outs_made").max()).item() == 453
    print(df.select(pl.col("player")).to_series().to_list())
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


def test_ratio_batting():
    with pytest.raises(ValueError):
        bt.ratio_batting(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.ratio_batting(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.ratio_batting(team=None, year=2025)
    df = bt.ratio_batting(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 20
    assert df.shape[1] == 18
    assert df.select(pl.col("player").n_unique()).item() == 20
    assert df.select(pl.col("home_run_perc").max()).item() == 8.5


def test_win_probability_batting():
    with pytest.raises(ValueError):
        bt.win_probability_batting(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.win_probability_batting(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.win_probability_batting(team=None, year=2025)
    df = bt.win_probability_batting(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 20
    assert df.shape[1] == 23
    assert df.select(pl.col("player").n_unique()).item() == 20
    assert df.select(pl.col("cli_avg").max()).item() == 1.4700000286102295
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


def test_baserunning_batting():
    with pytest.raises(ValueError):
        bt.baserunning_batting(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.baserunning_batting(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.baserunning_batting(team=None, year=2025)
    df = bt.baserunning_batting(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 20
    assert df.shape[1] == 34
    assert df.select(pl.col("player").n_unique()).item() == 20
    assert df.select(pl.col("CS_2").max()).item() == 5
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


def test_situational_batting():
    with pytest.raises(ValueError):
        bt.situational_batting(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.situational_batting(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.situational_batting(team=None, year=2025)
    df = bt.situational_batting(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 20
    assert df.shape[1] == 39
    assert df.select(pl.col("player").n_unique()).item() == 20
    assert df.select(pl.col("PA_with_platoon_adv_perc").max()).item() == 100.0
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


def test_pitches_batting():
    with pytest.raises(ValueError):
        bt.pitches_batting(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.pitches_batting(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.pitches_batting(team=None, year=2025)
    df = bt.pitches_batting(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 20
    assert df.shape[1] == 31
    assert df.select(pl.col("player").n_unique()).item() == 20
    assert (
        df.select(pl.col("all_strikes_swinging_perc").max()).item() == 81.80000305175781
    )
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


def test_career_cumulative_batting():
    with pytest.raises(ValueError):
        bt.career_cumulative_batting(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.career_cumulative_batting(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.career_cumulative_batting(team=None, year=2025)
    df = bt.career_cumulative_batting(team=bt.BREFTeams.YANKEES, year=2023)
    assert df.shape[0] == 54
    assert df.shape[1] == 27
    assert df.select(pl.col("player").n_unique()).item() == 54
    assert df.select(pl.col("G").max()).item() == 1635
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


# endregion
