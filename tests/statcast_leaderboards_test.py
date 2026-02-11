from concurrent.futures import ThreadPoolExecutor

import polars as pl
import pytest

import pybaseballstats.statcast_leaderboards as sl


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
