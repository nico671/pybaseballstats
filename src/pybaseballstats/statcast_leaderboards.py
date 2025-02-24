import pandas as pd
import polars as pl
import requests

from pybaseballstats.utils.statcast_utils import _handle_dates

BAT_TRACKING_URL = "https://baseballsavant.mlb.com/leaderboard/bat-tracking?attackZone=&batSide=&contactType=&count=&dateStart={start_dt}&dateEnd={end_dt}&gameType=&groupBy=&isHardHit=&minSwings=q&minGroupSwings=1&pitchHand=&pitchType=&seasonStart=&seasonEnd=&team=&type={pitcher_batter}&csv=true"
EXIT_VELO_BARRELS_URL = "https://baseballsavant.mlb.com/leaderboard/statcast?type={pitcher_batter}&year={year}&position=&team=&min=q&sort=barrels_per_pa&sortDir=desc&csv=true"


def statcast_bat_tracking(
    start_dt: str,
    end_dt: str,
    pitcher_batter: str = "batter",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if start_dt is None or end_dt is None:
        raise ValueError("start_dt and end_dt must be provided")
    start_dt, end_dt = _handle_dates(start_dt, end_dt)
    if start_dt.year < 2023 or end_dt.year < 2023:
        raise ValueError(
            "Dates must be after 2023 as bat tracking data is only available from 2023 onwards"
        )
    if pitcher_batter not in ["pitcher", "batter"]:
        raise ValueError("pitcher_batter must be either 'pitcher' or 'batter'")
    df = pl.read_csv(
        requests.get(
            BAT_TRACKING_URL.format(
                start_dt=start_dt, end_dt=end_dt, pitcher_batter=pitcher_batter
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


def statcast_exit_velo_barrels(
    year: int, pitcher_batter: str = "batter", return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    if year is None:
        raise ValueError("year must be provided")
    if year < 2015:
        raise ValueError(
            "Dates must be after 2015 as exit velo/ barrels data is only available from 2015 onwards"
        )
    if pitcher_batter not in ["pitcher", "batter"]:
        raise ValueError("pitcher_batter must be either 'pitcher' or 'batter'")
    df = pl.read_csv(
        requests.get(
            EXIT_VELO_BARRELS_URL.format(year=year, pitcher_batter=pitcher_batter)
        ).content
    )
    return df if not return_pandas else df.to_pandas()


EXPECTED_STATS_URL = "https://baseballsavant.mlb.com/leaderboard/expected_statistics?type={pitcher_batter}&year={year}&position=&team=&filterType=bip&min=q&csv=true"


def statcast_expected_stats(
    year: int, pitcher_batter: str = "batter", return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    if year is None:
        raise ValueError("year must be provided")
    if year < 2015:
        raise ValueError(
            "Dates must be after 2015 as expected stats data is only available from 2015 onwards"
        )
    if pitcher_batter not in ["pitcher", "batter"]:
        raise ValueError("pitcher_batter must be either 'pitcher' or 'batter'")
    df = pl.read_csv(
        requests.get(
            EXPECTED_STATS_URL.format(pitcher_batter=pitcher_batter, year=year)
        ).content,
        truncate_ragged_lines=True,
    )
    return df if not return_pandas else df.to_pandas()


PITCH_ARSENAL_URL = "https://baseballsavant.mlb.com/leaderboard/pitch-arsenal-stats?type={pitcher_batter}&pitchType=&year={year}&team=&min=150&csv=true"


def statcast_pitch_arsenal(
    year: int, pitcher_batter: str = "pitcher", return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    if year is None:
        raise ValueError("year must be provided")
    if year < 2019:
        raise ValueError(
            "Dates must be after 2019 as pitch arsenal data is only available from 2019 onwards"
        )
    if pitcher_batter not in ["pitcher", "batter"]:
        raise ValueError("pitcher_batter must be either 'pitcher' or 'batter'")
    df = pl.read_csv(
        requests.get(
            PITCH_ARSENAL_URL.format(pitcher_batter=pitcher_batter, year=year)
        ).content,
        truncate_ragged_lines=True,
    )
    return df if not return_pandas else df.to_pandas()


PITCHING_ACTIVE_SPIN_URL = "https://baseballsavant.mlb.com/leaderboard/active-spin?year={year}_spin-based&min=50&hand=&csv=true"


def statcast_pitching_active_spin(
    year: int, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    if year is None:
        raise ValueError("year must be provided")
    if year < 2020:
        raise ValueError(
            "Dates must be after 2020 as spin tracking data is only available from 2020 onwards"
        )
    df = pl.read_csv(
        requests.get(PITCHING_ACTIVE_SPIN_URL.format(year=year)).content,
        truncate_ragged_lines=True,
    )
    return df if not return_pandas else df.to_pandas()


PITCHING_ARM_ANGLE_URL = "https://baseballsavant.mlb.com/leaderboard/pitcher-arm-angles?batSide=&dateStart={start_dt}&dateEnd={end_dt}&gameType=R%7CF%7CD%7CL%7CW&groupBy=&min=q&minGroupPitches=1&perspective=back&pitchHand=&pitchType=&season={season}&size=small&sort=ascending&team=&csv=true"


def statcast_pitching_arm_angle(
    start_dt: str,
    end_dt: str,
    season: int = None,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if season is not None:
        print("WARNING: start_dt and end_dt will be ignored as season is provided")
        start_dt = None
        end_dt = None
        if season < 2023:
            raise ValueError(
                "Dates must be after 2023 as arm angle data is only available from 2023 onwards"
            )
    else:
        if start_dt is not None and end_dt is not None:
            start_dt, end_dt = _handle_dates(start_dt, end_dt)
            if start_dt.year < 2023 or end_dt.year < 2023:
                raise ValueError(
                    "Dates must be after 2023 as arm angle data is only available from 2023 onwards"
                )
            if start_dt > end_dt:
                raise ValueError("Start date must be before end date")
        else:
            raise ValueError(
                "Both start_dt and end_dt must be provided if season is not"
            )

    df = pl.read_csv(
        requests.get(
            PITCHING_ARM_ANGLE_URL.format(
                start_dt=start_dt if start_dt is not None else "",
                end_dt=end_dt if end_dt is not None else "",
                season=season,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


# TODO: just combine these tbh
# ARM_STRENGTH_URL = "https://baseballsavant.mlb.com/leaderboard/arm-strength?type=player&year={year}&minThrows=50&pos=&team=&csv=true"


# def statcast_arm_strength(
#     year: int, return_pandas: bool = False
# ) -> pl.DataFrame | pd.DataFrame:
#     if year is None:
#         raise ValueError("year must be provided")
#     if year < 2020:
#         raise ValueError(
#             "Dates must be after 2020 as arm strength data is only available from 2020 onwards"
#         )
#     df = pl.read_csv(
#         requests.get(ARM_STRENGTH_URL.format(year=year)).content,
#         truncate_ragged_lines=True,
#     )
#     return df if not return_pandas else df.to_pandas()


# ARM_VALUE_URL = "https://baseballsavant.mlb.com/leaderboard/baserunning?game_type=All&n=top&key_base_out=All&season_end={end_year}&season_start={start_year}&split=no&team=&type=Fld&with_team_only=1&csv=true"


# def statcast_arm_value(
#     start_year: int, end_year: int, return_pandas: bool = False
# ) -> pl.DataFrame | pd.DataFrame:
#     if start_year < 2016 or end_year < 2016:
#         raise ValueError(
#             "Dates must be after 2016 as arm value data is only available from 2016 onwards"
#         )
#     if start_year > end_year:
#         raise ValueError("Start year must be before end year")
#     df = pl.read_csv(
#         requests.get(
#             ARM_VALUE_URL.format(start_year=start_year, end_year=end_year)
#         ).content,
#         truncate_ragged_lines=True,
#     )
#     return df if not return_pandas else df.to_pandas()


# catcher blocking available from 2018 onwards
CATCHER_BLOCKING_URL = "https://baseballsavant.mlb.com/leaderboard/catcher-blocking?game_type=All&n=1&season_end={end_season}&season_start={start_season}&split=no&team=&type=Cat&with_team_only=1&sortColumn=diff_runner_pbwp&sortDirection=desc&players={players}&selected_idx=0&csv=true"
# catcher framing available from 2015 onwards
CATCHER_FRAMING_URL = "https://baseballsavant.mlb.com/catcher_framing?year={year}&team=&min=1&type=catcher&sort=4%2C1&csv=true"
# catcher pop time available from 2015 onwards
CATCHER_POP_TIME_URL = "https://baseballsavant.mlb.com/leaderboard/poptime?year={year}&team=&min2b=5&min3b=0&csv=true"
# catcher throwing available from 2016 onwards
CATCHER_THROWING_URL = "https://baseballsavant.mlb.com/leaderboard/catcher-throwing?game_type=All&n=q&season_end={end_season}&season_start={start_season}&split=no&team=&type=Cat&with_team_only=1&target_base=All&csv=true"


# FIXME: figure out how players= works for blocking url
def statcast_catcher_stats(
    start_season: int,
    end_season: int,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if start_season < 2018 or end_season < 2018:
        raise ValueError(
            "Dates must be after 2018 as catcher blocking data is only available from 2018 onwards"
        )
    if start_season > end_season:
        raise ValueError("Start season must be before end season")
    df_list = []

    for year in range(start_season, end_season + 1):
        players = ""
        if year == 2018:
            players = "571466-2018-113"
        elif year == 2019:
            players = "547379-2019-114"
        elif year == 2020:
            players = "571466-2020-113"
        elif year == 2021:
            players = "607732-2021-134"
        elif year == 2022:
            players = "668939-2022-110"
        elif year == 2023:
            players = "669221-2023-144"
        elif year == 2024:
            players = "643376-2024-111"
        else:
            print("warning: unexpected error, please contact developer")
        catcher_blocking = pl.read_csv(
            requests.get(
                CATCHER_BLOCKING_URL.format(
                    players=players,
                    start_season=year,
                    end_season=year,
                )
            ).content,
            truncate_ragged_lines=True,
        )
        catcher_blocking = catcher_blocking.with_columns(
            [
                pl.col("player_id").cast(pl.Int32).alias("player_id"),
            ]
        )
        catcher_framing = pl.read_csv(
            requests.get(CATCHER_FRAMING_URL.format(year=year)).content,
            truncate_ragged_lines=True,
        ).filter(pl.col("player_id") != "")
        catcher_framing = catcher_framing.with_columns(
            [
                pl.col("player_id").cast(pl.Int32).alias("player_id"),
            ]
        )
        catcher_pop_time = pl.read_csv(
            requests.get(CATCHER_POP_TIME_URL.format(year=year)).content,
            truncate_ragged_lines=True,
        )
        catcher_pop_time = catcher_pop_time.with_columns(
            [
                pl.col("player_id").cast(pl.Int32).alias("player_id"),
            ]
        )
        catcher_throwing = pl.read_csv(
            requests.get(
                CATCHER_THROWING_URL.format(start_season=year, end_season=year)
            ).content,
            truncate_ragged_lines=True,
        )

        catcher_throwing = catcher_throwing.with_columns(
            [
                pl.col("player_id").cast(pl.Int32).alias("player_id"),
            ]
        )
        df = catcher_blocking.join(catcher_framing, on="player_id", how="inner")
        df = df.join(
            catcher_pop_time, left_on="player_name", right_on="catcher", how="inner"
        )
        df = df.join(catcher_throwing, on="player_id", how="inner")
        df = df.drop(
            [
                "start_year",
                "end_year",
                "last_name",
                "first_name",
                "year",
                "player_id_right",
                "player_name_right",
                "team_name_right",
                "start_year_right",
                "end_year_right",
                "team_id",
            ]
        )
        df_list.append(df)
    df = (
        pl.concat(df_list)
        .group_by("player_id", maintain_order=True)
        .agg(
            pl.col("player_name").first().alias("player_name"),
            pl.col("age").unique().alias("ages"),
            pl.col("pitches").sum().alias("pitches"),
            pl.col("n_pbwp").sum().alias("n_pbwp"),
            pl.col("x_pbwp").sum().alias("x_pbwp"),
            pl.col("freq_pbwp_easy").mean().alias("freq_pbwp_easy"),
            pl.col("freq_pbwp_medium").mean().alias("freq_pbwp_medium"),
            pl.col("freq_pbwp_tough").mean().alias("freq_pbwp_tough"),
            pl.col("diff_pbwp_easy").mean().alias("diff_pbwp_easy"),
            pl.col("diff_pbwp_medium").mean().alias("diff_pbwp_medium"),
            pl.col("diff_pbwp_tough").mean().alias("diff_pbwp_tough"),
            pl.col("catcher_blocking_runs").sum().alias("catcher_blocking_runs"),
            pl.col("blocks_above_average").sum().alias("blocks_above_average"),
            pl.col("blocks_above_average_per_game")
            .mean()
            .alias("blocks_above_average_per_game"),
            pl.col("n_called_pitches").sum().alias("n_called_pitches"),
            pl.col("runs_extra_strikes").sum().alias("runs_extra_strikes"),
            pl.col("strike_rate").mean().alias("strike_rate"),
            pl.col("strike_rate_11").mean().alias("strike_rate_zone_11"),
            pl.col("strike_rate_12").mean().alias("strike_rate_zone_12"),
            pl.col("strike_rate_13").mean().alias("strike_rate_zone_13"),
            pl.col("strike_rate_14").mean().alias("strike_rate_zone_14"),
            pl.col("strike_rate_16").mean().alias("strike_rate_zone_16"),
            pl.col("strike_rate_17").mean().alias("strike_rate_zone_17"),
            pl.col("strike_rate_18").mean().alias("strike_rate_zone_18"),
            pl.col("strike_rate_19").mean().alias("strike_rate_zone_19"),
            pl.col("maxeff_arm_2b_3b_sba").mean().alias("maxeff_arm_2b_3b_sba"),
            pl.col("exchange_2b_3b_sba").mean().alias("exchange_2b_3b_sba"),
            pl.col("pop_2b_sba_count").sum().alias("pop_2b_sba_count"),
            pl.col("pop_2b_sba").mean().alias("pop_2b_sba"),
            pl.col("pop_2b_cs").mean().alias("pop_2b_cs"),
            pl.col("pop_2b_sb").mean().alias("pop_2b_sb"),
            pl.col("pop_3b_sba_count").sum().alias("pop_3b_sba_count"),
            pl.col("pop_3b_sba").mean().alias("pop_3b_sba"),
            pl.col("pop_3b_cs").mean().alias("pop_3b_cs"),
            pl.col("pop_3b_sb").mean().alias("pop_3b_sb"),
            pl.col("sb_attempts").sum().alias("sb_attempts"),
            pl.col("catcher_stealing_runs").sum().alias("catcher_stealing_runs"),
            pl.col("caught_stealing_above_average")
            .sum()
            .alias("caught_stealing_above_average"),
            pl.col("n_cs").sum().alias("n_cs"),
            pl.col("rate_cs").mean().alias("rate_cs"),
            pl.col("est_cs_pct").mean().alias("est_cs_pct"),
            pl.col("cs_aa_per_throw").mean().alias("cs_aa_per_throw"),
            pl.col("seasonal_runner_speed").mean().alias("seasonal_runner_speed"),
            pl.col("runner_distance_from_second")
            .mean()
            .alias("runner_distance_from_second"),
            pl.col("pop_time").mean().alias("pop_time"),
            pl.col("exchange_time").mean().alias("exchange_time"),
            pl.col("arm_strength").mean().alias("arm_strength"),
            pl.col("n_xcs_with_flight_over_xcs")
            .sum()
            .alias("n_xcs_with_flight_over_xcs"),
            pl.col("n_xcs_with_exchange_over_xcs")
            .sum()
            .alias("n_xcs_with_exchange_over_xcs"),
            pl.col("n_xcs_with_accuracy_over_xcs")
            .sum()
            .alias("n_xcs_with_accuracy_over_xcs"),
            pl.col("n_xcs_with_ground_other_over_xcs")
            .sum()
            .alias("n_xcs_with_ground_other_over_xcs"),
            pl.col("n_xcs_with_onfly_other_over_xcs")
            .sum()
            .alias("n_xcs_with_onfly_other_over_xcs"),
            pl.col("n_xcs_with_untracked_other_over_xcs")
            .sum()
            .alias("n_xcs_with_untracked_other_over_xcs"),
        )
    )

    if return_pandas:
        return df.to_pandas()
    return df
