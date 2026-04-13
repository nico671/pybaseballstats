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


# region pitching function tests
def test_standard_pitching():
    with pytest.raises(ValueError):
        bt.standard_pitching(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.standard_pitching(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.standard_pitching(team=None, year=2025)
    df = bt.standard_pitching(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 34
    assert df.shape[1] == 35
    assert df.select(pl.col("name_display").n_unique()).item() == 34
    assert df.select(pl.col("earned_run_avg").min()).item() == 0.0


def test_value_pitching():
    with pytest.raises(ValueError):
        bt.value_pitching(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.value_pitching(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.value_pitching(team=None, year=2025)
    df = bt.value_pitching(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 34
    assert df.shape[1] == 22
    assert df.select(pl.col("name_display").n_unique()).item() == 34
    assert df.select(pl.col("ip").max()).item() == 195.10000610351562


def test_advanced_pitching():
    with pytest.raises(ValueError):
        bt.advanced_pitching(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.advanced_pitching(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.advanced_pitching(team=None, year=2025)
    df = bt.advanced_pitching(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 35
    assert df.shape[1] == 21
    assert df.select(pl.col("name_display").n_unique()).item() == 35
    assert df.select(pl.col("home_run_perc").max()).item() == 16.700000762939453


def test_ratio_pitching():
    with pytest.raises(ValueError):
        bt.ratio_pitching(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.ratio_pitching(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.ratio_pitching(team=None, year=2025)
    df = bt.ratio_pitching(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 34
    assert df.shape[1] == 20
    assert df.select(pl.col("player").n_unique()).item() == 34
    assert df.select(pl.col("home_run_perc").max()).item() == 16.700000762939453
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


def test_batting_against_pitching():
    with pytest.raises(ValueError):
        bt.batting_against_pitching(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.batting_against_pitching(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.batting_against_pitching(team=None, year=2025)
    df = bt.batting_against_pitching(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 34
    assert df.shape[1] == 27
    assert df.select(pl.col("player").n_unique()).item() == 34
    assert df.select(pl.col("PA").max()).item() == 801
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


def test_win_probability_pitching():
    with pytest.raises(ValueError):
        bt.win_probability_pitching(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.win_probability_pitching(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.win_probability_pitching(team=None, year=2025)
    df = bt.win_probability_pitching(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 34
    assert df.shape[1] == 24
    assert df.select(pl.col("player").n_unique()).item() == 34
    assert df.select(pl.col("cli_avg").max()).item() == 3.190000057220459
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


def test_starting_pitching():
    with pytest.raises(ValueError):
        bt.starting_pitching(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.starting_pitching(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.starting_pitching(team=None, year=2025)
    df = bt.starting_pitching(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 11
    assert df.shape[1] == 35
    assert df.select(pl.col("player").n_unique()).item() == 11
    assert df.select(pl.col("GS").max()).item() == 33
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


def test_relief_pitching():
    with pytest.raises(ValueError):
        bt.relief_pitching(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.relief_pitching(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.relief_pitching(team=None, year=2025)
    df = bt.relief_pitching(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 27
    assert df.shape[1] == 33
    assert df.select(pl.col("player").n_unique()).item() == 27
    assert df.select(pl.col("SV").max()).item() == 18
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


def test_baserunning_situational_pitching():
    with pytest.raises(ValueError):
        bt.baserunning_situational_pitching(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.baserunning_situational_pitching(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.baserunning_situational_pitching(team=None, year=2025)
    df = bt.baserunning_situational_pitching(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 34
    assert df.shape[1] == 35
    assert df.select(pl.col("player").n_unique()).item() == 34
    assert df.select(pl.col("SB").max()).item() == 17
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


def test_career_cumulative_pitching():
    with pytest.raises(ValueError):
        bt.career_cumulative_pitching(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.career_cumulative_pitching(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.career_cumulative_pitching(team=None, year=2025)
    df = bt.career_cumulative_pitching(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 37
    assert df.shape[1] == 32
    assert df.select(pl.col("player").n_unique()).item() == 37
    assert df.select(pl.col("G").max()).item() == 727
    assert "League Average" not in df.select(pl.col("player")).to_series().to_list()


# endregion


# region fielding function tests
def test_fielding_standard_all_and_position():
    with pytest.raises(ValueError):
        bt.fielding(team="XXX", year=2023, metric_type="standard", position="all")
    with pytest.raises(ValueError):
        bt.fielding(
            team=bt.BREFTeams.YANKEES,
            year=2025,
            metric_type="standard",
            position="c_baserunning",
        )

    df_all = bt.fielding(
        team=bt.BREFTeams.YANKEES,
        year=2025,
        metric_type="standard",
        position="all",
    )
    assert df_all.shape[0] > 0
    assert df_all.shape[1] > 0

    df_c = bt.fielding(
        team=bt.BREFTeams.YANKEES,
        year=2025,
        metric_type="standard",
        position="c",
    )
    assert df_c.shape[0] > 0
    assert df_c.shape[1] > 0


def test_fielding_advanced_validation_and_position():
    with pytest.raises(ValueError):
        bt.fielding(
            team=bt.BREFTeams.YANKEES,
            year=2025,
            metric_type="advanced",
            position="all",
        )
    with pytest.raises(ValueError):
        bt.fielding(
            team=bt.BREFTeams.YANKEES,
            year=2025,
            metric_type="advanced",
            position="of",
        )

    df = bt.fielding(
        team=bt.BREFTeams.YANKEES,
        year=2025,
        metric_type="advanced",
        position="c",
    )
    assert df.shape[0] > 0
    assert df.shape[1] > 0


def test_fielding_invalid_metric_type():
    with pytest.raises(ValueError):
        bt.fielding(
            team=bt.BREFTeams.YANKEES,
            year=2025,
            metric_type="foo",  # type: ignore[arg-type]
            position="all",
        )


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
