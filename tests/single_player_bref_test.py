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


def test_single_player_standard_fielding():
    df = bsp.single_player_standard_fielding("suzukse01")
    assert df.shape[0] >= 15
    assert df.shape[1] == 25
    assert df.head(15).select(pl.col("team_name").n_unique()).item() == 1
    assert df.head(15).select(pl.col("team_name").unique()).item() == "CHC"
    assert df.head(15).select(pl.col("age").min()).item() == 27
    assert df.head(15).select(pl.col("age").max()).item() == 30
    assert df.columns == [
        "year_id",
        "age",
        "team_name",
        "comp_name",
        "position",
        "games",
        "games_started",
        "cg",
        "innings",
        "chances",
        "po",
        "assists",
        "errors",
        "dp",
        "fielding_perc",
        "fielding_perc_lg",
        "tz_runs_total",
        "tz_runs_total_per_year",
        "drs_total",
        "drs_total_per_year",
        "range_factor_per_nine",
        "range_factor_per_nine_lg",
        "range_factor_per_game",
        "range_factor_per_game_lg",
        "awards",
    ]


def test_single_player_sabermetric_fielding():
    df = bsp.single_player_sabermetric_fielding("suzukse01")
    assert df.shape[0] >= 4
    assert df.shape[1] == 27
    assert df.head(4).select(pl.col("team_ID").n_unique()).item() == 1
    assert df.head(4).select(pl.col("team_ID").unique()).item() == "CHC"
    assert df.select(pl.col("age").min()).item() == 27
    assert df.columns == [
        "year_ID",
        "age",
        "team_ID",
        "pos",
        "lg_ID",
        "tz_runs_total",
        "tz_runs_total_per_season",
        "tz_runs_field",
        "tz_runs_field_home",
        "tz_runs_field_road",
        "tz_runs_infield",
        "tz_runs_outfield",
        "tz_runs_catcher",
        "bis_runs_total",
        "bis_runs_total_per_season",
        "bis_runs_field",
        "bis_runs_infield",
        "bis_runs_good_plays",
        "bis_runs_air",
        "bis_runs_range",
        "bis_runs_throwing",
        "bis_runs_bunts",
        "bis_runs_outfield",
        "bis_runs_catcher_er",
        "bis_runs_catcher_sb",
        "bis_runs_catcher_sz",
        "bis_runs_pitcher_sb",
    ]


def test_single_player_standard_pitching():
    df = bsp.single_player_standard_pitching("imanash01")
    assert df.shape[0] >= 2
    assert df.shape[1] == 36
    assert df.head(2).select(pl.col("team_name").n_unique()).item() == 1
    assert df.head(2).select(pl.col("team_name").unique()).item() == "CHC"
    assert df.head(2).select(pl.col("age").min()).item() == 30
    assert df.head(2).select(pl.col("age").max()).item() == 31
    assert df.columns == [
        "year_id",
        "age",
        "team_name",
        "comname",
        "war",
        "w",
        "l",
        "win_loss_perc",
        "earned_run_avg",
        "g",
        "gs",
        "gf",
        "cg",
        "sho",
        "sv",
        "ip",
        "h",
        "r",
        "er",
        "hr",
        "bb",
        "ibb",
        "so",
        "hbp",
        "bk",
        "wp",
        "bfp",
        "earned_run_avg_plus",
        "fip",
        "whip",
        "hits_per_nine",
        "hr_per_nine",
        "bb_per_nine",
        "so_per_nine",
        "strikeouts_per_base_on_balls",
        "awards",
    ]


def test_single_player_value_pitching():
    df = bsp.single_player_value_pitching("imanash01")
    assert df.shape[0] >= 2
    assert df.shape[1] == 23
    assert df.head(2).select(pl.col("team_name").n_unique()).item() == 1
    assert df.head(2).select(pl.col("team_name").unique()).item() == "CHC"
    assert df.head(2).select(pl.col("age").min()).item() == 30
    assert df.head(2).select(pl.col("age").max()).item() == 31
    assert df.columns == [
        "year_id",
        "age",
        "team_name",
        "comname",
        "ip",
        "g",
        "gs",
        "r",
        "ra9",
        "ra9_opp",
        "ra9_def",
        "ra9_role",
        "ra9_extras",
        "ppf_custom",
        "ra9_avg_pitcher",
        "raa",
        "waa",
        "waa_adj",
        "war",
        "rar",
        "waa_win_perc",
        "waa_win_perc_162",
        "awards",
    ]


def test_single_player_advanced_pitching():
    df = bsp.single_player_advanced_pitching("imanash01")
    assert df.shape[0] >= 2
    assert df.shape[1] == 23
    assert df.head(2).select(pl.col("team_name").n_unique()).item() == 1
    assert df.head(2).select(pl.col("team_name").unique()).item() == "CHC"
    assert df.head(2).select(pl.col("age").min()).item() == 30
    assert df.head(2).select(pl.col("age").max()).item() == 31
    assert df.columns == [
        "year_id",
        "age",
        "team_name",
        "comname",
        "ip",
        "batting_avg",
        "onbase_perc",
        "slugging_perc",
        "onbase_plus_slugging",
        "batting_avg_bip",
        "home_run_perc",
        "strikeout_perc",
        "base_on_balls_perc",
        "avg_exit_velo",
        "hard_hit_perc",
        "ld_perc",
        "gb_perc",
        "fb_perc",
        "gb_fb_ratio",
        "wpa_def",
        "cwpa_def",
        "baseout_runs",
        "awards",
    ]
