import polars as pl

import pybaseballstats.umpire_scorecards as us

# region game_data function tests


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


# endregion

# region umpire_data function tests


def test_umpire_data_general():
    # general test
    df = us.umpire_data(start_date="2025-01-01", end_date="2025-10-01", game_type="R")
    assert df.shape[0] == 92
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").n_unique()).item() == 92
    assert df.select(pl.col("n").min()).item() == 3


def test_umpire_data_game_type():
    # game_type parameter test
    df = us.umpire_data(start_date="2025-01-01", end_date="2025-09-07", game_type="A")
    assert df.shape[0] == 1
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").n_unique()).item() == 1
    assert df.select(pl.col("umpire").unique()).item() == "Dan Iassogna"
    df = us.umpire_data(start_date="2025-07-01", end_date="2025-07-07", game_type="P")
    assert df.shape[0] == 0
    assert df.shape[1] == 0


def test_umpire_data_team_params():
    # just focus_team
    df = us.umpire_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        game_type="R",
        focus_team=us.UmpireScorecardTeams.BRAVES,
    )
    assert df.shape[0] == 82
    assert df.shape[1] == 17
    assert df.select(pl.col("n").min()).item() == 1
    assert df.select(pl.col("n").max()).item() == 5
    assert df.select(pl.col("umpire").n_unique()).item() == 82

    # focus_team only away
    df = us.umpire_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        game_type="R",
        focus_team=us.UmpireScorecardTeams.BRAVES,
        focus_team_home_away="a",
    )
    assert df.shape[0] == 59
    assert df.shape[1] == 17
    assert df.select(pl.col("n").min()).item() == 1
    assert df.select(pl.col("n").max()).item() == 3
    assert df.select(pl.col("umpire").n_unique()).item() == 59

    # focus_team away with opponent_team
    df = us.umpire_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        game_type="R",
        focus_team=us.UmpireScorecardTeams.BRAVES,
        focus_team_home_away="a",
        opponent_team=us.UmpireScorecardTeams.NATIONALS,
    )
    assert df.shape[0] == 6
    assert df.shape[1] == 17
    assert df.select(pl.col("n").min()).item() == 1
    assert df.select(pl.col("n").max()).item() == 1
    assert df.select(pl.col("umpire").n_unique()).item() == 6


def test_umpire_data_umpire_name_param():
    # umpire_name param test
    df = us.umpire_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        game_type="R",
        umpire_name="Dan Iassogna",
    )
    assert df.shape[0] == 1
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").unique()).item() == "Dan Iassogna"
    assert df.select(pl.col("n").unique()).item() == 29


def test_umpire_data_min_games_param():
    # min_games param test
    df = us.umpire_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        game_type="R",
        min_games_called=20,
    )
    assert df.shape[0] == 81
    assert df.shape[1] == 17
    assert df.select(pl.col("n").min()).item() == 20
    assert df.select(pl.col("umpire").n_unique()).item() == 81


# endregion


# region team_data function tests


def test_team_data_general():
    # general test
    df = us.team_data(start_date="2025-01-01", end_date="2025-10-30", game_type="R")
    assert df.shape[0] == 30
    assert df.shape[1] == 19
    assert df.select(pl.col("team").n_unique()).item() == 30


def test_team_data_game_type():
    df = us.team_data(start_date="2025-07-01", end_date="2025-07-07", game_type="P")
    assert df.shape[0] == 0
    assert df.shape[1] == 0

    df = us.team_data(start_date="2025-07-01", end_date="2025-10-07", game_type="P")
    assert df.shape[0] == 12  # number of teams that made the playoffs
    assert df.shape[1] == 19
    assert df.select(pl.col("team").n_unique()).item() == 12


def test_team_data_focus_team():
    df = us.team_data(
        start_date="2025-01-01",
        end_date="2025-10-30",
        game_type="R",
        focus_team=us.UmpireScorecardTeams.ANGELS,
    )
    assert df.shape[0] == 1
    assert df.shape[1] == 19
    assert df.select(pl.col("team").unique()).item() == "LAA"


# endregion
