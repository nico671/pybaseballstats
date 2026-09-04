from concurrent.futures import ThreadPoolExecutor

import polars as pl
import pytest

import pybaseballstats.statcast_leaderboards as sl


# Helper to run tests in a separate thread to avoid "Sync API inside asyncio loop" errors
def run_in_thread(func, *args, **kwargs):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        return future.result()


@pytest.mark.live
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


@pytest.mark.live
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


@pytest.mark.live
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


@pytest.mark.live
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


@pytest.mark.live
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


@pytest.mark.live
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


def test_percentile_rankings_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=2014)
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=9999)
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=True)
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=False)
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=2025, player_type="fielder")
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=2025, player_type="Batter")
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=2025, player_type=None)
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=2025, position="all")
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=2025, position="OF")
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=2025, position=6)
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=2025, position=None)
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(
            season=2025, player_type="pitcher", position="P"
        )
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(
            season=2025, player_type="pitcher", position="C"
        )
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(
            season=2025, player_type="pitcher", position="SS"
        )
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(
            season=2025, player_type="pitcher", position="DH"
        )
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=2025, team="NYY")
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=2025, team=147)
    with pytest.raises(ValueError):
        sl.percentile_rankings_leaderboard(season=2025, team=None)


def test_percentile_rankings_leaderboard_builds_batter_urls(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            'player_name,player_id,year,xwoba,xba,hard_hit_percent,bat_speed\n'
            '"Judge, Aaron",592450,2025,100,,99,98\n'
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.percentile_rankings_leaderboard(
        season=2025,
        position="SS",
        team=sl.StatcastLeaderboardsTeams.YANKEES,
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/percentile-rankings?"
        "type=batter&year=2025&position=6&team=147&csv=true"
    ]
    assert df.select(pl.col("player_name")).item() == "Judge, Aaron"
    assert df.select(pl.col("player_id")).item() == 592450
    assert df.select(pl.col("year")).item() == 2025
    assert df.select(pl.col("xba")).item() is None
    assert {"hard_hit_percent", "bat_speed"} <= set(df.columns)

    sl.percentile_rankings_leaderboard(season=2025)
    assert requested_urls[-1] == (
        "https://baseballsavant.mlb.com/leaderboard/percentile-rankings?"
        "type=batter&year=2025&position=&team=&csv=true"
    )


def test_percentile_rankings_leaderboard_builds_pitcher_url(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            "player_name,player_id,year,xwoba,xera,fb_velocity,curve_spin\n"
            '"Sale, Chris",519242,2025,92,92,58,\n'
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.percentile_rankings_leaderboard(season=2025, player_type="pitcher")

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/percentile-rankings?"
        "type=pitcher&year=2025&position=&team=&csv=true"
    ]
    assert df.select(pl.col("player_name")).item() == "Sale, Chris"
    assert df.select(pl.col("player_id")).item() == 519242
    assert df.select(pl.col("curve_spin")).item() is None
    assert {"xera", "fb_velocity", "curve_spin"} <= set(df.columns)
    assert "bat_speed" not in df.columns


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


@pytest.mark.live
def test_arm_strength_leaderboard_player_and_team_modes(monkeypatch):

    # Cover year="All" conversion branch and player-mode column drop.
    df_player = sl.arm_strength_leaderboard(
        stat_type="player",
        year=2025,
        min_throws=50,
        pos="rf",
        team=sl.StatcastLeaderboardsTeams.YANKEES,
    )
    assert df_player.shape[0] == 2
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


def test_catcher_blocking_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.catcher_blocking_leaderboard(start_season=2017, end_season=2025)
    with pytest.raises(ValueError):
        sl.catcher_blocking_leaderboard(start_season=2025, end_season=2024)
    with pytest.raises(ValueError):
        sl.catcher_blocking_leaderboard(
            start_season=2025, end_season=2025, game_type="invalid"
        )
    with pytest.raises(ValueError):
        sl.catcher_blocking_leaderboard(
            start_season=2025, end_season=2025, group_by="invalid"
        )
    with pytest.raises(ValueError):
        sl.catcher_blocking_leaderboard(
            start_season=2025, end_season=2025, min_pitches=0
        )
    with pytest.raises(ValueError):
        sl.catcher_blocking_leaderboard(
            start_season=2025, end_season=2025, min_pitches="100"
        )
    with pytest.raises(ValueError):
        sl.catcher_blocking_leaderboard(
            start_season=2025, end_season=2025, team="Yankees"
        )
    with pytest.raises(ValueError):
        sl.catcher_blocking_leaderboard(
            start_season=2025, end_season=2025, split_years="yes"
        )


def test_catcher_blocking_leaderboard_builds_url(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            "player_id,player_name,team_name,start_year,end_year,pitches,"
            "catcher_blocking_runs,blocks_above_average\n"
            "672386,\"Kirk, Alejandro\",TOR,2025,2025,2118,3,13\n"
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.catcher_blocking_leaderboard(
        start_season=2020,
        end_season=2025,
        game_type="Playoff",
        group_by="Cat",
        min_pitches=100,
        team=sl.StatcastLeaderboardsTeams.BLUE_JAYS,
        split_years=True,
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/catcher-blocking?"
        "game_type=Playoff&n=100&season_end=2025&season_start=2020&split=yes&"
        "team=141&type=Cat&with_team_only=1&sortColumn=diff_runner_pbwp&"
        "sortDirection=desc&csv=true"
    ]
    assert df.select(pl.col("player_name")).item() == "Kirk, Alejandro"

    sl.catcher_blocking_leaderboard(
        start_season=2020,
        end_season=2025,
        group_by="Catching Team",
        min_pitches=100,
        team=sl.StatcastLeaderboardsTeams.BLUE_JAYS,
    )
    assert requested_urls[-1] == (
        "https://baseballsavant.mlb.com/leaderboard/catcher-blocking?"
        "game_type=Regular&n=&season_end=2025&season_start=2020&split=no&"
        "team=&type=Pitching+Team&with_team_only=1&sortColumn=diff_runner_pbwp&"
        "sortDirection=desc&csv=true"
    )


def test_catcher_framing_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.catcher_framing_leaderboard(start_season=2017, end_season=2025)
    with pytest.raises(ValueError):
        sl.catcher_framing_leaderboard(start_season=2025, end_season=2024)
    with pytest.raises(ValueError):
        sl.catcher_framing_leaderboard(
            start_season=2025, end_season=2025, group_by="invalid"
        )
    with pytest.raises(ValueError):
        sl.catcher_framing_leaderboard(
            start_season=2025, end_season=2025, game_type="invalid"
        )
    with pytest.raises(ValueError):
        sl.catcher_framing_leaderboard(
            start_season=2025, end_season=2025, min_pitches=0
        )
    with pytest.raises(ValueError):
        sl.catcher_framing_leaderboard(
            start_season=2025, end_season=2025, teams=["NYY"]
        )
    with pytest.raises(ValueError):
        sl.catcher_framing_leaderboard(
            start_season=2025, end_season=2025, batter_handedness="B"
        )
    with pytest.raises(ValueError):
        sl.catcher_framing_leaderboard(
            start_season=2025, end_season=2025, pitcher_handedness="B"
        )
    with pytest.raises(ValueError):
        sl.catcher_framing_leaderboard(
            start_season=2025, end_season=2025, in_zone="in"
        )
    with pytest.raises(ValueError):
        sl.catcher_framing_leaderboard(
            start_season=2025, end_season=2025, min_results=0
        )


def test_catcher_framing_leaderboard_builds_url(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            "id,name,pitches,rv_tot,pct_tot,rv_11,pct_11\n"
            "672386,\"Kirk, Alejandro\",878,0.46,0.84,0,0.60\n"
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.catcher_framing_leaderboard(
        start_season=2020,
        end_season=2025,
        group_by="catcher",
        game_type="Playoff",
        min_pitches=250,
        teams=[
            sl.StatcastLeaderboardsTeams.BLUE_JAYS,
            sl.StatcastLeaderboardsTeams.ORIOLES,
        ],
        batter_handedness="L",
        pitcher_handedness="R",
        in_zone=True,
        min_results=50,
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/catcher-framing?"
        "gameType=Playoff&seasonStart=2020&seasonEnd=2025&team=141|110&"
        "type=catcher&minPitches=250&minResults=50&batSide=L&pitchHand=R&"
        "ballStrike=in&csv=true"
    ]
    assert df.select(pl.col("player_id")).item() == 672386
    assert df.select(pl.col("player_name")).item() == "Kirk, Alejandro"

    team_df = sl.catcher_framing_leaderboard(
        start_season=2020, end_season=2025, group_by="catching-team"
    )
    assert requested_urls[-1].endswith(
        "type=catching-team&minPitches=q&minResults=1&"
        "batSide=&pitchHand=&ballStrike=&csv=true"
    )
    assert "team_id" in team_df.columns
    assert "team_name" in team_df.columns


def test_catcher_pop_time_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.catcher_pop_time_leaderboard(season=2014)
    with pytest.raises(ValueError):
        sl.catcher_pop_time_leaderboard(season=9999)
    with pytest.raises(ValueError):
        sl.catcher_pop_time_leaderboard(team="Yankees")
    with pytest.raises(ValueError):
        sl.catcher_pop_time_leaderboard(min_2b_attempts="2")
    with pytest.raises(ValueError):
        sl.catcher_pop_time_leaderboard(min_3b_attempts="2")


def test_catcher_pop_time_leaderboard_builds_url(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            "entity_name,entity_id,team_id,age,maxeff_arm_2b_3b_sba,"
            "exchange_2b_3b_sba,pop_2b_sba_count,pop_2b_sba,pop_2b_cs,"
            "pop_2b_sb,pop_3b_sba_count,pop_3b_sba,pop_3b_cs,pop_3b_sb\n"
            '"Kirk, Alejandro",672386,141,27,82.4,0.63,20,1.95,1.92,1.98,5,1.4,1.35,1.45\n'
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.catcher_pop_time_leaderboard(
        season=2025,
        team=sl.StatcastLeaderboardsTeams.BLUE_JAYS,
        min_2b_attempts=7,
        min_3b_attempts=3,
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/poptime?"
        "year=2025&team=141&min2b=7&min3b=3&csv=true"
    ]
    assert df.select(pl.col("entity_name")).item() == "Kirk, Alejandro"
    assert df.select(pl.col("pop_2b_sba")).item() == 1.95


def test_catcher_stance_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(start_season=2019, end_season=2025)
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(start_season=2025, end_season=2024)
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(start_season=2025, end_season=2025, group_by="invalid")
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(start_season=2025, end_season=2025, game_type="invalid")
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(start_season=2025, end_season=2025, min_pitches=0)
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(start_season=2025, end_season=2025, teams=["NYY"])
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(
            start_season=2025, end_season=2025, batter_handedness="B"
        )
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(
            start_season=2025, end_season=2025, pitcher_handedness="B"
        )
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(
            start_season=2025, end_season=2025, knee_position="invalid"
        )
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(start_season=2025, end_season=2025, min_results=0)
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(
            start_season=2025, end_season=2025, start_date="2020/07/23"
        )
    with pytest.raises(ValueError):
        sl.catcher_stance_leaderboard(
            start_season=2025,
            end_season=2025,
            start_date="2024-10-01",
            end_date="2024-09-01",
        )


def test_catcher_stance_leaderboard_builds_url(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            "id,name,year,pitches,knee_down_pct,l_down_r_up_pct,r_down_l_up_pct,"
            "both_down_pct,both_up_pct,catching_rv\n"
            '672386,"Kirk, Alejandro",2024,2500,0.5,0.2,0.1,0.1,0.1,1.2\n'
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.catcher_stance_leaderboard(
        start_season=2023,
        end_season=2024,
        group_by="catcher",
        game_type="Playoff",
        min_pitches=250,
        teams=[
            sl.StatcastLeaderboardsTeams.BLUE_JAYS,
            sl.StatcastLeaderboardsTeams.ORIOLES,
        ],
        batter_handedness="L",
        pitcher_handedness="R",
        knee_position="Knee(s) Down",
        min_results=25,
        start_date="2023-04-01",
        end_date="2024-10-01",
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/catcher-stance?"
        "gameType=Playoff&seasonStart=2023&seasonEnd=2024&team=141|110&"
        "type=catcher&minPitches=250&minResults=25&batSide=L&pitchHand=R&"
        "kneeCode=9999&dateStart=2023-04-01&dateEnd=2024-10-01&csv=true"
    ]
    assert df.select(pl.col("player_id")).item() == 672386
    assert df.select(pl.col("player_name")).item() == "Kirk, Alejandro"


def test_catcher_throwing_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.catcher_throwing_leaderboard(start_season=2015, end_season=2025)
    with pytest.raises(ValueError):
        sl.catcher_throwing_leaderboard(start_season=2025, end_season=2024)
    with pytest.raises(ValueError):
        sl.catcher_throwing_leaderboard(
            start_season=2025, end_season=2025, game_type="invalid"
        )
    with pytest.raises(ValueError):
        sl.catcher_throwing_leaderboard(
            start_season=2025, end_season=2025, group_by="invalid"
        )
    with pytest.raises(ValueError):
        sl.catcher_throwing_leaderboard(
            start_season=2025, end_season=2025, min_sb_attempts=0
        )
    with pytest.raises(ValueError):
        sl.catcher_throwing_leaderboard(
            start_season=2025, end_season=2025, min_sb_attempts="100"
        )
    with pytest.raises(ValueError):
        sl.catcher_throwing_leaderboard(
            start_season=2025, end_season=2025, target_base="1B"
        )
    with pytest.raises(ValueError):
        sl.catcher_throwing_leaderboard(
            start_season=2025, end_season=2025, team="Yankees"
        )
    with pytest.raises(ValueError):
        sl.catcher_throwing_leaderboard(
            start_season=2025, end_season=2025, split_years="yes"
        )
    with pytest.raises(ValueError):
        sl.catcher_throwing_leaderboard(
            start_season=2025, end_season=2025, with_team_only=1
        )


def test_catcher_throwing_leaderboard_builds_url(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            "player_id,player_name,team_name,start_year,end_year,sb_attempts,"
            "catcher_stealing_runs,caught_stealing_above_average,n_cs,rate_cs,"
            "est_cs_pct,cs_aa_per_throw,pop_time,exchange_time,arm_strength\n"
            '672386,"Kirk, Alejandro",TOR,2024,2024,75,1.2,2.1,15,0.2,0.25,0.03,1.9,0.6,80\n'
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.catcher_throwing_leaderboard(
        start_season=2023,
        end_season=2024,
        game_type="Playoff",
        group_by="Pitching Team",
        min_sb_attempts=50,
        target_base="2B",
        team=sl.StatcastLeaderboardsTeams.BLUE_JAYS,
        split_years=True,
        with_team_only=False,
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/catcher-throwing?"
        "game_type=Playoff&n=50&season_end=2024&season_start=2023&split=yes&"
        "team=141&type=Pitching Team&with_team_only=0&target_base=2B&csv=true"
    ]
    assert df.select(pl.col("player_id")).item() == 672386
    assert df.select(pl.col("sb_attempts")).item() == 75


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


@pytest.mark.live
def test_abs_challenges_leaderboard_season():
    df = sl.abs_challenges_leaderboard(
        season=2026,
    )
    assert df.shape[0] >= 381
    assert df.shape[1] == 35
    assert df.select(pl.col("level").unique()).item() == "MLB"
    assert df.select(pl.col("team_abbr").n_unique()).item() == 30


@pytest.mark.live
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


@pytest.mark.live
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


@pytest.mark.live
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


@pytest.mark.live
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
    assert df.shape[0] == 15
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


@pytest.mark.live
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


@pytest.mark.live
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


@pytest.mark.live
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


def test_baserunning_run_value_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.baserunning_run_value_leaderboard(start_season=2015, end_season=2025)
    with pytest.raises(ValueError):
        sl.baserunning_run_value_leaderboard(start_season=2025, end_season=2024)
    with pytest.raises(ValueError):
        sl.baserunning_run_value_leaderboard(
            start_season=2025, end_season=2025, game_type="invalid"
        )
    with pytest.raises(ValueError):
        sl.baserunning_run_value_leaderboard(
            start_season=2025, end_season=2025, group_by="invalid"
        )
    with pytest.raises(ValueError):
        sl.baserunning_run_value_leaderboard(
            start_season=2025, end_season=2025, min_opportunities=0
        )
    with pytest.raises(ValueError):
        sl.baserunning_run_value_leaderboard(
            start_season=2025, end_season=2025, min_opportunities="100"
        )
    with pytest.raises(ValueError):
        sl.baserunning_run_value_leaderboard(
            start_season=2025, end_season=2025, team="Yankees"
        )
    with pytest.raises(ValueError):
        sl.baserunning_run_value_leaderboard(
            start_season=2025, end_season=2025, split_years="yes"
        )


def test_baserunning_run_value_leaderboard_builds_url(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            "player_id,entity_name,team_name,start_year,end_year,runner_runs_tot\n"
            '677951,"Witt Jr., Bobby",KC,2024,2025,12.5\n'
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.baserunning_run_value_leaderboard(
        start_season=2024,
        end_season=2025,
        game_type="All",
        group_by="Runners",
        min_opportunities=20,
        team=sl.StatcastLeaderboardsTeams.YANKEES,
        split_years=True,
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/baserunning-run-value?"
        "game_type=All&season_start=2024&season_end=2025&"
        "sortColumn=runner_runs_tot&sortDirection=desc&split=yes&n=20&"
        "team=147&type=Run&with_team_only=1&csv=true"
    ]
    assert df.select(pl.col("player_id")).item() == 677951
    assert df.select(pl.col("player_name")).item() == "Witt Jr., Bobby"


def test_baserunning_run_value_leaderboard_normalizes_group_identifiers(monkeypatch):
    class Response:
        text = (
            "player_id,entity_name,team_name,start_year,end_year,runner_runs_tot\n"
            '147,"Yankees",NYY,2024,2024,10.0\n'
        )

    monkeypatch.setattr(sl.requests, "get", lambda url: Response())

    team_df = sl.baserunning_run_value_leaderboard(
        start_season=2024, end_season=2024, group_by="Running Team"
    )
    assert team_df.select(pl.col("team_id")).item() == 147
    assert team_df.select(pl.col("team_name")).item() == "Yankees"
    assert team_df.select(pl.col("team_abbr")).item() == "NYY"

    league_df = sl.baserunning_run_value_leaderboard(
        start_season=2024, end_season=2024, group_by="League"
    )
    assert league_df.select(pl.col("league_id")).item() == 147
    assert league_df.select(pl.col("league_name")).item() == "Yankees"


def test_basestealing_run_value_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(start_season=2015, end_season=2025)
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(start_season=2025, end_season=2024)
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(
            start_season=2025, end_season=2025, game_type="invalid"
        )
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(
            start_season=2025, end_season=2025, group_by="invalid"
        )
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(
            start_season=2025, end_season=2025, pitcher_handedness="invalid"
        )
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(
            start_season=2025, end_season=2025, runner_movement="invalid"
        )
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(
            start_season=2025, end_season=2025, target_base="invalid"
        )
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(
            start_season=2025, end_season=2025, num_prior_disengagements="4"
        )
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(
            start_season=2025, end_season=2025, min_sb_opportunities=0
        )
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(
            start_season=2025, end_season=2025, min_sb_opportunities="100"
        )
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(
            start_season=2025, end_season=2025, team="Yankees"
        )
    with pytest.raises(ValueError):
        sl.basestealing_run_value_leaderboard(
            start_season=2025, end_season=2025, split_years="yes"
        )


def test_basestealing_run_value_leaderboard_builds_url(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            "player_id,player_name,team_name,start_year,end_year,key_target_base,"
            "runs_stolen_on_running_act,n_init\n"
            '677951,"Witt Jr., Bobby",KC,2024,2025,"2B",3.5,25\n'
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.basestealing_run_value_leaderboard(
        start_season=2024,
        end_season=2025,
        game_type="All",
        group_by="Running Team",
        pitcher_handedness="L",
        runner_movement="Advance",
        target_base="2B",
        num_prior_disengagements="3+",
        min_sb_opportunities=50,
        team=sl.StatcastLeaderboardsTeams.YANKEES,
        split_years=True,
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/basestealing-run-value?"
        "game_type=All&n=50&pitch_hand=L&runner_moved=Advance&target_base=2B&"
        "prior_pk=3&season_end=2025&season_start=2024&"
        "sortColumn=simple_stolen_on_running_act&sortDirection=desc&split=yes&"
        "team=147&type=Batting+Team&with_team_only=1&csv=true"
    ]
    assert df.select(pl.col("player_id")).item() == 677951
    assert df.select(pl.col("player_name")).item() == "Witt Jr., Bobby"


def test_basestealing_run_value_leaderboard_keeps_identifier_columns(monkeypatch):
    class Response:
        text = (
            "player_id,player_name,team_name,start_year,end_year,key_target_base,"
            "runs_stolen_on_running_act,n_init\n"
            '147,"Yankees",NYY,2024,2024,"All",-3.7,10\n'
        )

    monkeypatch.setattr(sl.requests, "get", lambda url: Response())

    df = sl.basestealing_run_value_leaderboard(
        start_season=2024, end_season=2024, group_by="Running Team"
    )
    assert df.columns[:3] == ["player_id", "player_name", "team_name"]


def test_extra_bases_taken_run_value_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.extra_bases_taken_run_value_leaderboard(start_season=2015, end_season=2025)
    with pytest.raises(ValueError):
        sl.extra_bases_taken_run_value_leaderboard(start_season=2025, end_season=2024)
    with pytest.raises(ValueError):
        sl.extra_bases_taken_run_value_leaderboard(
            start_season=2025, end_season=2025, game_type="invalid"
        )
    with pytest.raises(ValueError):
        sl.extra_bases_taken_run_value_leaderboard(
            start_season=2025, end_season=2025, group_by="invalid"
        )
    with pytest.raises(ValueError):
        sl.extra_bases_taken_run_value_leaderboard(
            start_season=2025, end_season=2025, situation="invalid"
        )
    with pytest.raises(ValueError):
        sl.extra_bases_taken_run_value_leaderboard(
            start_season=2025, end_season=2025, min_opportunities=0
        )
    with pytest.raises(ValueError):
        sl.extra_bases_taken_run_value_leaderboard(
            start_season=2025, end_season=2025, min_opportunities="100"
        )
    with pytest.raises(ValueError):
        sl.extra_bases_taken_run_value_leaderboard(
            start_season=2025, end_season=2025, team="Yankees"
        )
    with pytest.raises(ValueError):
        sl.extra_bases_taken_run_value_leaderboard(
            start_season=2025, end_season=2025, split_years="yes"
        )


def test_extra_bases_taken_run_value_leaderboard_builds_url(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            "entity_name,entity_id,team_name,year,runner_runs,"
            "runner_runs_advances\n"
            '"Rojas, Miguel",500743,LAD,2024,1.5,2.0\n'
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.extra_bases_taken_run_value_leaderboard(
        start_season=2024,
        end_season=2025,
        game_type="Playoff",
        group_by="Fielders",
        situation="runner_1b_to_3b_2_outs",
        min_opportunities=20,
        team=sl.StatcastLeaderboardsTeams.YANKEES,
        split_years=True,
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/baserunning?"
        "game_type=Playoff&n=20&key_base_out=r11_to_3b_2&season_end=2025&"
        "season_start=2024&split=yes&team=147&type=Fld&with_team_only=1&csv=true"
    ]
    assert df.select(pl.col("player_id")).item() == 500743
    assert df.select(pl.col("player_name")).item() == "Rojas, Miguel"


def test_extra_bases_taken_run_value_leaderboard_normalizes_group_identifiers(
    monkeypatch,
):
    class Response:
        text = (
            "entity_name,entity_id,team_name,year,runner_runs\n"
            '"Yankees",147,NYY,2024,1.0\n'
        )

    monkeypatch.setattr(sl.requests, "get", lambda url: Response())

    team_df = sl.extra_bases_taken_run_value_leaderboard(
        start_season=2024, end_season=2024, group_by="Batting Team"
    )
    assert team_df.select(pl.col("team_id")).item() == 147
    assert team_df.select(pl.col("team_name")).item() == "Yankees"
    assert team_df.select(pl.col("team_abbr")).item() == "NYY"

    league_df = sl.extra_bases_taken_run_value_leaderboard(
        start_season=2024, end_season=2024, group_by="League"
    )
    assert league_df.select(pl.col("league_id")).item() == 147
    assert league_df.select(pl.col("league_name")).item() == "Yankees"


def test_sprint_speed_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.sprint_speed_leaderboard(start_season=2014, end_season=2025)
    with pytest.raises(ValueError):
        sl.sprint_speed_leaderboard(start_season=2025, end_season=2024)
    with pytest.raises(ValueError):
        sl.sprint_speed_leaderboard(
            start_season=2025, end_season=2025, group_by="invalid"
        )
    with pytest.raises(ValueError):
        sl.sprint_speed_leaderboard(
            start_season=2025, end_season=2025, position="invalid"
        )
    with pytest.raises(ValueError):
        sl.sprint_speed_leaderboard(
            start_season=2025, end_season=2025, min_opportunities=-1
        )
    with pytest.raises(ValueError):
        sl.sprint_speed_leaderboard(
            start_season=2025, end_season=2025, min_opportunities=True
        )
    with pytest.raises(ValueError):
        sl.sprint_speed_leaderboard(
            start_season=2025, end_season=2025, team="Yankees"
        )
    with pytest.raises(ValueError):
        sl.sprint_speed_leaderboard(
            start_season=2025, end_season=2025, split_years="yes"
        )
    with pytest.raises(ValueError):
        sl.sprint_speed_leaderboard(
            start_season=2024, end_season=2025, group_by="Team"
        )


def test_sprint_speed_leaderboard_builds_player_url(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            '"last_name, first_name",player_id,team_id,team,position,age,'
            "competitive_runs,bolts,hp_to_1b,sprint_speed\n"
            '"Witt Jr., Bobby",677951,118,KC,SS,25,543,257,4.12,30.4\n'
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.sprint_speed_leaderboard(
        start_season=2024,
        end_season=2025,
        position="SS",
        min_opportunities=25,
        team=sl.StatcastLeaderboardsTeams.YANKEES,
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/sprint_speed?"
        "min_season=2024&max_season=2025&position=6&team=147&min=25&csv=true"
    ]
    assert df.select(pl.col("player_id")).item() == 677951
    assert df.select(pl.col("player_name")).item() == "Witt Jr., Bobby"
    assert df.select(pl.col("team_abbr")).item() == "KC"

    sl.sprint_speed_leaderboard(
        start_season=2024, end_season=2024, position="Position Players"
    )
    assert requested_urls[-1] == (
        "https://baseballsavant.mlb.com/leaderboard/sprint_speed?"
        "min_season=2024&max_season=2024&position=&team=&min=10&csv=true"
    )

    sl.sprint_speed_leaderboard(start_season=2024, end_season=2024, position="All")
    assert requested_urls[-1] == (
        "https://baseballsavant.mlb.com/leaderboard/sprint_speed?"
        "min_season=2024&max_season=2024&position=all&team=&min=10&csv=true"
    )


def test_sprint_speed_leaderboard_builds_team_urls(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            "team,team_id,year,n,competitive_runs,bolts,home_to_first,"
            "avg_sprint_speed,fastest_sprint_speed\n"
            '"Yankees",147,2024,18,1543,29,4.52,26.8,"29.0"\n'
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.sprint_speed_leaderboard(
        start_season=2024,
        end_season=2024,
        group_by="Team",
        team=sl.StatcastLeaderboardsTeams.YANKEES,
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/leaderboard/sprint-speed-team?"
        "season=2024&team=147&csv=true"
    ]
    assert df.select(pl.col("team_id")).item() == 147
    assert df.select(pl.col("team_name")).item() == "Yankees"
    assert df.select(pl.col("hp_to_1b")).item() == 4.52

    split_df = sl.sprint_speed_leaderboard(
        start_season=2024, end_season=2025, group_by="Team", split_years=True
    )
    assert requested_urls[-1] == (
        "https://baseballsavant.mlb.com/leaderboard/sprint-speed-team?"
        "season=all&team=&csv=true"
    )
    assert split_df.select(pl.col("team_name")).item() == "Yankees"


def test_running_splits_leaderboard_badinputs():
    with pytest.raises(ValueError):
        sl.running_splits_leaderboard(season=2014)
    with pytest.raises(ValueError):
        sl.running_splits_leaderboard(season=2027)
    with pytest.raises(ValueError):
        sl.running_splits_leaderboard(season=2025, position="P")
    with pytest.raises(ValueError):
        sl.running_splits_leaderboard(season=2025, team="Yankees")
    with pytest.raises(ValueError):
        sl.running_splits_leaderboard(season=2025, bat_side="R")
    with pytest.raises(ValueError):
        sl.running_splits_leaderboard(season=2025, min_opportunities=0)
    with pytest.raises(ValueError):
        sl.running_splits_leaderboard(season=2025, min_opportunities=True)
    with pytest.raises(ValueError):
        sl.running_splits_leaderboard(season=2025, split_type="raw")


def test_running_splits_leaderboard_builds_url(monkeypatch):
    requested_urls = []

    class Response:
        text = (
            '"last_name, first_name",player_id,name_abbrev,team_id,position_name,'
            "age,bat_side,seconds_since_hit_000,seconds_since_hit_005\n"
            '"Volpe, Anthony",683011,NYY,147,SS,23,R,0.00,0.56\n'
        )

    def fake_get(url):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(sl.requests, "get", fake_get)

    df = sl.running_splits_leaderboard(
        season=2024,
        position="SS",
        team=sl.StatcastLeaderboardsTeams.YANKEES,
        bat_side="Right",
        min_opportunities=25,
        split_type="percentile",
    )

    assert requested_urls == [
        "https://baseballsavant.mlb.com/running_splits?"
        "type=percent&bats=R&year=2024&position=6&team=147&min=25&csv=true"
    ]
    assert df.select(pl.col("player_id")).item() == 683011
    assert df.select(pl.col("player_name")).item() == "Volpe, Anthony"
    assert df.select(pl.col("team_abbr")).item() == "NYY"
    assert df.select(pl.col("position")).item() == "SS"
