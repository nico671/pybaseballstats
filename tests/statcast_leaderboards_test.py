from concurrent.futures import ThreadPoolExecutor

import polars as pl
import pytest

import pybaseballstats.statcast_leaderboards as sl

pytestmark = [
    pytest.mark.integration,
    pytest.mark.playwright,
    pytest.mark.heavy,
    pytest.mark.slow,
    pytest.mark.data_dependent,
]


# Helper to run tests in a separate thread to avoid "Sync API inside asyncio loop" errors
def run_in_thread(func, *args, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        return future.result()


def test_park_factor_dimensions():
    def _test():
        with pytest.raises(ValueError):
            sl.park_factor_dimensions_leaderboard(season=2025, metric="invalid_metric")
        with pytest.raises(ValueError):
            sl.park_factor_dimensions_leaderboard(season=1900, metric="distance")
        df_distance = sl.park_factor_dimensions_leaderboard(
            season=2025, metric="distance"
        )
        assert df_distance.shape == (32, 13)
        assert (
            df_distance.filter(pl.col("Team") == "Rockies")
            .select(pl.col("lf_line_distance_ft"))
            .item()
            == 347
        )
        assert (
            df_distance.filter(pl.col("Team") == "Rockies")
            .select(pl.col("playing_field_area_sq_ft"))
            .item()
            == 116729
        )
        assert df_distance.select(pl.col("Venue").n_unique()).item() == 32
        df_height = sl.park_factor_dimensions_leaderboard(season=2025, metric="height")
        assert df_height.shape == (32, 13)
        assert (
            df_height.filter(pl.col("Team") == "Red Sox")
            .select(pl.col("lf_line_height_ft"))
            .item()
            == 37
        )
        assert (
            df_height.filter(pl.col("Team") == "Red Sox")
            .select(pl.col("playing_field_area_sq_ft"))
            .item()
            == 102935
        )
        assert df_height.select(pl.col("Venue").n_unique()).item() == 32

    run_in_thread(_test)


def test_park_factor_yearly_badinput():
    def _test():
        with pytest.raises(ValueError):
            sl.park_factor_yearly_leaderboard(season=1900)
        with pytest.raises(ValueError):
            sl.park_factor_yearly_leaderboard(season=2025, bat_side="B")
        with pytest.raises(ValueError):
            sl.park_factor_yearly_leaderboard(season=2025, conditions="Rainy")
        with pytest.raises(ValueError):
            sl.park_factor_yearly_leaderboard(season=2025, rolling_years=5)

    run_in_thread(_test)


def test_park_factor_yearly_season_rolling_years():
    def _test():
        df = sl.park_factor_yearly_leaderboard(season=2025, rolling_years=3)
        assert df.shape == (28, 19)
        assert df.select(pl.col("Year").unique()).item() == "2023-2025"
        assert df.select(pl.col("Park Factor").max()).item() == 113
        assert df.select(pl.col("Team").n_unique()).item() == 28

        df = sl.park_factor_yearly_leaderboard(season=2025, rolling_years=1)
        assert df.shape == (30, 19)
        assert df.select(pl.col("Year").unique()).item() == "2025"
        assert df.select(pl.col("Park Factor").max()).item() == 115
        assert df.select(pl.col("Team").n_unique()).item() == 30

    run_in_thread(_test)


def test_park_factor_yearly_bat_side():
    def _test():
        df = sl.park_factor_yearly_leaderboard(
            season=2015, bat_side="L", rolling_years=3
        )
        assert df.shape == (30, 19)
        assert df.select(pl.col("Year").unique()).item() == "2013-2015"
        assert df.select(pl.col("Park Factor").max()).item() == 113
        assert df.select(pl.col("Team").n_unique()).item() == 30

        df = sl.park_factor_yearly_leaderboard(
            season=2015, bat_side="R", rolling_years=3
        )
        assert df.shape == (30, 19)
        assert df.select(pl.col("Year").unique()).item() == "2013-2015"
        assert df.select(pl.col("Park Factor").max()).item() == 118
        assert df.select(pl.col("Team").n_unique()).item() == 30

    run_in_thread(_test)


def test_park_factor_yearly_conditions():
    def _test():
        df = sl.park_factor_yearly_leaderboard(
            season=2019, conditions="Day", rolling_years=3
        )
        assert df.shape == (30, 19)
        assert df.select(pl.col("Year").unique()).item() == "2017-2019"
        assert df.select(pl.col("Park Factor").max()).item() == 113
        assert df.select(pl.col("Team").n_unique()).item() == 30

        df = sl.park_factor_yearly_leaderboard(
            season=2019, conditions="Roof Closed", rolling_years=3
        )
        assert df.shape == (7, 19)
        assert df.select(pl.col("Year").unique()).item() == "2017-2019"
        assert df.select(pl.col("Park Factor").max()).item() == 101
        assert df.select(pl.col("Team").n_unique()).item() == 7

    run_in_thread(_test)


def test_park_factor_distance_badinputs():
    def _test():
        with pytest.raises(ValueError):
            sl.park_factor_distance_leaderboard(season=1900)
        with pytest.raises(ValueError):
            sl.park_factor_distance_leaderboard(season=8000)

    run_in_thread(_test)


def test_park_factor_distance():
    def _test():
        df = sl.park_factor_distance_leaderboard(season=2023)
        assert df.shape == (30, 11)
        assert df.select(pl.col("Team").n_unique()).item() == 30
        assert df.select(pl.col("Venue").n_unique()).item() == 30
        assert df.select(pl.col("total_extra_distance_ft").max()).item() == 18.0
        assert df.select(pl.col("total_extra_distance_ft").min()).item() == -5.8

    run_in_thread(_test)


def test_timer_infractions_leaderboard_badinputs():
    def _test():
        with pytest.raises(ValueError):
            sl.timer_infractions_leaderboard(season=1900)
        with pytest.raises(ValueError):
            sl.timer_infractions_leaderboard(season=8000)
        with pytest.raises(ValueError):
            sl.timer_infractions_leaderboard(
                season=2023, perspective="invalid_perspective"
            )
        with pytest.raises(ValueError):
            sl.timer_infractions_leaderboard(season=2023, min_pitches=0)

    run_in_thread(_test)


def test_timer_infractions_leaderboard():
    def _test():
        df = sl.timer_infractions_leaderboard(season=2023, perspective="Team")
        assert df.shape == (30, 10)
        assert df.select(pl.col("year").unique()).item() == 2023
        assert df.select(pl.col("all_violations").max()).item() == 55
        df = sl.timer_infractions_leaderboard(
            season=2023, perspective="Pit", min_pitches=50
        )
        assert df.shape == (387, 10)
        assert df.select(pl.col("year").unique()).item() == 2023
        assert df.select(pl.col("all_violations").max()).item() == 13

    run_in_thread(_test)


def test_arm_strength_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.arm_strength_leaderboard(stat_type="invalid")
    with pytest.raises(ValueError):
        sl.arm_strength_leaderboard(year=2019)
    with pytest.raises(ValueError):
        sl.arm_strength_leaderboard(year="invalid")
    with pytest.raises(ValueError):
        sl.arm_strength_leaderboard(min_throws=0)
    with pytest.raises(ValueError):
        sl.arm_strength_leaderboard(pos="invalid")
    with pytest.raises(ValueError):
        sl.arm_strength_leaderboard(team="NYY")


def test_arm_strength_leaderboard_player_and_team_modes(monkeypatch):
    class MockResponse:
        def __init__(self, text: str):
            self.text = text

    csv_text = """fielder_name,player_id,primary_position,primary_position_name,total_throws,total_throws_inf,total_throws_of,arm_inf,arm_of,team_name,metric
John Doe,123,RF,Right Field,100,10,90,88.1,90.2,NYY,89.5
Jane Smith,456,CF,Center Field,120,20,100,87.4,91.1,BOS,90.0
"""

    def fake_get(_url: str):
        return MockResponse(csv_text)

    monkeypatch.setattr(sl.requests, "get", fake_get)

    # Cover year="All" conversion branch and player-mode column drop.
    df_player = sl.arm_strength_leaderboard(
        stat_type="player",
        year="All",
        min_throws=50,
        pos="rf",
        team=sl.StatcastLeaderboardsTeams.YANKEES,
    )
    assert df_player.shape[0] == 2
    assert "team_name" not in df_player.columns
    assert "fielder_name" in df_player.columns
    assert df_player.select(pl.col("metric").max()).item() == 90.0

    # Cover team-mode drop path.
    df_team = sl.arm_strength_leaderboard(
        stat_type="team",
        year=2025,
        min_throws=10,
        pos="All",
        team=None,
    )
    assert df_team.shape[0] == 2
    assert "team_name" in df_team.columns
    assert "fielder_name" not in df_team.columns
    assert "player_id" not in df_team.columns
    assert df_team.select(pl.col("metric").min()).item() == 89.5


def test_abs_challenges_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2023,
        )
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025, challenge_type="invalid_challenge_type"
        )
    # invalid game_type
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025, challenge_type="all", game_type="invalid_game_type"
        )
    # invalid challenging_teams (not list)
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025, challenge_type="all", challenging_teams="NYY"
        )
    # invalid challenging teams (list but not of StatcastLeaderboardsTeams)
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025,
            challenge_type="all",
            challenging_teams=[sl.StatcastLeaderboardsTeams.YANKEES, "BOS"],
        )
    # invalid opposing_teams (not list)
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025, challenge_type="all", opposing_teams="BOS"
        )
    # invalid opposing teams (list but not of StatcastLeaderboardsTeams)
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025,
            challenge_type="all",
            opposing_teams=[sl.StatcastLeaderboardsTeams.RED_SOX, "NYY"],
        )
    # invalid pitch_types
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025, challenge_type="all", pitch_types=["invalid_pitch_type"]
        )
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025, challenge_type="all", pitch_types="FF,SL,CH"
        )
    # invalid attack_zone
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025, challenge_type="all", attack_zone="invalid_attack_zone"
        )
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025, challenge_type="all", attack_zone="1,2,3"
        )
    # invalid in_zone
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025, challenge_type="all", in_zone="invalid_in_zone"
        )
    # invalid min_challenges
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025, challenge_type="all", min_challenges=-1
        )
    # invalid min_opp_challenges
    with pytest.raises(ValueError):
        sl.abs_challenges_leaderboard(
            season=2025, challenge_type="all", min_opp_challenges=-1
        )


def test_abs_challenges_leaderboard_season():
    df = sl.abs_challenges_leaderboard(
        season=2026,
    )
    assert df.shape[0] >= 381
    assert df.shape[1] == 35
    assert df.select(pl.col("level").unique()).item() == "MLB"
    assert df.select(pl.col("team_abbr").n_unique()).item() == 30


def test_abs_challenges_leaderboard_challenge_type():
    df_batter = sl.abs_challenges_leaderboard(
        season=2026,
        challenge_type="batter",
    )
    assert df_batter.shape[0] >= 381
    assert df_batter.shape[1] == 35

    df = sl.abs_challenges_leaderboard(
        season=2026,
        challenge_type="batting-team",
    )
    assert df.shape[0] == 30
    assert df.shape[1] == 35
    assert df.select(pl.col("team_abbr").n_unique()).item() == 30

    df = sl.abs_challenges_leaderboard(
        season=2026,
        challenge_type="league",
    )
    assert df.shape[0] == 1
    assert df.shape[1] == 27

    df = sl.abs_challenges_leaderboard(
        season=2026,
        challenge_type="catcher",
    )
    assert df.shape[0] >= 63
    assert df.shape[1] == 35
    assert df.select(pl.col("team_abbr").n_unique()).item() == 30


def test_spin_direction_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.spin_direction_leaderboard(season=1900)
    with pytest.raises(ValueError):
        sl.spin_direction_leaderboard(season=10000)
    with pytest.raises(ValueError):
        sl.spin_direction_leaderboard(season="2025")
    with pytest.raises(ValueError):
        sl.spin_direction_leaderboard(team="yankees")
    with pytest.raises(ValueError):
        sl.spin_direction_leaderboard(pitch_type="four_seamer")
    with pytest.raises(ValueError):
        sl.spin_direction_leaderboard(pitcher_handedness="right")
    with pytest.raises(ValueError):
        sl.spin_direction_leaderboard(min_pitches=0)
    with pytest.raises(ValueError):
        sl.spin_direction_leaderboard(min_pitches="100")


def test_spin_direction_leaderboard():
    # single season
    df = sl.spin_direction_leaderboard(
        season=2025,
        team=sl.StatcastLeaderboardsTeams.ASTROS,
        pitch_type="FF",
        pitcher_handedness="R",
        min_pitches=100,
    )
    assert df.shape == (14, 29)
    assert df.select(pl.col("year").unique()).item() == 2025
    assert df.select(pl.col("player_name").n_unique()).item() == 14
    assert df.select(pl.col("pitch_hand").unique()).item() == "R"
    assert df.select(pl.col("api_pitch_type").unique()).item() == "FF"
    assert df.select(pl.col("n_pitches").min()).item() >= 100

    df = sl.spin_direction_leaderboard(
        season="ALL",
        team=sl.StatcastLeaderboardsTeams.ASTROS,
        pitch_type="FF",
        pitcher_handedness="R",
        min_pitches=100,
    )
    assert df.shape[0] >= 80
    assert df.shape[1] == 29
    assert df.select(pl.col("pitch_hand").unique()).item() == "R"
    assert df.select(pl.col("api_pitch_type").unique()).item() == "FF"
    assert df.select(pl.col("n_pitches").min()).item() >= 100
