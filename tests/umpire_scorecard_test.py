import pytest

import pybaseballstats as pyb


# Test umpire_games_date_range
def test_umpire_games_date_range_badinputs():
    with pytest.raises(ValueError):
        pyb.umpire_games_date_range(
            start_dt=None,
        )
    with pytest.raises(ValueError):
        pyb.umpire_games_date_range(end_dt=None)
    with pytest.raises(ValueError):
        pyb.umpire_games_date_range(
            start_dt="2024-04-01",
            end_dt="2024-03-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_games_date_range(
            start_dt="2014-04-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_games_date_range(
            end_dt="9999-04-01",
        )
    with pytest.raises(ValueError):
        pyb.umpire_games_date_range(
            start_dt="2024-04-01",
            end_dt="2024-05-01",
            game_type="not_a_game_type",
        )
    with pytest.raises(ValueError):
        pyb.umpire_games_date_range(
            start_dt="2024-04-01",
            end_dt="2024-05-01",
            focus_team=pyb.UmpireScorecardTeams.ALL,
            focus_team_home_away="not_a_home_away",
        )
    with pytest.raises(ValueError):
        pyb.umpire_games_date_range(
            start_dt="2024-04-01",
            end_dt="2024-05-01",
            focus_team=pyb.UmpireScorecardTeams.ALL,
            opponent_team=pyb.UmpireScorecardTeams.ALL,
        )
    with pytest.raises(ValueError):
        pyb.umpire_games_date_range(
            start_dt="2024-04-01",
            end_dt="2024-05-01",
            focus_team=pyb.UmpireScorecardTeams.NATIONALS,
            opponent_team=pyb.UmpireScorecardTeams.NATIONALS,
        )
    with pytest.raises(ValueError):
        pyb.umpire_games_date_range(
            start_dt="2024-04-01",
            end_dt="2024-05-01",
            opponent_team=pyb.UmpireScorecardTeams.ALL,
        )
