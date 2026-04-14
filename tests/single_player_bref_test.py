import polars as pl
import pytest

from pybaseballstats import bref_single_player as bsp

pytestmark = [pytest.mark.integration, pytest.mark.data_dependent]


def test_single_player_batting_invalid_metric_type():
    with pytest.raises(ValueError, match="Invalid metric type: invalid_metric"):
        bsp.single_player_batting("suzukse01", metric_type="invalid_metric")


def test_single_player_batting_valid_metric_types():
    df = bsp.single_player_batting("suzukse01", metric_type="standard")
    assert df.shape[0] >= 4
    assert df.shape[1] == 33
    assert df.head(4).select(pl.col("team_name").n_unique()).item() == 1
    assert df.head(4).select(pl.col("team_name").unique()).item() == "CHC"
    assert df.head(4).select(pl.col("age").min()).item() == 27
    assert df.head(4).select(pl.col("age").max()).item() == 30

    df = bsp.single_player_batting("suzukse01", metric_type="ratio")
    assert df.shape[0] >= 4
    assert df.shape[1] == 20
    assert df.head(4).select(pl.col("team_ID").n_unique()).item() == 1
    assert df.head(4).select(pl.col("team_ID").unique()).item() == "CHC"
    assert df.head(4).select(pl.col("age").min()).item() == 27
    assert (
        df.head(4).select(pl.col("home_run_fperc").max()).item() == 13.100000381469727
    )

    df = bsp.single_player_batting("suzukse01", metric_type="cumulative")
    assert df.shape[0] >= 4
    assert df.shape[1] == 26
    assert df.head(4).select(pl.col("G").n_unique()).item() == 4
    assert df.head(4).select(pl.col("age").min()).item() == 27
    assert df.head(4).select(pl.col("age").max()).item() == 30


def test_single_player_pitching_bad_inputs():
    with pytest.raises(ValueError):
        bsp.single_player_pitching("suzukse01", metric_type="invalid_metric")


def test_single_player_pitching_valid_metric_types():
    df = bsp.single_player_pitching("imanash01", metric_type="standard")
    assert df.shape[0] >= 2
    assert df.shape[1] == 36
    assert df.head(2).select(pl.col("team_name").n_unique()).item() == 1
    assert df.head(2).select(pl.col("team_name").unique()).item() == "CHC"
    assert df.head(2).select(pl.col("age").min()).item() == 30
    assert df.head(2).select(pl.col("age").max()).item() == 31

    df = bsp.single_player_pitching("imanash01", metric_type="ratio")
    assert df.shape[0] >= 2
    assert df.shape[1] == 22
    assert df.head(2).select(pl.col("team_ID").n_unique()).item() == 1
    assert df.head(2).select(pl.col("team_ID").unique()).item() == "CHC"
    assert df.head(2).select(pl.col("age").min()).item() == 30
    assert df.head(2).select(pl.col("GIDP_perc").max()).item() == 7.0

    df = bsp.single_player_pitching("imanash01", metric_type="cumulative")
    assert df.shape[0] >= 2
    assert df.shape[1] == 31
    assert df.head(2).select(pl.col("year_ID").max()).item() == 2025
    assert df.head(2).select(pl.col("SHO").max()).item() == 0


def test_single_player_fielding_bad_inputs():
    with pytest.raises(ValueError):
        bsp.single_player_fielding("suzukse01", metric_type="invalid_metric")
    with pytest.raises(ValueError):
        bsp.single_player_fielding("suzukse01", metric_type="advanced_at_position")
    with pytest.raises(ValueError):
        bsp.single_player_fielding(
            "suzukse01", metric_type="advanced_at_position", position="invalid_position"
        )
    with pytest.raises(ValueError):
        bsp.single_player_fielding("suzukse01", metric_type="standard", position="p")


def test_single_player_fielding():
    df = bsp.single_player_fielding("sheldsc01", metric_type="standard")
    assert df.shape[0] == 25
    assert df.shape[1] == 30
    assert df.select(pl.col("year_id").max()).item() == 2001
    assert df.select(pl.col("team_name").n_unique()).item() == 2

    df = bsp.single_player_fielding("sheldsc01", metric_type="appearances")
    assert df.shape[0] == 5
    assert df.shape[1] == 21
    assert df.select(pl.col("year_id").max()).item() == 2001
    assert df.select(pl.col("team_name").n_unique()).item() == 2
    assert df.select(pl.col("games_at_pr").max()).item() == 5

    df = bsp.single_player_fielding("sheldsc01", metric_type="sabermetric")
    assert df.shape[0] == 21
    assert df.shape[1] == 27
    assert df.select(pl.col("year_ID").max()).item() == 2001
    assert df.select(pl.col("team_ID").n_unique()).item() == 2
    assert df.select(pl.col("pos").n_unique()).item() == 9

    df = bsp.single_player_fielding(
        "sheldsc01", metric_type="advanced_at_position", position="lf"
    )
    assert df.shape[0] == 2
    assert df.shape[1] == 42
    assert df.select(pl.col("year_ID").max()).item() == 2001
    assert (
        df.select(pl.col("team_ID").n_unique()).item() == 1
    )  # only played left field for one team
    assert df.select(pl.col("PA_with_bip_perc").max()).item() == 73.0
