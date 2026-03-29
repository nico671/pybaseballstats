import polars as pl
import pytest

import pybaseballstats.umpire_scorecards as us

# region game_data function tests


def test_game_data_general():
    with pytest.raises(ValueError):
        us.game_data(start_date=None, end_date="2023-07-07")
    with pytest.raises(ValueError):
        us.game_data(start_date="2023-07-01", end_date=None)
    with pytest.raises(ValueError):
        us.game_data(start_date="2023-07-07", end_date="2023-07-01")
    with pytest.raises(ValueError):
        us.game_data(start_date="2023-07-01", end_date="2023-07-07", game_type="X")
    with pytest.raises(ValueError):
        us.game_data(
            start_date="2014-07-01",
            end_date="2023-07-07",
            # focus_team_home_away="x",
        )
    with pytest.raises(ValueError):
        us.game_data(
            start_date="2023-07-01",
            end_date="2023-07-07",
            focus_team=us.UmpireScorecardTeams.ANGELS,
            focus_team_home_away="x",
        )
    with pytest.raises(AssertionError):
        us.game_data(
            start_date="2023-07-01",
            end_date="2023-07-07",
            focus_team=None,
            focus_team_home_away="h",
        )
    with pytest.raises(AssertionError):
        us.game_data(
            start_date="2023-07-01",
            end_date="2023-07-07",
            focus_team=us.UmpireScorecardTeams.ANGELS,
            opponent_team=None,
        )
    with pytest.raises(ValueError):
        us.game_data(
            start_date="2023-07-01",
            end_date="2023-07-07",
            focus_team=us.UmpireScorecardTeams.ANGELS,
            focus_team_home_away="h",
            opponent_team=us.UmpireScorecardTeams.ANGELS,
        )
    # general test
    df = us.game_data(start_date="2026-01-01", end_date="2026-03-27")
    assert df.shape[0] == 20
    assert df.shape[1] == 47
    print(df.columns)
    assert df.select(pl.col("date").min()).item() == "2026-03-25"  # start of season
    assert df.select(pl.col("date").max()).item() == "2026-03-27"


def test_game_data_game_type():
    # game_type parameter test
    df = us.game_data(
        start_date="2026-01-01", end_date="2026-03-27", game_type="R"
    )  # regular season
    assert df.shape[0] == 20
    assert df.shape[1] == 47
    assert df.select(pl.col("date").min()).item() == "2026-03-25"  # start of season
    assert df.select(pl.col("date").max()).item() == "2026-03-27"
    assert df.select(pl.col("type").unique()).item() == "R"
    df = us.game_data(
        start_date="2026-01-01", end_date="2026-03-27", game_type="P"
    )  # postseason
    assert df.shape[0] == 0
    assert df.shape[1] == 0


def test_game_data_team_filtering():
    # focus_team, focus_team_home_away, opponent_team parameter test
    df = us.game_data(
        start_date="2026-01-01",
        end_date="2026-03-27",
        focus_team=us.UmpireScorecardTeams.GIANTS,
        focus_team_home_away="h",
    )
    assert df.shape[0] == 2
    assert df.shape[1] == 47
    assert df.select(pl.col("home_team").n_unique()).item() == 1
    assert df.select(pl.col("home_team").unique()).item() == "SF"
    df = us.game_data(
        start_date="2023-04-01",
        end_date="2023-07-07",
        focus_team=us.UmpireScorecardTeams.ANGELS,
        focus_team_home_away="h",
        opponent_team=us.UmpireScorecardTeams.RANGERS,
    )
    assert df.shape[0] == 3
    assert df.shape[1] == 47
    assert df.select(pl.col("home_team").n_unique()).item() == 1
    assert df.select(pl.col("home_team").unique()).item() == "LAA"
    assert df.select(pl.col("away_team").n_unique()).item() == 1
    assert df.select(pl.col("away_team").unique()).item() == "TEX"

    df = us.game_data(
        start_date="2023-04-01",
        end_date="2023-07-07",
        focus_team=us.UmpireScorecardTeams.ANGELS,
        focus_team_home_away="a",
        opponent_team=us.UmpireScorecardTeams.RANGERS,
    )
    assert df.shape[0] == 3
    assert df.shape[1] == 47
    assert df.select(pl.col("away_team").n_unique()).item() == 1
    assert df.select(pl.col("away_team").unique()).item() == "LAA"
    assert df.select(pl.col("home_team").n_unique()).item() == 1
    assert df.select(pl.col("home_team").unique()).item() == "TEX"


def test_game_data_umpire_filtering():
    # umpire param test
    df = us.game_data(
        start_date="2023-04-01",
        end_date="2023-07-07",
        umpire_name="Alan Porter",
    )
    assert df.shape[0] == 17
    assert df.shape[1] == 47
    assert df.select(pl.col("umpire").n_unique()).item() == 1
    assert df.select(pl.col("umpire").unique()).item() == "Alan Porter"


# endregion

# region umpire_data function tests


def test_umpire_data_general():
    # general test
    df = us.umpire_data(start_date="2025-01-01", end_date="2025-10-01", game_type="R")
    assert df.shape[0] == 92
    assert df.shape[1] == 20
    assert df.select(pl.col("umpire").n_unique()).item() == 92
    assert df.select(pl.col("n").min()).item() == 3


def test_umpire_data_game_type():
    # game_type parameter test
    df = us.umpire_data(start_date="2025-01-01", end_date="2025-09-07", game_type="A")
    assert df.shape[0] == 1
    assert df.shape[1] == 20
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
    assert df.shape[1] == 20
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
    assert df.shape[1] == 20
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
    assert df.shape[1] == 20
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
    assert df.shape[1] == 20
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
    assert df.shape[1] == 20
    assert df.select(pl.col("n").min()).item() == 20
    assert df.select(pl.col("umpire").n_unique()).item() == 81


# endregion


# region team_data function tests


def test_team_data_general():
    # general test
    df = us.team_data(start_date="2025-01-01", end_date="2025-10-30", game_type="R")
    assert df.shape[0] == 30
    assert df.shape[1] == 25
    assert df.select(pl.col("team").n_unique()).item() == 30


def test_team_data_game_type():
    df = us.team_data(start_date="2025-07-01", end_date="2025-07-07", game_type="P")
    assert df.shape[0] == 0
    assert df.shape[1] == 0

    df = us.team_data(start_date="2025-07-01", end_date="2025-10-07", game_type="P")
    assert df.shape[0] == 12  # number of teams that made the playoffs
    assert df.shape[1] == 25
    assert df.select(pl.col("team").n_unique()).item() == 12


def test_team_data_focus_team():
    df = us.team_data(
        start_date="2025-01-01",
        end_date="2025-10-30",
        game_type="R",
        focus_team=us.UmpireScorecardTeams.ANGELS,
    )
    assert df.shape[0] == 1
    assert df.shape[1] == 25
    assert df.select(pl.col("team").unique()).item() == "LAA"


# endregion


# region player_data function tests


def test_player_data_general():
    with pytest.raises(ValueError):
        us.player_data(start_date=None, end_date="2025-10-01", player_type="P")
    with pytest.raises(ValueError):
        us.player_data(start_date="2025-01-01", end_date=None, player_type="P")
    with pytest.raises(ValueError):
        us.player_data(
            start_date="01-01-2025",
            end_date="2025-10-01",
            player_type="P",
        )
    with pytest.raises(ValueError):
        us.player_data(
            start_date="2025-01-01",
            end_date="10-01-2025",
            player_type="P",
        )
    with pytest.raises(ValueError):
        us.player_data(
            start_date="2025-10-01",
            end_date="2025-01-01",
            player_type="P",
        )
    with pytest.raises(ValueError):
        us.player_data(
            start_date="2014-01-01",
            end_date="2025-10-01",
            player_type="P",
        )
    with pytest.raises(ValueError):
        us.player_data(
            start_date="2027-01-01",
            end_date="2027-03-01",
            player_type="P",
        )
    with pytest.raises(ValueError):
        us.player_data(
            start_date="2025-01-01",
            end_date="2025-10-01",
            player_type="P",
            game_type="X",
        )
    with pytest.raises(ValueError):
        us.player_data(
            start_date="2025-01-01",
            end_date="2025-10-01",
            player_type="X",
        )
    with pytest.raises(AssertionError):
        us.player_data(
            start_date="2025-01-01",
            end_date="2025-10-01",
            player_type="P",
            team=None,
        )

    # general test
    df = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="P",
        game_type="R",
    )
    assert df.shape[0] == 872
    assert df.shape[1] == 11
    assert df.select(pl.col("player_id").n_unique()).item() == 872
    assert df.select(pl.col("n_pitches").min()).item() == 1
    assert df.select(pl.col("n_pitches").max()).item() == 1759


def test_player_data_game_type():
    # game_type parameter test
    df = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="P",
        game_type="R",
    )
    assert df.shape[0] == 872
    assert df.shape[1] == 11

    df = us.player_data(
        start_date="2025-07-01",
        end_date="2025-10-07",
        player_type="P",
        game_type="P",
    )
    assert df.shape[0] == 0
    assert df.shape[1] == 0


def test_player_data_player_type():
    # player_type parameter test
    df = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="P",
        game_type="R",
    )
    assert df.shape[0] == 872
    assert df.shape[1] == 11
    assert df.select(pl.col("player_id").n_unique()).item() == 872
    assert df.select(pl.col("n_pitches").min()).item() == 1

    df = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="C",
        game_type="R",
    )
    assert df.shape[0] == 111
    assert df.shape[1] == 11
    assert df.select(pl.col("player_id").n_unique()).item() == 111
    assert df.select(pl.col("n_pitches").min()).item() == 15

    df = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="B",
        game_type="R",
    )
    assert df.shape[0] == 673
    assert df.shape[1] == 11
    assert df.select(pl.col("player_id").n_unique()).item() == 673
    assert df.select(pl.col("n_pitches").min()).item() == 1


def test_player_data_team_filtering():
    # team parameter test
    df_all = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="P",
        game_type="R",
        team=us.UmpireScorecardTeams.ALL,
    )
    df_braves = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="P",
        game_type="R",
        team=us.UmpireScorecardTeams.BRAVES,
    )

    assert df_all.shape[0] == 872
    assert df_all.shape[1] == 11
    assert df_braves.shape[0] == 46
    assert df_braves.shape[1] == 11
    assert df_braves.shape[0] < df_all.shape[0]
    assert df_braves.select(pl.col("player_id").n_unique()).item() == 46
    assert df_braves.select(pl.col("n_pitches").min()).item() == 10

    df_angels_batters = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="B",
        game_type="R",
        team=us.UmpireScorecardTeams.ANGELS,
    )
    assert df_angels_batters.shape[0] == 29
    assert df_angels_batters.shape[1] == 11
    assert df_angels_batters.select(pl.col("player_id").n_unique()).item() == 29
    assert df_angels_batters.select(pl.col("n_pitches").min()).item() == 8


# endregion
