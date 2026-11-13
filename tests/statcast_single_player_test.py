import polars as pl
import pytest
from live_assertions import assert_live_frame

import pybaseballstats.statcast_single_player as ssp
from pybaseballstats import _statcast_single_player as ssp_impl
from pybaseballstats._utils import request_utils


@pytest.fixture
def run_async_inline(monkeypatch):
    """Run coroutines whose mocked awaitables complete without an event loop."""

    def _run(coro):
        try:
            coro.send(None)
        except StopIteration as exc:
            return exc.value
        raise AssertionError("Mocked coroutine did not complete immediately")

    monkeypatch.setattr(ssp_impl.asyncio, "run", _run)


def assert_single_player_row(df: pl.DataFrame, *, player_id: int) -> None:
    assert_live_frame(
        df,
        columns=("player_name",),
        numeric=(
            "api_break_x_arm",
            "api_break_x_batter_in",
            "api_break_z_induced",
            "api_break_z_with_gravity",
            "arm_angle",
            "attack_angle",
            "attack_direction",
            "ba",
            "babip",
            "barrels_per_bbe_percent",
            "barrels_per_pa_percent",
            "bat_speed",
            "batter_run_value_per_100",
            "bb_percent",
            "bbdist",
            "eff_min_vel",
            "effective_speed",
            "hardhit_percent",
            "hyper_speed",
            "intercept_ball_minus_batter_pos_x_inches",
            "intercept_ball_minus_batter_pos_y_inches",
            "iso",
            "k_percent",
            "launch_angle",
            "launch_speed",
            "obp",
            "pitch_percent",
            "pitcher_run_exp",
            "pitcher_run_value_per_100",
            "plate_x",
            "plate_z",
            "pos3_int_start_distance",
            "pos4_int_start_distance",
            "pos5_int_start_distance",
            "pos6_int_start_distance",
            "pos7_int_start_distance",
            "pos8_int_start_distance",
            "pos9_int_start_distance",
            "rate_ideal_attack_angle",
            "release_extension",
            "release_pos_x",
            "release_pos_z",
            "run_exp",
            "slg",
            "spin_rate",
            "swing_length",
            "swing_miss_percent",
            "swing_path_tilt",
            "velocity",
            "woba",
            "wobadiff",
            "xba",
            "xbadiff",
            "xobp",
            "xobpdiff",
            "xslg",
            "xslgdiff",
            "xwoba",
        ),
        counts=(
            "abs",
            "barrels_total",
            "bb",
            "bip",
            "doubles",
            "hits",
            "hrs",
            "pa",
            "pitches",
            "player_id",
            "singles",
            "so",
            "swings",
            "takes",
            "total_pitches",
            "triples",
            "whiffs",
        ),
    )
    assert df.height == 1
    assert df["player_id"].item() == player_id
    assert df["player_name"].dtype == pl.String
    assert df["player_name"].null_count() == 0
    assert df["hits"].item() <= df["abs"].item()


@pytest.mark.parametrize(
    ("kwargs", "error_type"),
    (
        ({"player_id": "660271"}, TypeError),
        ({"season": "2025"}, TypeError),
        ({"season": 2014}, ValueError),
        ({"player_type": "fielder"}, ValueError),
        ({"chunk_size_days": "7"}, TypeError),
        ({"chunk_size_days": 0}, ValueError),
        ({"concurrency": "4"}, TypeError),
        ({"concurrency": 0}, ValueError),
    ),
)
def test_single_player_pitch_by_pitch_bad_inputs(kwargs, error_type):
    arguments = {
        "player_id": 660271,
        "season": 2025,
        "player_type": "batter",
        "show_progress": False,
    }
    arguments.update(kwargs)

    with pytest.raises(error_type):
        ssp.single_player_pitch_by_pitch(**arguments)


@pytest.mark.parametrize(
    ("player_type", "player_id", "lookup_param", "role_column"),
    (
        ("batter", 660271, "batters_lookup%5B%5D", "batter"),
        ("pitcher", 808967, "pitchers_lookup%5B%5D", "pitcher"),
    ),
)
def test_single_player_pitch_by_pitch_query_and_return_type(
    monkeypatch,
    run_async_inline,
    player_type,
    player_id,
    lookup_param,
    role_column,
):
    captured = {}

    async def _mock_fetch_all_data(
        urls,
        date_range_total_days,
        *,
        concurrency=None,
        show_progress=True,
        output_dir=None,
    ):
        captured["urls"] = urls
        captured["date_range_total_days"] = date_range_total_days
        captured["concurrency"] = concurrency
        captured["show_progress"] = show_progress
        captured["output_dir"] = output_dir
        return [
            pl.DataFrame(),
            pl.DataFrame(
                {
                    "game_date": ["2025-04-01"],
                    "pitcher": [808967],
                    "batter": [660271],
                    "plate_x": [0.25],
                    "plate_z": [2.75],
                }
            ),
        ]

    monkeypatch.setattr(ssp_impl, "_fetch_all_data", _mock_fetch_all_data)

    result = ssp.single_player_pitch_by_pitch(
        player_id=player_id,
        season=2025,
        player_type=player_type,
        chunk_size_days=1000,
        show_progress=False,
        concurrency=3,
    )

    assert isinstance(result, pl.LazyFrame)
    assert result.collect()[role_column].to_list() == [player_id]
    assert captured["date_range_total_days"] == 229
    assert captured["concurrency"] == 3
    assert captured["show_progress"] is False
    assert captured["output_dir"].name.startswith("pybaseballstats-statcast-player-")
    assert len(captured["urls"]) == 1
    url = captured["urls"][0]
    assert "type=details" in url
    assert "hfGT=R%7C" in url
    assert "hfSea=2025%7C" in url
    assert f"player_type={player_type}" in url
    assert f"{lookup_param}={player_id}" in url
    assert "game_date_gt=2025-03-18" in url
    assert "game_date_lt=2025-11-01" in url
    assert "group_by=name" not in url


def test_single_player_pitch_by_pitch_force_collect(monkeypatch, run_async_inline):
    async def _mock_fetch_all_data(*args, **kwargs):
        return [pl.DataFrame({"pitcher": [808967], "plate_x": [-0.1]})]

    monkeypatch.setattr(ssp_impl, "_fetch_all_data", _mock_fetch_all_data)

    result = ssp.single_player_pitch_by_pitch(
        player_id=808967,
        season=2025,
        player_type="pitcher",
        force_collect=True,
        chunk_size_days=1000,
        show_progress=False,
    )

    assert isinstance(result, pl.DataFrame)
    assert result.height == 1


def test_single_player_pitch_by_pitch_current_season_stops_today(
    monkeypatch, run_async_inline
):
    class FixedDate(ssp_impl.date):
        @classmethod
        def today(cls):
            return cls(2026, 4, 1)

    captured_urls = []

    async def _mock_fetch_all_data(urls, *args, **kwargs):
        captured_urls.extend(urls)
        return [pl.DataFrame({"batter": [660271]})]

    monkeypatch.setattr(ssp_impl, "date", FixedDate)
    monkeypatch.setattr(ssp_impl, "_fetch_all_data", _mock_fetch_all_data)

    ssp.single_player_pitch_by_pitch(
        player_id=660271,
        season=2026,
        player_type="batter",
        chunk_size_days=7,
        show_progress=False,
    )

    assert len(captured_urls) == 2
    assert "game_date_lt=2026-04-01" in captured_urls[-1]


def test_single_player_pitch_by_pitch_no_data(monkeypatch, run_async_inline):
    async def _mock_fetch_all_data(*args, **kwargs):
        return [pl.DataFrame(schema={"game_date": pl.String, "pitcher": pl.Int64})]

    monkeypatch.setattr(ssp_impl, "_fetch_all_data", _mock_fetch_all_data)

    frame = ssp.single_player_pitch_by_pitch(
        player_id=999999999,
        season=2025,
        player_type="batter",
        show_progress=False,
    )
    assert isinstance(frame, pl.LazyFrame)
    assert frame.collect().schema == {"game_date": pl.String, "pitcher": pl.Int64}


def test_single_player_pitch_by_pitch_no_rows_in_streamed_chunks(
    monkeypatch, run_async_inline
):
    async def _mock_fetch_all_data(*args, **kwargs):
        return []

    monkeypatch.setattr(ssp_impl, "_fetch_all_data", _mock_fetch_all_data)

    frame = ssp.single_player_pitch_by_pitch(
        player_id=999999999,
        season=2025,
        player_type="batter",
        show_progress=False,
    )
    assert isinstance(frame, pl.LazyFrame)
    assert frame.collect().is_empty()


def test_single_player_pitch_by_pitch_download_failure(monkeypatch, run_async_inline):
    async def _mock_fetch_all_data(*args, **kwargs):
        raise RuntimeError("chunk failed")

    monkeypatch.setattr(ssp_impl, "_fetch_all_data", _mock_fetch_all_data)

    with pytest.raises(
        RuntimeError,
        match=(
            "Unable to complete Statcast single-player pitch-by-pitch download "
            "for pitcher 808967 in 2025. chunk failed"
        ),
    ):
        ssp.single_player_pitch_by_pitch(
            player_id=808967,
            season=2025,
            player_type="pitcher",
            show_progress=False,
        )


def test_single_player_season_stats_bad_inputs():
    with pytest.raises(TypeError):
        ssp.single_player_season_stats(
            player_id="660271", season=2023, player_type="batter"
        )
    with pytest.raises(TypeError):
        ssp.single_player_season_stats(player_id="", season=2023, player_type="batter")
    with pytest.raises(TypeError):
        ssp.single_player_season_stats(
            player_id=None, season=2023, player_type="batter"
        )
    with pytest.raises(TypeError):
        ssp.single_player_season_stats(
            player_id=660271, season="2023", player_type="batter"
        )
    with pytest.raises(ValueError):
        ssp.single_player_season_stats(
            player_id=660271, season=1900, player_type="batter"
        )
    with pytest.raises(ValueError):
        ssp.single_player_season_stats(
            player_id=660271, season=2014, player_type="batter"
        )
    with pytest.raises(ValueError):
        ssp.single_player_season_stats(
            player_id=660271, season=2023, player_type="fielder"
        )
    with pytest.raises(TypeError):
        ssp.single_player_season_stats(
            player_id=660271,
            season=2023,
            player_type="batter",
            show_progress=False,
        )
    with pytest.raises(TypeError):
        ssp.single_player_season_stats(
            player_id=660271,
            season=2023,
            player_type="batter",
            concurrency=1,
        )


@pytest.mark.live
def test_single_player_season_stats_player_not_found():
    with pytest.raises(
        RuntimeError,
        match="No Statcast single-player data found for batter 999999999 in 2024",
    ):
        ssp.single_player_season_stats(
            player_id=999999999,
            season=2024,
            player_type="batter",
        )


def test_single_player_season_stats_malformed_csv(monkeypatch):
    class MockResponse:
        def raise_for_status(self) -> None:
            pass

        text = "a,b\n1,2,3\n"

    def _mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(request_utils.requests, "get", _mock_get)

    with pytest.raises(
        RuntimeError,
        match="Unable to retrieve or parse Statcast single-player CSV for pitcher 808967 in 2025",
    ):
        ssp.single_player_season_stats(
            player_id=808967,
            season=2025,
            player_type="pitcher",
        )


@pytest.mark.live
def test_single_player_season_stats_batter():
    # Shohei Ohtani
    df = ssp.single_player_season_stats(
        player_id=660271,
        season=2024,
        player_type="batter",
    )

    assert_single_player_row(df, player_id=660271)


@pytest.mark.live
def test_single_player_season_stats_pitcher():
    # Yoshinobu Yamamoto
    df = ssp.single_player_season_stats(
        player_id=808967,
        season=2025,
        player_type="pitcher",
    )

    assert_single_player_row(df, player_id=808967)
