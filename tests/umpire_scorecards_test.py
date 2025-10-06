import polars as pl

import pybaseballstats.umpire_scorecards as us

# game_data tests


def test_game_data_general():
    # general test
    df = us.game_data(start_date="2023-07-01", end_date="2023-07-07")
    assert df.shape[0] == 98
    assert df.shape[1] == 32
    print(df.columns)
    assert df.select(pl.col("date").min()).item() == "2023-07-01"
    assert df.select(pl.col("date").max()).item() == "2023-07-07"


def test_game_data_game_type():
    # game_type parameter test
    df = us.game_data(
        start_date="2023-07-01", end_date="2023-07-07", game_type="R"
    )  # regular season
    assert df.shape[0] == 98
    assert df.shape[1] == 32
    assert df.select(pl.col("date").min()).item() == "2023-07-01"
    assert df.select(pl.col("date").max()).item() == "2023-07-07"
    assert df.select(pl.col("type").unique()).item() == "R"
    df = us.game_data(
        start_date="2023-07-01", end_date="2023-07-07", game_type="P"
    )  # postseason
    assert df.shape[0] == 0
    assert df.shape[1] == 0


def test_game_data_team_filtering():
    # focus_team, focus_team_home_away, opponent_team parameter test
    df = us.game_data(
        start_date="2023-04-01",
        end_date="2023-07-07",
        focus_team=us.UmpireScorecardTeams.ANGELS,
        focus_team_home_away="h",
    )
    assert df.shape[0] == 43
    assert df.shape[1] == 32
    assert df.select(pl.col("home_team").n_unique()).item() == 1
    assert df.select(pl.col("home_team").unique()).item() == "LAA"
    df = us.game_data(
        start_date="2023-04-01",
        end_date="2023-07-07",
        focus_team=us.UmpireScorecardTeams.ANGELS,
        focus_team_home_away="h",
        opponent_team=us.UmpireScorecardTeams.RANGERS,
    )
    assert df.shape[0] == 3
    assert df.shape[1] == 32
    assert df.select(pl.col("home_team").n_unique()).item() == 1
    assert df.select(pl.col("home_team").unique()).item() == "LAA"
    assert df.select(pl.col("away_team").n_unique()).item() == 1
    assert df.select(pl.col("away_team").unique()).item() == "TEX"


def test_game_data_umpire_filtering():
    # umpire param test
    df = us.game_data(
        start_date="2023-04-01",
        end_date="2023-07-07",
        umpire_name="Alan Porter",
    )
    assert df.shape[0] == 17
    assert df.shape[1] == 32
    assert df.select(pl.col("umpire").n_unique()).item() == 1
    assert df.select(pl.col("umpire").unique()).item() == "Alan Porter"
