import polars as pl
import pytest
from polars.testing import assert_frame_equal

import pybaseballstats as pyb


# Test umpire_scorecard_games_date_range
def test_umpire_scorecard_games_date_range_badinputs():
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_games_date_range(
            start_date=None,
            end_date="2024-04-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_games_date_range(start_date="2024-04-01", end_date=None)
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_games_date_range(
            start_date="2024-04-01",
            end_date="2024-03-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_games_date_range(
            start_date="2014-04-01",
            end_date="2024-05-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_games_date_range(
            start_date="2024-04-01",
            end_date="9999-04-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_games_date_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            game_type="not_a_game_type",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_games_date_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            focus_team=pyb.UmpireScorecardTeams.ALL,
            focus_team_home_away="not_a_home_away",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_games_date_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            focus_team=pyb.UmpireScorecardTeams.NATIONALS,
            opponent_team=pyb.UmpireScorecardTeams.NATIONALS,
        )


def test_umpire_scorecard_games_date_range():
    df = pyb.umpire_scorecard_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
    )
    assert df is not None
    assert df.shape[0] == 397
    assert df.shape[1] == 32
    assert df.select(pl.col("date").min()).item() == "2024-04-01"
    assert df.select(pl.col("date").max()).item() == "2024-04-30"
    assert df.select(pl.col("type").n_unique()).item() == 1
    assert df.select(pl.col("type").unique()).item() == "R"
    assert df.select(pl.col("home_team").n_unique()).item() == 30
    assert df.select(pl.col("away_team").n_unique()).item() == 30

    df2 = pyb.umpire_scorecard_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        return_pandas=True,
    )
    assert df2 is not None
    assert df2.shape[0] == 397
    assert df2.shape[1] == 32
    assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


def test_umpire_scorecard_games_date_range_custom_game_type():
    df = pyb.umpire_scorecard_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        game_type="P",
    )
    assert df is not None
    assert df.shape[0] == 0
    assert df.shape[1] == 0
    df = pyb.umpire_scorecard_games_date_range(
        start_date="2024-04-01",
        end_date="2024-09-30",
        game_type="A",
    )
    assert df is not None
    assert df.shape[0] == 1
    assert df.shape[1] == 32
    assert df.select(pl.col("date").min()).item() == "2024-07-16"
    assert df.select(pl.col("type").unique()).item() == "A"

    df = pyb.umpire_scorecard_games_date_range(
        start_date="2024-04-01",
        end_date="2024-11-30",
        game_type="W",
    )
    assert df is not None
    assert df.shape[0] == 5
    assert df.shape[1] == 32
    assert df.select(pl.col("date").min()).item() == "2024-10-25"
    assert df.select(pl.col("date").max()).item() == "2024-10-30"
    assert df.select(pl.col("type").unique()).item() == "W"
    assert df.select(pl.col("home_team").n_unique()).item() == 2
    assert df.select(pl.col("away_team").n_unique()).item() == 2
    assert set(df.select(pl.col("home_team").unique()).to_series().to_list()) == set(
        [
            "NYY",
            "LAD",
        ]
    )


def test_umpire_scorecard_games_date_range_custom_team():
    # just focus team, no opponent or home/away
    df = pyb.umpire_scorecard_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        focus_team=pyb.UmpireScorecardTeams.DODGERS,
    )
    assert df is not None
    assert df.shape[0] == 26
    assert df.shape[1] == 32

    # focus_team, only home
    df = pyb.umpire_scorecard_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        focus_team=pyb.UmpireScorecardTeams.DODGERS,
        focus_team_home_away="h",
    )
    assert df is not None
    assert df.shape[0] == 12
    assert df.shape[1] == 32
    assert df.select(pl.col("home_team").unique()).item() == "LAD"
    assert df.select(pl.col("away_team").n_unique()).item() == 4
    assert df.select(pl.col("home_team").n_unique()).item() == 1

    # focus_team, opponent team, no home/away
    df = pyb.umpire_scorecard_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        focus_team=pyb.UmpireScorecardTeams.DODGERS,
        opponent_team=pyb.UmpireScorecardTeams.NATIONALS,
    )
    assert df is not None
    assert df.shape[0] == 6
    assert df.shape[1] == 32
    assert df.select(pl.col("home_team").n_unique()).item() == 2
    assert df.select(pl.col("away_team").n_unique()).item() == 2

    # focus_team, opponent team, home/away
    df = pyb.umpire_scorecard_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        focus_team=pyb.UmpireScorecardTeams.DODGERS,
        opponent_team=pyb.UmpireScorecardTeams.NATIONALS,
        focus_team_home_away="a",
    )
    assert df is not None
    assert df.shape[0] == 3
    assert df.shape[1] == 32
    assert df.select(pl.col("home_team").n_unique()).item() == 1
    assert df.select(pl.col("home_team").unique()).item() == "WSH"
    assert df.select(pl.col("away_team").n_unique()).item() == 1
    assert df.select(pl.col("away_team").unique()).item() == "LAD"


def test_umpire_scorecard_games_date_range_custom_ump():
    df = pyb.umpire_scorecard_games_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        umpire_name="Dan Iassogna",
    )
    assert df is not None
    assert df.shape[0] == 6
    assert df.shape[1] == 32
    assert df.select(pl.col("umpire").n_unique()).item() == 1
    assert df.select(pl.col("umpire").unique()).item() == "Dan Iassogna"
    assert df.select(pl.col("home_team").n_unique()).item() == 6
    assert df.select(pl.col("away_team").n_unique()).item() == 6


# umpire_scorecard_umpires_date_range


def test_umpire_scorecard_umpires_badinputs():
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_umpires_date_range(
            start_date=None,
            end_date="2024-04-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_umpires_date_range(start_date="2024-04-01", end_date=None)
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_umpires_date_range(
            start_date="2024-04-01",
            end_date="2024-03-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_umpires_date_range(
            start_date="2014-04-01",
            end_date="2024-05-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_umpires_date_range(
            start_date="2024-04-01",
            end_date="9999-04-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_umpires_date_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            game_type="not_a_game_type",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_umpires_date_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            focus_team=pyb.UmpireScorecardTeams.ALL,
            focus_team_home_away="not_a_home_away",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_umpires_date_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            focus_team=pyb.UmpireScorecardTeams.NATIONALS,
            opponent_team=pyb.UmpireScorecardTeams.NATIONALS,
        )


def test_umpire_scorecard_umpires_date_range():
    df = pyb.umpire_scorecard_umpires_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
    )
    assert df is not None
    assert df.shape[0] == 82
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").n_unique()).item() == 82

    df2 = pyb.umpire_scorecard_umpires_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        return_pandas=True,
    )
    assert df2 is not None
    assert df2.shape[0] == 82
    assert df2.shape[1] == 17
    assert_frame_equal(
        df.sort("umpire"), pl.DataFrame(df2, schema=df.schema).sort("umpire")
    )


def test_umpire_scorecard_umpires_date_range_custom_game_type():
    df = pyb.umpire_scorecard_umpires_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        game_type="P",
    )
    assert df is not None
    assert df.shape[0] == 0
    assert df.shape[1] == 0
    df = pyb.umpire_scorecard_umpires_date_range(
        start_date="2024-04-01",
        end_date="2024-11-30",
        game_type="A",
    )
    assert df is not None
    assert df.shape[0] == 1
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").n_unique()).item() == 1
    assert df.select(pl.col("umpire").unique()).item() == "James Hoye"
    assert df.select(pl.col("n").unique()).item() == 1

    df = pyb.umpire_scorecard_umpires_date_range(
        start_date="2024-04-01",
        end_date="2024-11-30",
        game_type="W",
    )
    assert df is not None
    assert df.shape[0] == 5
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").n_unique()).item() == 5
    assert df.select(pl.col("n").unique()).item() == 1


def test_umpire_scorecard_umpires_custom_team():
    # just focus team, no opponent or home/away
    df = pyb.umpire_scorecard_umpires_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        focus_team=pyb.UmpireScorecardTeams.DODGERS,
    )
    assert df is not None
    assert df.shape[0] == 24
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").n_unique()).item() == 24
    assert df.select(pl.col("n").n_unique()).item() == 2
    assert df.select(pl.col("n").max()).item() == 2
    assert df.select(pl.col("n").min()).item() == 1

    # focus_team, only home
    df = pyb.umpire_scorecard_umpires_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        focus_team=pyb.UmpireScorecardTeams.DODGERS,
        focus_team_home_away="h",
    )
    assert df is not None
    assert df.shape[0] == 12
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").n_unique()).item() == 12
    assert df.select(pl.col("n").n_unique()).item() == 1
    assert df.select(pl.col("n").max()).item() == 1
    assert df.select(pl.col("n").min()).item() == 1

    # focus_team, opponent team, no home/away
    df = pyb.umpire_scorecard_umpires_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        focus_team=pyb.UmpireScorecardTeams.DODGERS,
        opponent_team=pyb.UmpireScorecardTeams.NATIONALS,
    )
    assert df is not None
    assert df.shape[0] == 6
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").n_unique()).item() == 6
    assert df.select(pl.col("n").n_unique()).item() == 1
    assert df.select(pl.col("n").unique()).item() == 1

    # focus_team, opponent team, home/away
    df = pyb.umpire_scorecard_umpires_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        focus_team=pyb.UmpireScorecardTeams.DODGERS,
        opponent_team=pyb.UmpireScorecardTeams.NATIONALS,
        focus_team_home_away="h",
    )
    assert df is not None
    assert df.shape[0] == 3
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").n_unique()).item() == 3
    assert df.select(pl.col("n").n_unique()).item() == 1
    assert df.select(pl.col("n").unique()).item() == 1


def test_umpire_scorecard_umpires_custom_umpire():
    df = pyb.umpire_scorecard_umpires_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        umpire_name="Dan Iassogna",
    )
    assert df is not None
    assert df.shape[0] == 1
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").n_unique()).item() == 1
    assert df.select(pl.col("umpire").unique()).item() == "Dan Iassogna"
    assert df.select(pl.col("n").n_unique()).item() == 1
    assert df.select(pl.col("n").unique()).item() == 6


def test_umpire_scorecard_umpires_min_games_called():
    df = pyb.umpire_scorecard_umpires_date_range(
        start_date="2024-04-01",
        end_date="2024-11-30",
        min_games_called=30,
    )
    assert df is not None
    assert df.shape[0] == 37
    assert df.shape[1] == 17
    assert df.select(pl.col("umpire").n_unique()).item() == 37
    assert df.select(pl.col("n").min()).item() >= 30


# umpire_scorecard_teams_date_range


def test_umpire_scorecard_teams_date_range_badinputs():
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_teams_date_range(
            start_date=None,
            end_date="2024-04-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_teams_date_range(start_date="2024-04-01", end_date=None)
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_teams_date_range(
            start_date="2024-04-01",
            end_date="2024-03-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_teams_date_range(
            start_date="2014-04-01",
            end_date="2024-05-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_teams_date_range(
            start_date="2024-04-01",
            end_date="9999-04-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_scorecard_teams_date_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            game_type="not_a_game_type",
        )


def test_umpire_scorecards_teams_date_range():
    df = pyb.umpire_scorecard_teams_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
    )
    assert df is not None
    assert df.shape[0] == 30
    assert df.shape[1] == 19
    assert df.select(pl.col("team").n_unique()).item() == 30
    assert df.select(pl.col("n").max()).item() < 30

    df2 = pyb.umpire_scorecard_teams_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        return_pandas=True,
    )
    assert df2 is not None
    assert df2.shape[0] == 30
    assert df2.shape[1] == 19
    assert_frame_equal(
        df.sort("team"), pl.DataFrame(df2, schema=df.schema).sort("team")
    )


def test_umpire_scorecard_teams_date_range_custom_game_type():
    df = pyb.umpire_scorecard_teams_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        game_type="P",
    )
    assert df is not None
    assert df.shape[0] == 0
    assert df.shape[1] == 0
    df = pyb.umpire_scorecard_teams_date_range(
        start_date="2024-04-01",
        end_date="2024-11-30",
        game_type="A",
    )
    assert df is not None
    assert df.shape[0] == 2
    assert df.shape[1] == 19
    assert df.select(pl.col("team").n_unique()).item() == 2
    assert df.select(pl.col("n").unique()).item() == 1

    df = pyb.umpire_scorecard_teams_date_range(
        start_date="2024-04-01",
        end_date="2024-11-30",
        game_type="W",
    )
    assert df is not None
    assert df.shape[0] == 2
    assert df.shape[1] == 19
    assert df.select(pl.col("team").n_unique()).item() == 2
    assert df.select(pl.col("n").unique()).item() == 5
    assert set(df.select(pl.col("team").unique()).to_series().to_list()) == set(
        [
            "LAD",
            "NYY",
        ]
    )


def test_umpire_scorecard_teams_date_range_custom_team():
    df = pyb.umpire_scorecard_teams_date_range(
        start_date="2024-04-01",
        end_date="2024-04-30",
        focus_team=pyb.UmpireScorecardTeams.DODGERS,
    )
    assert df is not None
    assert df.shape[0] == 1
    assert df.shape[1] == 19
    assert df.select(pl.col("team").n_unique()).item() == 1
    assert df.select(pl.col("n").n_unique()).item() == 1
    assert df.select(pl.col("n").unique()).item() == 26
    assert df.select(pl.col("team").unique()).item() == "LAD"
