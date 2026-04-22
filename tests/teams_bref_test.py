import polars as pl
import pytest

import pybaseballstats.bref_teams as bt

pytestmark = [
    pytest.mark.integration,
    pytest.mark.heavy,
    pytest.mark.data_dependent,
]


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
    with pytest.raises(ValueError):
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


def test_batting_orders():
    with pytest.raises(ValueError):
        bt.batting_orders(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.batting_orders(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.batting_orders(team=None, year=2025)
    df = bt.batting_orders(team=bt.BREFTeams.YANKEES, year=2025)
    assert df.shape[0] == 162
    assert df.shape[1] == 27
    assert df.select(pl.col("game_number").max()).item() == 162
    assert df.select(pl.col("batting_9_player").n_unique()).item() == 12


# endregion


# region pitching function tests
def test_pitching_bad_inputs():
    with pytest.raises(ValueError):
        bt.pitching(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.pitching(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.pitching(team=None, year=2025)
    with pytest.raises(ValueError):
        bt.pitching(team=bt.BREFTeams.YANKEES, year=2025, metric_type="foo")


def test_pitching():
    # standard
    df = bt.pitching(team=bt.BREFTeams.YANKEES, year=2025, metric_type="standard")
    assert df.shape[0] == 34
    assert df.shape[1] == 35
    assert df.select(pl.col("player_name").n_unique()).item() == 34
    assert df.select(pl.col("earned_run_avg").min()).item() == 0.0
    assert (
        "League Average" not in df.select(pl.col("player_name")).to_series().to_list()
    )

    # advanced
    df = bt.pitching(team=bt.BREFTeams.YANKEES, year=2025, metric_type="advanced")
    assert df.shape[0] == 34
    assert df.shape[1] == 21
    assert df.select(pl.col("player_name").n_unique()).item() == 34
    assert df.select(pl.col("home_run_perc").max()).item() == 16.700000762939453
    assert (
        "League Average" not in df.select(pl.col("player_name")).to_series().to_list()
    )

    # ratio
    df = bt.pitching(team=bt.BREFTeams.YANKEES, year=2025, metric_type="ratio")
    assert df.shape[0] == 34
    assert df.shape[1] == 19
    assert df.select(pl.col("player_name").n_unique()).item() == 34
    assert df.select(pl.col("home_run_perc").max()).item() == 16.700000762939453
    assert (
        "League Average" not in df.select(pl.col("player_name")).to_series().to_list()
    )
    # cumulative
    df = bt.pitching(team=bt.BREFTeams.YANKEES, year=2025, metric_type="cumulative")
    assert df.shape[0] == 37
    assert df.shape[1] == 32
    assert df.select(pl.col("player_name").n_unique()).item() == 37
    assert df.select(pl.col("W").max()).item() == 112
    assert (
        "League Average" not in df.select(pl.col("player_name")).to_series().to_list()
    )


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


# region batting function tests
def test_batting_bad_inputs():
    with pytest.raises(ValueError):
        bt.batting(team="XXX", year=2023)
    with pytest.raises(ValueError):
        bt.batting(team=bt.BREFTeams.ANGELS, year=1800)
    with pytest.raises(ValueError):
        bt.batting(team=None, year=2025)
    with pytest.raises(ValueError):
        bt.batting(team=bt.BREFTeams.YANKEES, year=2023, metric_type="foo")


def test_batting():
    # standard
    df = bt.batting(team=bt.BREFTeams.YANKEES, year=2025, metric_type="standard")
    assert df.shape[0] == 22
    assert df.shape[1] == 32
    assert df.select(pl.col("player_name").n_unique()).item() == df.shape[0]
    assert df.select(pl.col("war").max()).item() == 9.699999809265137
    assert (
        "League Average" not in df.select(pl.col("player_name")).to_series().to_list()
    )
    # advanced
    df = bt.batting(team=bt.BREFTeams.YANKEES, year=2025, metric_type="advanced")
    assert df.shape[0] == 22
    assert df.shape[1] == 27
    assert df.select(pl.col("player_name").n_unique()).item() == df.shape[0]
    assert df.select(pl.col("roba").max()).item() == 0.460999995470047
    assert (
        "League Average" not in df.select(pl.col("player_name")).to_series().to_list()
    )

    # ratio
    df = bt.batting(team=bt.BREFTeams.YANKEES, year=2025, metric_type="ratio")
    assert df.shape[0] == 20
    assert df.shape[1] == 18
    assert df.select(pl.col("player_name").n_unique()).item() == 20
    assert df.select(pl.col("home_run_perc").max()).item() == 8.5
    assert (
        "League Average" not in df.select(pl.col("player_name")).to_series().to_list()
    )


# endregion
