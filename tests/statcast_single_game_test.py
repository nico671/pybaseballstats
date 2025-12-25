import polars as pl

import pybaseballstats.statcast_single_game as ssg


def test_statcast_single_game_available_game_pks_for_date():
    game_pks = ssg.get_available_game_pks_for_date("2025-08-13")
    assert len(game_pks) == 15
    unique_game_pks = set(game["game_pk"] for game in game_pks)
    assert len(unique_game_pks) == len(game_pks)
    unique_home_teams = set(game["home_team"] for game in game_pks)
    assert len(unique_home_teams) == len(game_pks)
    unique_away_teams = set(game["away_team"] for game in game_pks)
    assert len(unique_away_teams) == len(game_pks)
    game_pks = ssg.get_available_game_pks_for_date("2020-12-25")
    assert len(game_pks) == 0


def test_statcast_single_game_pitch_by_pitch():
    df = ssg.single_game_pitch_by_pitch(game_pk=776759)
    assert not df.is_empty()
    assert df.shape == (338, 118)
    assert df.select(pl.col("game_pk").unique()).item() == 776759
    assert df.select(pl.col("game_date").unique()).item() == "2025-08-13"
    df2 = ssg.single_game_pitch_by_pitch(game_pk=0)
    assert df2.is_empty()
    assert df2.shape == (0, 118)


def test_statcast_single_game_exit_velocity():
    df = ssg.single_game_exit_velocity(game_date="2025-08-13", game_pk=776759)

    assert not df.is_empty()
    assert df.shape == (61, 12)
    assert df.select(pl.col("num_pa").max()).item() == 89
    assert df.select(pl.col("inning").max()).item() == 9
    assert df.select(pl.col("exit_velo").max()).item() == 108.69999694824219
    df2 = ssg.single_game_exit_velocity(game_date="2025-08-13", game_pk=0)

    assert df2.is_empty()
    assert df2.shape == (0, 0)


def test_statcast_single_game_pitch_velocity():
    df = ssg.single_game_pitch_velocity(game_date="2025-08-13", game_pk=776759)
    assert not df.is_empty()
    assert df.shape == (338, 13)
    assert set(df.select(pl.col("pitch_type").unique()).to_series().to_list()) == set(
        [
            "Slow Curve",
            "Changeup",
            "Slider",
            "Splitter",
            "Slurve",
            "Curveball",
            "Cutter",
            "4-Seam Fastball",
            "Sweeper",
            "Sinker",
        ]
    )
    assert df.select(pl.col("game_pitch_number").max()).item() == 338
    assert df.select(pl.col("Inning").max()).item() == 9
    df2 = ssg.single_game_pitch_velocity(game_date="2025-08-13", game_pk=0)
    assert df2.is_empty()
    assert df2.shape == (0, 0)


def test_statcast_single_game_win_probability():
    df = ssg.single_game_win_probability(game_date="2025-08-13", game_pk=776759)

    assert not df.is_empty()
    assert df.shape == (90, 8)
    assert df.select(pl.col("Inning").n_unique()).item() == 18  # 9 innings x top/bottom
    assert df.select(pl.col("Away WP%").max()).item() == 100.0
    assert df.select(pl.col("Home WP%").min()).item() == 0.0

    df2 = ssg.single_game_win_probability(game_date="2025-08-13", game_pk=0)
    assert df2.is_empty()
    assert df2.shape == (0, 0)
