import polars as pl
import pytest

import pybaseballstats.statcast_single_player as ssp

pytestmark = [
    pytest.mark.integration,
    pytest.mark.heavy,
    pytest.mark.data_dependent,
]

EXPECTED_SINGLE_PLAYER_SEASON_COLUMNS = [
    "pitches",
    "player_id",
    "player_name",
    "total_pitches",
    "pitch_percent",
    "ba",
    "iso",
    "babip",
    "slg",
    "woba",
    "xwoba",
    "xba",
    "hits",
    "abs",
    "launch_speed",
    "launch_angle",
    "spin_rate",
    "velocity",
    "effective_speed",
    "whiffs",
    "swings",
    "takes",
    "eff_min_vel",
    "release_extension",
    "pos3_int_start_distance",
    "pos4_int_start_distance",
    "pos5_int_start_distance",
    "pos6_int_start_distance",
    "pos7_int_start_distance",
    "pos8_int_start_distance",
    "pos9_int_start_distance",
    "pitcher_run_exp",
    "run_exp",
    "bat_speed",
    "swing_length",
    "pa",
    "bip",
    "singles",
    "doubles",
    "triples",
    "hrs",
    "so",
    "k_percent",
    "bb",
    "bb_percent",
    "api_break_z_with_gravity",
    "api_break_z_induced",
    "api_break_x_arm",
    "api_break_x_batter_in",
    "hyper_speed",
    "bbdist",
    "hardhit_percent",
    "barrels_per_bbe_percent",
    "barrels_per_pa_percent",
    "release_pos_z",
    "release_pos_x",
    "plate_x",
    "plate_z",
    "obp",
    "barrels_total",
    "batter_run_value_per_100",
    "xobp",
    "xslg",
    "pitcher_run_value_per_100",
    "xbadiff",
    "xobpdiff",
    "xslgdiff",
    "wobadiff",
    "swing_miss_percent",
    "arm_angle",
    "attack_angle",
    "attack_direction",
    "swing_path_tilt",
    "rate_ideal_attack_angle",
    "intercept_ball_minus_batter_pos_x_inches",
    "intercept_ball_minus_batter_pos_y_inches",
]


def assert_single_player_row_matches(
    df: pl.DataFrame, expected_row: dict[str, object]
) -> None:
    assert df.shape == (1, len(EXPECTED_SINGLE_PLAYER_SEASON_COLUMNS))
    assert df.columns == EXPECTED_SINGLE_PLAYER_SEASON_COLUMNS
    row = df.row(0, named=True)
    assert row.keys() == expected_row.keys()
    for col_name, expected_value in expected_row.items():
        if isinstance(expected_value, float):
            assert row[col_name] == pytest.approx(expected_value)
        else:
            assert row[col_name] == expected_value


def test_single_player_season_stats_bad_inputs():
    with pytest.raises(TypeError):
        ssp.single_player_season_stats(
            player_id="660271", season=2023, player_type="batter"
        )
    with pytest.raises(TypeError):
        ssp.single_player_season_stats(
            player_id="", season=2023, player_type="batter"
        )
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


def test_single_player_season_stats_player_not_found(monkeypatch):
    async def _mock_fetch_all_data(*args, **kwargs):
        raise RuntimeError(
            "Statcast download failed to retrieve all requested chunks after retries. "
            "1/1 chunk(s) failed. Data integrity policy prevented returning partial data. "
            "Failure details: CSV parse error: NoDataError: empty CSV"
        )

    monkeypatch.setattr(ssp, "_fetch_all_data", _mock_fetch_all_data)

    with pytest.raises(
        RuntimeError,
        match=(
            "Unable to complete Statcast single-player download for the requested "
            "player 999999999 in 2024"
        ),
    ):
        ssp.single_player_season_stats(
            player_id=999999999,
            season=2024,
            player_type="batter",
            show_progress=False,
        )

def test_single_player_season_stats_batter():
    # Shohei Ohtani
    df = ssp.single_player_season_stats(
        player_id=660271,
        season=2024,
        player_type="batter",
        show_progress=False,
    )

    assert_single_player_row_matches(
        df,
        {
            "pitches": 2838,
            "player_id": 660271,
            "player_name": "Ohtani, Shohei",
            "total_pitches": 2877,
            "pitch_percent": 98.6,
            "ba": 0.31,
            "iso": 0.336,
            "babip": 0.336,
            "slg": 0.646,
            "woba": 0.431,
            "xwoba": 0.444,
            "xba": 0.31,
            "hits": 197,
            "abs": 636,
            "launch_speed": 95.7,
            "launch_angle": 16,
            "spin_rate": 2233,
            "velocity": 89.4,
            "effective_speed": 89.68,
            "whiffs": 400,
            "swings": 1343,
            "takes": 1495,
            "eff_min_vel": 0.29999999999999716,
            "release_extension": 6.41,
            "pos3_int_start_distance": 117,
            "pos4_int_start_distance": 146,
            "pos5_int_start_distance": 130,
            "pos6_int_start_distance": 152,
            "pos7_int_start_distance": 301,
            "pos8_int_start_distance": 326,
            "pos9_int_start_distance": 307,
            "pitcher_run_exp": -71.195,
            "run_exp": 71.195,
            "bat_speed": 74.7,
            "swing_length": 7.7,
            "pa": 731,
            "bip": 479,
            "singles": 98,
            "doubles": 38,
            "triples": 7,
            "hrs": 54,
            "so": 162,
            "k_percent": 22.2,
            "bb": 81,
            "bb_percent": 11.1,
            "api_break_z_with_gravity": 2.34087,
            "api_break_z_induced": 0.54775,
            "api_break_x_arm": 0.34484,
            "api_break_x_batter_in": -0.16328,
            "hyper_speed": 94.5,
            "bbdist": 174,
            "hardhit_percent": 60.25104602510461,
            "barrels_per_bbe_percent": 21.548117154811717,
            "barrels_per_pa_percent": 14.09028727770178,
            "release_pos_z": 5.76,
            "release_pos_x": -0.57,
            "plate_x": -0.13,
            "plate_z": 2.35,
            "obp": 0.39,
            "barrels_total": 103,
            "batter_run_value_per_100": 2.50863284,
            "xobp": 0.392,
            "xslg": 0.672,
            "pitcher_run_value_per_100": -2.50863284,
            "xbadiff": 0,
            "xobpdiff": -0.0020000000000000018,
            "xslgdiff": -0.026,
            "wobadiff": -0.013,
            "swing_miss_percent": 29.8,
            "arm_angle": 38.0,
            "attack_angle": 10.780335786134769,
            "attack_direction": -0.9335278601853467,
            "swing_path_tilt": 34.86911573283945,
            "rate_ideal_attack_angle": 0.4995983935742972,
            "intercept_ball_minus_batter_pos_x_inches": 38.130972464999246,
            "intercept_ball_minus_batter_pos_y_inches": 26.275878565555765,
        },
    )


def test_single_player_season_stats_pitcher():
    # Yoshinobu Yamamoto
    df = ssp.single_player_season_stats(
        player_id=808967,
        season=2025,
        player_type="pitcher",
        show_progress=False,
    )

    assert_single_player_row_matches(
        df,
        {
            "pitches": 2789,
            "player_id": 808967,
            "player_name": "Yamamoto, Yoshinobu",
            "total_pitches": 2792,
            "pitch_percent": 99.9,
            "ba": 0.183,
            "iso": 0.1,
            "babip": 0.244,
            "slg": 0.283,
            "woba": 0.244,
            "xwoba": 0.259,
            "xba": 0.198,
            "hits": 113,
            "abs": 619,
            "launch_speed": 87.7,
            "launch_angle": 7.5,
            "spin_rate": 2148,
            "velocity": 90.2,
            "effective_speed": 90.54,
            "whiffs": 377,
            "swings": 1303,
            "takes": 1486,
            "eff_min_vel": 0.29999999999999716,
            "release_extension": 6.5,
            "pos3_int_start_distance": 111,
            "pos4_int_start_distance": 151,
            "pos5_int_start_distance": 122,
            "pos6_int_start_distance": 150,
            "pos7_int_start_distance": 297,
            "pos8_int_start_distance": 319,
            "pos9_int_start_distance": 297,
            "pitcher_run_exp": 41.644,
            "run_exp": -41.644,
            "bat_speed": 70.0,
            "swing_length": 7.2,
            "pa": 684,
            "bip": 421,
            "singles": 79,
            "doubles": 20,
            "triples": 0,
            "hrs": 14,
            "so": 201,
            "k_percent": 29.4,
            "bb": 59,
            "bb_percent": 8.6,
            "api_break_z_with_gravity": 2.43247,
            "api_break_z_induced": 0.4283,
            "api_break_x_arm": 0.30963,
            "api_break_x_batter_in": 0.00961,
            "hyper_speed": 91.6,
            "bbdist": 134,
            "hardhit_percent": 39.76190476190476,
            "barrels_per_bbe_percent": 5.714285714285714,
            "barrels_per_pa_percent": 3.508771929824561,
            "release_pos_z": 5.46,
            "release_pos_x": -1.82,
            "plate_x": -0.1,
            "plate_z": 2.05,
            "obp": 0.257,
            "barrels_total": 24,
            "batter_run_value_per_100": -1.493151667,
            "xobp": 0.271,
            "xslg": 0.304,
            "pitcher_run_value_per_100": 1.493151667,
            "xbadiff": -0.015,
            "xobpdiff": -0.014000000000000012,
            "xslgdiff": -0.021,
            "wobadiff": -0.015,
            "swing_miss_percent": 28.9,
            "arm_angle": 43.3,
            "attack_angle": 8.08176374190374,
            "attack_direction": -0.5911166669044164,
            "swing_path_tilt": 34.22369587995779,
            "rate_ideal_attack_angle": 0.4996028594122319,
            "intercept_ball_minus_batter_pos_x_inches": 36.40552248747585,
            "intercept_ball_minus_batter_pos_y_inches": 29.21433539386849,
        },
    )
