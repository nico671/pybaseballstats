from typing import Union

import pandas as pd
import polars as pl
import requests

from pybaseballstats.utils.statcast_utils import _handle_dates

BAT_TRACKING_URL = "https://baseballsavant.mlb.com/leaderboard/bat-tracking?attackZone=&batSide=&contactType=&count=&dateStart={start_dt}&dateEnd={end_dt}&gameType=&groupBy=&isHardHit=&minSwings={min_swings}&minGroupSwings=1&pitchHand=&pitchType=&seasonStart=&seasonEnd=&team=&type={perspective}&csv=true"


def statcast_bat_tracking_leaderboard(
    start_dt: str,
    end_dt: str,
    min_swings: Union[int, str] = "q",
    perspective: str = "batter",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves bat tracking leaderboard data from Baseball Savant

    Args:
        start_dt (str): start date in format 'YYYY-MM-DD'
        end_dt (str): end date in format 'YYYY-MM-DD'
        min_swings (Union[int, str], optional): Minimum swing count to be included in the data ("q" stands for qualified). Defaults to "q".
        perspective (str, optional): What perspective to return data from. Options are: 'batter', 'batting-team', 'pitcher', 'pitching-team', 'league'. Defaults to "batter".
        return_pandas (bool, optional): Whether or not to return the data as a Pandas DataFrame or not. Defaults to False (Polars DataFrame will be returned).

    Raises:
        ValueError: If start_dt or end_dt are None
        ValueError: If start_dt or end_dt have a year before 2023
        ValueError: If start_dt is after end_dt
        ValueError: If min_swings is an int and less than 1
        ValueError: If min_swings is a string and not 'q'
        ValueError: If perspective is not one of 'batter', 'batting-team', 'pitcher', 'pitching-team', 'league'

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame containing the bat tracking leaderboard data
    """
    if start_dt is None or end_dt is None:
        raise ValueError("Both start_dt and end_dt must be provided")
    start_dt, end_dt = _handle_dates(start_dt, end_dt)
    if start_dt.year < 2023 or end_dt.year < 2023:
        raise ValueError("Bat tracking data is only available from 2023 onwards")
    if start_dt > end_dt:
        raise ValueError("Start date must be before end date")
    if type(min_swings) is int:
        if min_swings < 1:
            raise ValueError("min_swings must be at least 1")
    elif type(min_swings) is str:
        if min_swings != "q":
            raise ValueError("if min_swings is a string, it must be 'q' for qualified")
    if perspective not in [
        "batter",
        "batting-team",
        "pitcher",
        "pitching-team",
        "league",
    ]:
        raise ValueError(
            "perspective must be one of 'batter', 'batting-team', 'pitcher', 'pitching-team', 'league'"
        )
    df = pl.read_csv(
        requests.get(
            BAT_TRACKING_URL.format(
                start_dt=start_dt,
                end_dt=end_dt,
                min_swings=min_swings,
                perspective=perspective,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


EXIT_VELO_BARRELS_URL = "https://baseballsavant.mlb.com/leaderboard/statcast?type={perspective}&year={year}&position=&team=&min={min_swings}&sort=barrels_per_pa&sortDir=desc&csv=true"


def statcast_exit_velo_barrels_leaderboard(
    year: int,
    perspective: str = "batter",
    min_swings: Union[str, int] = "q",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves exit velocity barrels leaderboard data from Baseball Savant

    Args:
        year (int): What year to retrieve data from
        perspective (str, optional): What perspective to return data from. Options are: 'batter', 'pitcher', 'batter-team', or 'pitcher-team'. Defaults to "batter".
        min_swings (Union[str, int], optional): minimum number of swings to be included in the data ("q" returns all qualified players). Defaults to "q".
        return_pandas (bool, optional): Whether or not to return the data as a Pandas DataFrame or not. Defaults to False (Polars DataFrame will be returned).

    Raises:
        ValueError: if year is None
        ValueError: if year is before 2015
        ValueError: if min_swings is an int and less than 1
        ValueError: if min_swings is a string and not 'q'
        ValueError: if perspective is not one of 'batter', 'pitcher', 'batter-team', 'pitcher-team'

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame containing the exit velocity barrels leaderboard data
    """
    if year is None:
        raise ValueError("year must be provided")
    if year < 2015:
        raise ValueError(
            "Dates must be after 2015 as exit velo barrels data is only available from 2015 onwards"
        )
    if type(min_swings) is int:
        if min_swings < 1:
            raise ValueError("min_swings must be at least 1")
    elif type(min_swings) is str:
        if min_swings != "q":
            raise ValueError("if min_swings is a string, it must be 'q' for qualified")
    if perspective not in ["batter", "pitcher", "batter-team", "pitcher-team"]:
        raise ValueError(
            "perspective must be either 'batter', 'pitcher', 'batter-team', or 'pitcher-team'"
        )
    df = pl.read_csv(
        requests.get(
            EXIT_VELO_BARRELS_URL.format(
                year=year,
                min_swings=min_swings,
                perspective=perspective,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


EXPECTED_STATS_URL = "https://baseballsavant.mlb.com/leaderboard/expected_statistics?type={perspective}&year={year}&position=&team=&filterType=bip&min={min_balls_in_play}&csv=true"


def statcast_expected_stats_leaderboard(
    year: int,
    perspective: str = "batter",
    min_balls_in_play: Union[str, int] = "q",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves expected statistics leaderboard data from Baseball Savant

    Args:
        year (int): Year to retrieve data from
        perspective (str, optional): What perspective to return data from. Options are: 'batter', 'pitcher', 'batter-team', or 'pitcher-team'. Defaults to "batter".
        min_balls_in_play (Union[str, int], optional): Minimum number of balls in play to be included in the data ("q" returns all qualified players). Defaults to "q".
        return_pandas (bool, optional): Whether or not to return the data as a Pandas DataFrame or not. Defaults to False (Polars DataFrame will be returned).

    Raises:
        ValueError: if year is None
        ValueError: if year is before 2015
        ValueError: if min_swings is an int and less than 1
        ValueError: if min_swings is a string and not 'q'
        ValueError: if perspective is not one of 'batter', 'pitcher', 'batter-team', 'pitcher-team'

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame containing the expected stats leaderboard data
    """
    if year is None:
        raise ValueError("year must be provided")
    if year < 2015:
        raise ValueError(
            "Dates must be after 2015 as exit velo barrels data is only available from 2015 onwards"
        )
    if type(min_balls_in_play) is int:
        if min_balls_in_play < 1:
            raise ValueError("min_swings must be at least 1")
    elif type(min_balls_in_play) is str:
        if min_balls_in_play != "q":
            raise ValueError("if min_swings is a string, it must be 'q' for qualified")
    if perspective not in ["batter", "pitcher", "batter-team", "pitcher-team"]:
        raise ValueError(
            "perspective must be either 'batter', 'pitcher', 'batter-team', or 'pitcher-team'"
        )
    df = pl.read_csv(
        requests.get(
            EXIT_VELO_BARRELS_URL.format(
                year=year,
                min_swings=min_balls_in_play,
                perspective=perspective,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


PITCH_ARSENAL_STATS_URL = "https://baseballsavant.mlb.com/leaderboard/pitch-arsenal-stats?type={perspective}&pitchType={pitch_type}&year={year}&team=&min={min_pa}&csv=true"


def statcast_pitch_arsenal_stats_leaderboard(
    year: int,
    perspective: str = "batter",
    min_pa: int = 100,
    pitch_type: str = "",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves pitch arsenal statistics leaderboard data from Baseball Savant

    Args:
        year (int): Year to retrieve data from
        perspective (str, optional): What perspective to return data from. Options are: 'batter', 'pitcher'. Defaults to "batter".
        min_pa (int, optional): Minimum plate appearances to be included in the data. Defaults to 150.
        pitch_type (str, optional): Type of pitch to filter by. Options are: 'ST' (sweeper), 'FS' (split-finger), 'SV' (slurve), 'SL' (slider), 'SI' (sinker), 'SC' (screwball), 'KN' (knuckleball), 'FC' (cutter), 'CU' (curveball), 'CH' (changeup), 'FF' (4-Seam Fastball), or '' (all). Defaults to "".
        return_pandas (bool, optional): Whether or not to return the data as a Pandas DataFrame or not. Defaults to False (Polars DataFrame will be returned).

    Raises:
        ValueError: If year is None
        ValueError: If year is before 2019
        ValueError: If min_pa is less than 1
        ValueError: If perspective is not one of 'batter', 'pitcher'
        ValueError: If pitch_type is not one of 'ST', 'FS', 'SV', 'SL', 'SI', 'SC', 'KN', 'FC', 'CU', 'CH', 'FF', or ''

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame containing the pitch arsenal statistics leaderboard data
    """
    if year is None:
        raise ValueError("year must be provided")
    if year < 2019:
        raise ValueError(
            "Dates must be after 2019 as pitch arsenal data is only available from 2019 onwards"
        )
    if min_pa < 1:
        raise ValueError("min_pa must be at least 1")
    if perspective not in ["batter", "pitcher"]:
        raise ValueError("perspective must be either 'batter' or 'pitcher'")
    if pitch_type not in [
        "ST",
        "FS",
        "SV",
        "SL",
        "SI",
        "SC",
        "KN",
        "FC",
        "CU",
        "CH",
        "FF",
        "",
    ]:
        raise ValueError(
            "pitch_type must be one of 'ST', 'FS', 'SV', 'SL', 'SI', 'SC', 'KN', 'FC', 'CU', 'CH', 'FF', or ''"
        )
    df = pl.read_csv(
        requests.get(
            PITCH_ARSENAL_STATS_URL.format(
                year=year,
                min_pa=min_pa,
                perspective=perspective,
                pitch_type=pitch_type,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


PITCH_ARSENALS_URL = "https://baseballsavant.mlb.com/leaderboard/pitch-arsenals?year={year}&min={min_pitches}&type={type}&hand={hand}&csv=true"


def statcast_pitch_arsenals_leaderboard(
    year: int,
    min_pitches: int = 100,
    pitch_type: str = "",
    hand: str = "",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if year is None:
        raise ValueError("year must be provided")
    if year < 2017:
        raise ValueError(
            "Dates must be after 2017 as pitch arsenal data is only available from 2017 onwards"
        )
    if min_pitches < 1:
        raise ValueError("min_pitches must be at least 1")
    if pitch_type not in [
        "ST",
        "FS",
        "SV",
        "SL",
        "SI",
        "SC",
        "KN",
        "FC",
        "CU",
        "CH",
        "FF",
        "",
    ]:
        raise ValueError(
            "pitch_type must be one of 'ST', 'FS', 'SV', 'SL', 'SI', 'SC', 'KN', 'FC', 'CU', 'CH', 'FF', or ''"
        )
    if hand not in ["R", "L", ""]:
        raise ValueError("hand must be one of 'R', 'L', or ''")
    types = ["avg_speed", "n_", "avg_spin"]
    df_list = []

    for t in types:
        df = pl.read_csv(
            requests.get(
                PITCH_ARSENALS_URL.format(year=2024, min_pitches=100, type=t, hand="R")
            ).content
        )

        if t != "avg_speed":
            df = df.drop(
                "last_name, first_name",
            )
        df_list.append(df)
    df = df_list[0]

    for d in df_list[1:]:
        df = df.join(d, on="pitcher", how="inner")
    df = df.rename(
        {
            "n_ff": "ff_usage_rate",
            "n_sl": "sl_usage_rate",
            "n_si": "si_usage_rate",
            "n_fc": "fc_usage_rate",
            "n_ch": "ch_usage_rate",
            "n_cu": "cu_usage_rate",
            "n_fs": "fs_usage_rate",
            "n_sv": "sv_usage_rate",
            "n_kn": "kn_usage_rate",
            "n_st": "st_usage_rate",
        }
    )
    df = df.with_columns(
        pl.col(pl.String).str.replace("", "0"),
    )
    df = df.with_columns(
        [
            pl.col("ff_usage_rate").cast(pl.Float32),
            pl.col("sl_usage_rate").cast(pl.Float32),
            pl.col("si_usage_rate").cast(pl.Float32),
            pl.col("fc_usage_rate").cast(pl.Float32),
            pl.col("ch_usage_rate").cast(pl.Float32),
            pl.col("cu_usage_rate").cast(pl.Float32),
            pl.col("fs_usage_rate").cast(pl.Float32),
            pl.col("sv_usage_rate").cast(pl.Float32),
            pl.col("kn_usage_rate").cast(pl.Float32),
            pl.col("st_usage_rate").cast(pl.Float32),
        ]
    )
    return df if not return_pandas else df.to_pandas()


ARM_STRENGTH_URL = "https://baseballsavant.mlb.com/leaderboard/arm-strength?type={perspective}&year={year}&minThrows={min_throws}&pos=&team=&csv=true"


def statcast_arm_strength_leaderboard(
    year: int,
    perspective: str = "player",
    min_throws: int = 50,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if year is None:
        raise ValueError("year must be provided")
    if year < 2020:
        raise ValueError(
            "Dates must be after 2020 as arm strength data is only available from 2020 onwards"
        )
    if min_throws < 1:
        raise ValueError("min_throws must be at least 1")
    if perspective not in ["player", "team"]:
        raise ValueError("perspective must be either 'player' or 'team'")
    df = pl.read_csv(
        requests.get(
            ARM_STRENGTH_URL.format(
                year=year, min_throws=min_throws, perspective=perspective
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


# # ARM_VALUE_URL = "https://baseballsavant.mlb.com/leaderboard/baserunning?game_type=All&n=top&key_base_out=All&season_end={end_year}&season_start={start_year}&split=no&team=&type=Fld&with_team_only=1&csv=true"


# # def statcast_arm_value(
# #     start_year: int, end_year: int, return_pandas: bool = False
# # ) -> pl.DataFrame | pd.DataFrame:
# #     if start_year < 2016 or end_year < 2016:
# #         raise ValueError(
# #             "Dates must be after 2016 as arm value data is only available from 2016 onwards"
# #         )
# #     if start_year > end_year:
# #         raise ValueError("Start year must be before end year")
# #     df = pl.read_csv(
# #         requests.get(
# #             ARM_VALUE_URL.format(start_year=start_year, end_year=end_year)
# #         ).content,
# #         truncate_ragged_lines=True,
# #     )
# #     return df if not return_pandas else df.to_pandas()


# # catcher blocking available from 2018 onwards
# CATCHER_BLOCKING_URL = "https://baseballsavant.mlb.com/leaderboard/catcher-blocking?game_type=All&n=1&season_end={end_season}&season_start={start_season}&split=no&team=&type=Cat&with_team_only=1&sortColumn=diff_runner_pbwp&sortDirection=desc&players={players}&selected_idx=0&csv=true"
# # catcher framing available from 2015 onwards
# CATCHER_FRAMING_URL = "https://baseballsavant.mlb.com/catcher_framing?year={year}&team=&min=1&type=catcher&sort=4%2C1&csv=true"
# # catcher pop time available from 2015 onwards
# CATCHER_POP_TIME_URL = "https://baseballsavant.mlb.com/leaderboard/poptime?year={year}&team=&min2b=5&min3b=0&csv=true"
# # catcher throwing available from 2016 onwards
# CATCHER_THROWING_URL = "https://baseballsavant.mlb.com/leaderboard/catcher-throwing?game_type=All&n=q&season_end={end_season}&season_start={start_season}&split=no&team=&type=Cat&with_team_only=1&target_base=All&csv=true"


# # FIXME: figure out how players= works for blocking url
# def statcast_catcher_stats(
#     start_season: int,
#     end_season: int,
#     return_pandas: bool = False,
# ) -> pl.DataFrame | pd.DataFrame:
#     if start_season < 2018 or end_season < 2018:
#         raise ValueError(
#             "Dates must be after 2018 as catcher blocking data is only available from 2018 onwards"
#         )
#     if start_season > end_season:
#         raise ValueError("Start season must be before end season")
#     df_list = []

#     for year in range(start_season, end_season + 1):
#         players = ""
#         if year == 2018:
#             players = "571466-2018-113"
#         elif year == 2019:
#             players = "547379-2019-114"
#         elif year == 2020:
#             players = "571466-2020-113"
#         elif year == 2021:
#             players = "607732-2021-134"
#         elif year == 2022:
#             players = "668939-2022-110"
#         elif year == 2023:
#             players = "669221-2023-144"
#         elif year == 2024:
#             players = "643376-2024-111"
#         else:
#             print("warning: unexpected error, please contact developer")
#         catcher_blocking = pl.read_csv(
#             requests.get(
#                 CATCHER_BLOCKING_URL.format(
#                     players=players,
#                     start_season=year,
#                     end_season=year,
#                 )
#             ).content,
#             truncate_ragged_lines=True,
#         )
#         catcher_blocking = catcher_blocking.with_columns(
#             [
#                 pl.col("player_id").cast(pl.Int32).alias("player_id"),
#             ]
#         )
#         catcher_framing = pl.read_csv(
#             requests.get(CATCHER_FRAMING_URL.format(year=year)).content,
#             truncate_ragged_lines=True,
#         ).filter(pl.col("player_id") != "")
#         catcher_framing = catcher_framing.with_columns(
#             [
#                 pl.col("player_id").cast(pl.Int32).alias("player_id"),
#             ]
#         )
#         catcher_pop_time = pl.read_csv(
#             requests.get(CATCHER_POP_TIME_URL.format(year=year)).content,
#             truncate_ragged_lines=True,
#         )
#         catcher_pop_time = catcher_pop_time.with_columns(
#             [
#                 pl.col("player_id").cast(pl.Int32).alias("player_id"),
#             ]
#         )
#         catcher_throwing = pl.read_csv(
#             requests.get(
#                 CATCHER_THROWING_URL.format(start_season=year, end_season=year)
#             ).content,
#             truncate_ragged_lines=True,
#         )

#         catcher_throwing = catcher_throwing.with_columns(
#             [
#                 pl.col("player_id").cast(pl.Int32).alias("player_id"),
#             ]
#         )
#         df = catcher_blocking.join(catcher_framing, on="player_id", how="inner")
#         df = df.join(
#             catcher_pop_time, left_on="player_name", right_on="catcher", how="inner"
#         )
#         df = df.join(catcher_throwing, on="player_id", how="inner")
#         df = df.drop(
#             [
#                 "start_year",
#                 "end_year",
#                 "last_name",
#                 "first_name",
#                 "year",
#                 "player_id_right",
#                 "player_name_right",
#                 "team_name_right",
#                 "start_year_right",
#                 "end_year_right",
#                 "team_id",
#             ]
#         )
#         df_list.append(df)
#     df = (
#         pl.concat(df_list)
#         .group_by("player_id", maintain_order=True)
#         .agg(
#             pl.col("player_name").first().alias("player_name"),
#             pl.col("age").unique().alias("ages"),
#             pl.col("pitches").sum().alias("pitches"),
#             pl.col("n_pbwp").sum().alias("n_pbwp"),
#             pl.col("x_pbwp").sum().alias("x_pbwp"),
#             pl.col("freq_pbwp_easy").mean().alias("freq_pbwp_easy"),
#             pl.col("freq_pbwp_medium").mean().alias("freq_pbwp_medium"),
#             pl.col("freq_pbwp_tough").mean().alias("freq_pbwp_tough"),
#             pl.col("diff_pbwp_easy").mean().alias("diff_pbwp_easy"),
#             pl.col("diff_pbwp_medium").mean().alias("diff_pbwp_medium"),
#             pl.col("diff_pbwp_tough").mean().alias("diff_pbwp_tough"),
#             pl.col("catcher_blocking_runs").sum().alias("catcher_blocking_runs"),
#             pl.col("blocks_above_average").sum().alias("blocks_above_average"),
#             pl.col("blocks_above_average_per_game")
#             .mean()
#             .alias("blocks_above_average_per_game"),
#             pl.col("n_called_pitches").sum().alias("n_called_pitches"),
#             pl.col("runs_extra_strikes").sum().alias("runs_extra_strikes"),
#             pl.col("strike_rate").mean().alias("strike_rate"),
#             pl.col("strike_rate_11").mean().alias("strike_rate_zone_11"),
#             pl.col("strike_rate_12").mean().alias("strike_rate_zone_12"),
#             pl.col("strike_rate_13").mean().alias("strike_rate_zone_13"),
#             pl.col("strike_rate_14").mean().alias("strike_rate_zone_14"),
#             pl.col("strike_rate_16").mean().alias("strike_rate_zone_16"),
#             pl.col("strike_rate_17").mean().alias("strike_rate_zone_17"),
#             pl.col("strike_rate_18").mean().alias("strike_rate_zone_18"),
#             pl.col("strike_rate_19").mean().alias("strike_rate_zone_19"),
#             pl.col("maxeff_arm_2b_3b_sba").mean().alias("maxeff_arm_2b_3b_sba"),
#             pl.col("exchange_2b_3b_sba").mean().alias("exchange_2b_3b_sba"),
#             pl.col("pop_2b_sba_count").sum().alias("pop_2b_sba_count"),
#             pl.col("pop_2b_sba").mean().alias("pop_2b_sba"),
#             pl.col("pop_2b_cs").mean().alias("pop_2b_cs"),
#             pl.col("pop_2b_sb").mean().alias("pop_2b_sb"),
#             pl.col("pop_3b_sba_count").sum().alias("pop_3b_sba_count"),
#             pl.col("pop_3b_sba").mean().alias("pop_3b_sba"),
#             pl.col("pop_3b_cs").mean().alias("pop_3b_cs"),
#             pl.col("pop_3b_sb").mean().alias("pop_3b_sb"),
#             pl.col("sb_attempts").sum().alias("sb_attempts"),
#             pl.col("catcher_stealing_runs").sum().alias("catcher_stealing_runs"),
#             pl.col("caught_stealing_above_average")
#             .sum()
#             .alias("caught_stealing_above_average"),
#             pl.col("n_cs").sum().alias("n_cs"),
#             pl.col("rate_cs").mean().alias("rate_cs"),
#             pl.col("est_cs_pct").mean().alias("est_cs_pct"),
#             pl.col("cs_aa_per_throw").mean().alias("cs_aa_per_throw"),
#             pl.col("seasonal_runner_speed").mean().alias("seasonal_runner_speed"),
#             pl.col("runner_distance_from_second")
#             .mean()
#             .alias("runner_distance_from_second"),
#             pl.col("pop_time").mean().alias("pop_time"),
#             pl.col("exchange_time").mean().alias("exchange_time"),
#             pl.col("arm_strength").mean().alias("arm_strength"),
#             pl.col("n_xcs_with_flight_over_xcs")
#             .sum()
#             .alias("n_xcs_with_flight_over_xcs"),
#             pl.col("n_xcs_with_exchange_over_xcs")
#             .sum()
#             .alias("n_xcs_with_exchange_over_xcs"),
#             pl.col("n_xcs_with_accuracy_over_xcs")
#             .sum()
#             .alias("n_xcs_with_accuracy_over_xcs"),
#             pl.col("n_xcs_with_ground_other_over_xcs")
#             .sum()
#             .alias("n_xcs_with_ground_other_over_xcs"),
#             pl.col("n_xcs_with_onfly_other_over_xcs")
#             .sum()
#             .alias("n_xcs_with_onfly_other_over_xcs"),
#             pl.col("n_xcs_with_untracked_other_over_xcs")
#             .sum()
#             .alias("n_xcs_with_untracked_other_over_xcs"),
#         )
#     )

#     if return_pandas:
#         return df.to_pandas()
#     return df
