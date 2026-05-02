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
        assert df.select(pl.col("Park Factor").max()).item() == 112
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

    # Cover year="All" conversion branch and player-mode column drop.
    df_player = sl.arm_strength_leaderboard(
        stat_type="player",
        year="All",
        min_throws=50,
        pos="rf",
        team=sl.StatcastLeaderboardsTeams.YANKEES,
    )
    assert df_player.shape[0] == 8
    assert df_player.shape[1] == 25
    assert "team_name" not in df_player.columns
    assert "fielder_name" in df_player.columns

    # Cover team-mode drop path.
    df_team = sl.arm_strength_leaderboard(
        stat_type="team",
        year=2025,
        min_throws=10,
        pos="All",
        team=None,
    )
    assert df_team.shape[0] == 30
    assert df_team.shape[1] == 17
    assert "team_name" in df_team.columns
    assert "fielder_name" not in df_team.columns
    assert "player_id" not in df_team.columns


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


def test_active_spin_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.active_spin_leaderboard(season=1900)
    with pytest.raises(ValueError):
        sl.active_spin_leaderboard(
            season=1900,
            stat_method="spin-based",
            min_pitches=100,
            pitcher_handedness="R",
        )
    with pytest.raises(ValueError):
        sl.active_spin_leaderboard(
            season=2025,
            stat_method="invalid_method",
            min_pitches=100,
            pitcher_handedness="R",
        )
    with pytest.raises(ValueError):
        sl.active_spin_leaderboard(
            season=2025, stat_method="spin-based", min_pitches=0, pitcher_handedness="R"
        )
    with pytest.raises(ValueError):
        sl.active_spin_leaderboard(
            season=2025,
            stat_method="spin-based",
            min_pitches=100,
            pitcher_handedness="invalid_handedness",
        )


def test_active_spin_leaderboard():
    df = sl.active_spin_leaderboard(
        season=2023, min_pitches=100, stat_method="spin-based", pitcher_handedness="R"
    )
    assert df.shape[0] == 510
    assert df.shape[1] == 12
    assert df.select(pl.col("pitch_hand").unique()).item() == "R"
    assert df.select(pl.col("player_id").n_unique()).item() == 510


def test_arm_angle_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(start_date="2023/04/01", end_date="2023/10/01")
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(start_date="2023-04-01", end_date="2023/10/01")
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(start_date="2023-04-01", end_date="2022-10-01")
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(start_date="2024-04-01", end_date="10000-10-01")
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01", end_date="2023-10-01", teams=["Yankees"]
        )
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01",
            end_date="2023-10-01",
            teams=[sl.StatcastLeaderboardsTeams.YANKEES, "BOS"],
        )
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01",
            end_date="2023-10-01",
            season_type=["R", "WC", "Invalid"],
        )
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01",
            end_date="2023-10-01",
            pitcher_handedness="invalid_handedness",
        )
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01",
            end_date="2023-10-01",
            batter_handedness="invalid_batter_handedness",
        )
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01",
            end_date="2023-10-01",
            pitch_types="FF",
        )
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01",
            end_date="2023-10-01",
            pitch_types=["invalid_pitch_type"],
        )
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01",
            end_date="2023-10-01",
            min_pitches=0,
        )
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01",
            end_date="2023-10-01",
            min_pitches="100",
        )
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01",
            end_date="2023-10-01",
            group_by="invalid_group_by",
        )
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01",
            end_date="2023-10-01",
            group_by=[
                "season",
                "month",
                "pitch_type",
                "game_type",
                "bat_side",
                "fielding_team",
            ],
        )
    with pytest.raises(ValueError):
        sl.arm_angle_leaderboard(
            start_date="2023-04-01", end_date="2023-10-01", min_group_size=0
        )


def test_arm_angle_leaderboard():
    df = sl.arm_angle_leaderboard(
        start_date="2020-01-01",
        end_date="2020-12-31",
        teams=[
            sl.StatcastLeaderboardsTeams.DODGERS,
            sl.StatcastLeaderboardsTeams.YANKEES,
        ],
        pitcher_handedness="R",
        batter_handedness="L",
        season_type=["R"],
        pitch_types=["FF", "SL"],
        min_pitches=100,
        group_by=["month", "pitch_type", "game_type", "bat_side"],
        min_group_size=10,
    )
    assert df.shape[0] == 11
    assert df.shape[1] == 15
    assert df.select(pl.col("pitch_hand").unique()).item() == "R"
    for col_name in ["month", "pitch_type", "game_type", "bat_side"]:
        assert col_name in df.columns
    assert df.select(pl.col("n_pitches").min()).item() >= 10
    assert df.select(pl.col("pitch_type").n_unique()).item() <= 2
    assert df.select(pl.col("game_type").unique()).item() == "R"
    assert df.select(pl.col("bat_side").n_unique()).item() == 1


def test_pitch_arsenals_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.pitch_arsenals_leaderboard(season=1900)
    with pytest.raises(ValueError):
        sl.pitch_arsenals_leaderboard(season=10000)
    with pytest.raises(ValueError):
        sl.pitch_arsenals_leaderboard(metric_type="invalid_metric_type")
    with pytest.raises(ValueError):
        sl.pitch_arsenals_leaderboard(pitcher_handedness="invalid_handedness")
    with pytest.raises(ValueError):
        sl.pitch_arsenals_leaderboard(min_pitches=0)
    with pytest.raises(ValueError):
        sl.pitch_arsenals_leaderboard(min_pitches="100")


def test_pitch_arsenals_leaderboard():
    df = sl.pitch_arsenals_leaderboard(
        season=2023, metric_type="avg_speed", pitcher_handedness="R", min_pitches=100
    )
    assert df.shape[0] == 515
    assert df.shape[1] == 12
    assert df.select(pl.col("player_id").n_unique()).item() == 515
    assert df.select(pl.col("ff_avg_speed").max()).item() == 101.8

    df = sl.pitch_arsenals_leaderboard(
        season=2023,
        metric_type="usage_percentage",
        pitcher_handedness="ALL",
        min_pitches=100,
    )
    assert df.shape[0] == 711
    assert df.shape[1] == 12
    assert df.select(pl.col("player_id").n_unique()).item() == 711


def test_pitch_movement_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.pitch_movement_leaderboard(season=1900)
    with pytest.raises(ValueError):
        sl.pitch_movement_leaderboard(season=10000)
    with pytest.raises(ValueError):
        sl.pitch_movement_leaderboard(pitch_type="invalid_pitch_type")
    with pytest.raises(ValueError):
        sl.pitch_movement_leaderboard(pitcher_handedness="invalid_handedness")
    with pytest.raises(ValueError):
        sl.pitch_movement_leaderboard(min_pitches=0)
    with pytest.raises(ValueError):
        sl.pitch_movement_leaderboard(min_pitches="100")


def test_pitch_movement_leaderboard():
    df = sl.pitch_movement_leaderboard(
        season=2023,
        pitch_type="FF",
        pitcher_handedness="L",
        min_pitches=100,
    )
    assert df.shape[0] == 132
    assert df.shape[1] == 24
    assert df.select(pl.col("pitcher_id").n_unique()).item() == 132
    assert df.select(pl.col("pitch_type").unique()).item() == "FF"
    assert df.select(pl.col("pitch_hand").unique()).item() == "L"
    assert df.select(pl.col("pitches_thrown").min()).item() >= 100
    assert df.select(pl.col("year").unique()).item() == 2023


def test_pitcher_running_game_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(start_season=1900, end_season=2025)
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(start_season=2025, end_season=1900)
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(
            start_season=2025, end_season=2025, game_type="invalid_game_type"
        )
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(
            start_season=2025, end_season=2025, group_by="invalid_group_by"
        )
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(
            start_season=2025, end_season=2025, pitcher_handedness="invalid_handedness"
        )
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(
            start_season=2025,
            end_season=2025,
            runner_movement="invalid_runner_movement",
        )
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(
            start_season=2025, end_season=2025, target_base="invalid_target_base"
        )
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(
            start_season=2025, end_season=2025, num_prior_disengagements="100"
        )
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(
            start_season=2025, end_season=2025, min_sb_opportunities=0
        )
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(
            start_season=2025, end_season=2025, min_sb_opportunities="100"
        )
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(
            start_season=2025, end_season=2025, team=108
        )
    with pytest.raises(ValueError):
        sl.pitcher_running_game_leaderboard(
            start_season=2025, end_season=2025, team="Yankees"
        )


def test_pitcher_running_game_leaderboard():
    df = sl.pitcher_running_game_leaderboard(
        start_season=2020,
        end_season=2023,
        game_type="Regular",
        group_by="Pit",
        pitcher_handedness="ALL",
        runner_movement="All",
        target_base="All",
        num_prior_disengagements="All",
        min_sb_opportunities=10,
        team="All",
        split_years=True,
    )
    assert df.shape[0] == 3174
    assert df.shape[1] == 25
    assert (
        df.select(pl.col("player_id").n_unique()).item() == 1374
    )  # less than total rows due to some pitchers appearing in multiple seasons
    assert df.select(pl.col("team_name").n_unique()).item() == 30
    assert df.select(pl.col("start_year").min()).item() == 2020
    assert df.select(pl.col("end_year").max()).item() == 2023
    assert df.select(pl.col("key_target_base").unique()).item() == "All"
    assert df.select(pl.col("n_init").min()).item() >= 10
