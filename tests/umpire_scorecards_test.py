import polars as pl
import pytest
from live_assertions import assert_date_range, assert_live_frame, assert_numeric

import pybaseballstats.umpire_scorecards as us
from pybaseballstats.enums import UmpireScorecardTeams

pytestmark = pytest.mark.live

# region game_data function tests


def test_game_data_general():
    with pytest.raises(TypeError):
        us.game_data(start_date=None, end_date="2023-07-07")
    with pytest.raises(TypeError):
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
            focus_team=UmpireScorecardTeams.ANGELS,
            focus_team_home_away="x",
        )
    with pytest.raises(TypeError):
        us.game_data(
            start_date="2023-07-01",
            end_date="2023-07-07",
            focus_team=None,
            focus_team_home_away="h",
        )
    with pytest.raises(TypeError):
        us.game_data(
            start_date="2023-07-01",
            end_date="2023-07-07",
            focus_team=UmpireScorecardTeams.ANGELS,
            opponent_team=None,
        )
    with pytest.raises(ValueError):
        us.game_data(
            start_date="2023-07-01",
            end_date="2023-07-07",
            focus_team=UmpireScorecardTeams.ANGELS,
            focus_team_home_away="h",
            opponent_team=UmpireScorecardTeams.ANGELS,
        )
    with pytest.raises(ValueError):
        us.game_data(
            start_date="2023-07-01",
            end_date="2028-07-07",
            focus_team=UmpireScorecardTeams.ANGELS,
            focus_team_home_away="a",
            opponent_team=UmpireScorecardTeams.ANGELS,
        )
    # general test
    df = us.game_data(start_date="2026-01-01", end_date="2026-03-27")
    assert_live_frame(df, columns=("date", "umpire", "home_team", "away_team", "type"))
    print(df.columns)
    assert_date_range(df["date"], "2026-01-01", "2026-03-27")


def test_game_data_game_type():
    # game_type parameter test
    df = us.game_data(
        start_date="2026-01-01", end_date="2026-03-27", game_type="R"
    )  # regular season
    assert_live_frame(df, columns=("date", "umpire", "home_team", "away_team", "type"))
    assert_date_range(df["date"], "2026-01-01", "2026-03-27")
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
        focus_team=UmpireScorecardTeams.GIANTS,
        focus_team_home_away="h",
    )
    assert_live_frame(df, columns=("date", "umpire", "home_team", "away_team", "type"))
    assert df.select(pl.col("home_team").n_unique()).item() == 1
    assert df.select(pl.col("home_team").unique()).item() == "SF"
    df = us.game_data(
        start_date="2023-04-01",
        end_date="2023-07-07",
        focus_team=UmpireScorecardTeams.ANGELS,
        focus_team_home_away="h",
        opponent_team=UmpireScorecardTeams.RANGERS,
    )
    assert_live_frame(df, columns=("date", "umpire", "home_team", "away_team", "type"))
    assert df.select(pl.col("home_team").n_unique()).item() == 1
    assert df.select(pl.col("home_team").unique()).item() == "LAA"
    assert df.select(pl.col("away_team").n_unique()).item() == 1
    assert df.select(pl.col("away_team").unique()).item() == "TEX"

    df = us.game_data(
        start_date="2023-04-01",
        end_date="2023-07-07",
        focus_team=UmpireScorecardTeams.ANGELS,
        focus_team_home_away="a",
        opponent_team=UmpireScorecardTeams.RANGERS,
    )
    assert_live_frame(df, columns=("date", "umpire", "home_team", "away_team", "type"))
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
    assert_live_frame(df, columns=("date", "umpire", "home_team", "away_team", "type"))
    assert df.select(pl.col("umpire").n_unique()).item() == 1
    assert df.select(pl.col("umpire").unique()).item() == "Alan Porter"


# endregion

# region umpire_data function tests


def test_umpire_data_general():
    # general test
    df = us.umpire_data(start_date="2025-01-01", end_date="2025-10-01", game_type="R")
    assert_live_frame(df, columns=("umpire",), counts=("n",), unique_by=("umpire",))


def test_umpire_data_game_type():
    # game_type parameter test
    df = us.umpire_data(start_date="2025-01-01", end_date="2025-09-07", game_type="A")
    assert_live_frame(df, columns=("umpire",), counts=("n",), unique_by=("umpire",))
    df = us.umpire_data(start_date="2025-07-01", end_date="2025-07-07", game_type="P")
    assert df.shape[0] == 0
    assert df.shape[1] == 0


def test_umpire_data_team_params():
    # just focus_team
    df = us.umpire_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        game_type="R",
        focus_team=UmpireScorecardTeams.BRAVES,
    )
    assert_live_frame(df, columns=("umpire",), counts=("n",), unique_by=("umpire",))

    # focus_team only away
    df = us.umpire_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        game_type="R",
        focus_team=UmpireScorecardTeams.BRAVES,
        focus_team_home_away="a",
    )
    assert_live_frame(df, columns=("umpire",), counts=("n",), unique_by=("umpire",))

    # focus_team away with opponent_team
    df = us.umpire_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        game_type="R",
        focus_team=UmpireScorecardTeams.BRAVES,
        focus_team_home_away="a",
        opponent_team=UmpireScorecardTeams.NATIONALS,
    )
    assert_live_frame(df, columns=("umpire",), counts=("n",), unique_by=("umpire",))


def test_umpire_data_umpire_name_param():
    # umpire_name param test
    df = us.umpire_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        game_type="R",
        umpire_name="Dan Iassogna",
    )
    assert df.height == 1
    assert_live_frame(df, columns=("umpire",), counts=("n",), unique_by=("umpire",))
    assert df.select(pl.col("umpire").unique()).item() == "Dan Iassogna"


def test_umpire_data_min_games_param():
    # min_games param test
    df = us.umpire_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        game_type="R",
        min_games_called=20,
    )
    assert_live_frame(df, columns=("umpire",), counts=("n",), unique_by=("umpire",))
    assert_numeric(df["n"], minimum=20, count=True)


# endregion


# region team_data function tests


def test_team_data_general():
    # general test
    df = us.team_data(start_date="2025-01-01", end_date="2025-10-30", game_type="R")
    assert_live_frame(df, columns=("team",), unique_by=("team",))


def test_team_data_game_type():
    df = us.team_data(start_date="2025-07-01", end_date="2025-07-07", game_type="P")
    assert df.shape[0] == 0
    assert df.shape[1] == 0

    df = us.team_data(start_date="2025-07-01", end_date="2025-10-07", game_type="P")
    assert_live_frame(df, columns=("team",), unique_by=("team",))


def test_team_data_focus_team():
    df = us.team_data(
        start_date="2025-01-01",
        end_date="2025-10-30",
        game_type="R",
        focus_team=UmpireScorecardTeams.ANGELS,
    )
    assert df.height == 1
    assert_live_frame(df, columns=("team",), unique_by=("team",))
    assert df.select(pl.col("team").unique()).item() == "LAA"


# endregion


# region player_data function tests


def test_player_data_general():
    with pytest.raises(TypeError):
        us.player_data(start_date=None, end_date="2025-10-01", player_type="P")
    with pytest.raises(TypeError):
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
    with pytest.raises(TypeError):
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
    assert_live_frame(df, counts=("player_id", "n_pitches"), unique_by=("player_id",))


def test_player_data_game_type():
    # game_type parameter test
    df = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="P",
        game_type="R",
    )
    assert_live_frame(df, counts=("player_id", "n_pitches"), unique_by=("player_id",))

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
    assert_live_frame(df, counts=("player_id", "n_pitches"), unique_by=("player_id",))

    df = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="C",
        game_type="R",
    )
    assert_live_frame(df, counts=("player_id", "n_pitches"), unique_by=("player_id",))

    df = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="B",
        game_type="R",
    )
    assert_live_frame(df, counts=("player_id", "n_pitches"), unique_by=("player_id",))


def test_player_data_team_filtering():
    # team parameter test
    df_all = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="P",
        game_type="R",
        team=UmpireScorecardTeams.ALL,
    )
    df_braves = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="P",
        game_type="R",
        team=UmpireScorecardTeams.BRAVES,
    )

    assert df_all.height > 0
    assert_live_frame(
        df_all, counts=("player_id", "n_pitches"), unique_by=("player_id",)
    )
    assert df_braves.height > 0
    assert_live_frame(
        df_braves, counts=("player_id", "n_pitches"), unique_by=("player_id",)
    )
    assert set(df_braves["player_id"]) <= set(df_all["player_id"])

    df_angels_batters = us.player_data(
        start_date="2025-01-01",
        end_date="2025-10-01",
        player_type="B",
        game_type="R",
        team=UmpireScorecardTeams.ANGELS,
    )
    assert df_angels_batters.height > 0
    assert_live_frame(
        df_angels_batters, counts=("player_id", "n_pitches"), unique_by=("player_id",)
    )


# endregion
