import json
from typing import Literal

import pandas as pd
import polars as pl
import requests
from bs4 import BeautifulSoup

from pybaseballstats.utils.statcast_utils import _handle_dates

BAT_TRACKING_URL = "https://baseballsavant.mlb.com/leaderboard/bat-tracking?attackZone=&batSide=&contactType=&count=&dateStart={start_dt}&dateEnd={end_dt}&gameType=&groupBy=&isHardHit=&minSwings={min_swings}&minGroupSwings=1&pitchHand=&pitchType=&seasonStart={start_season}&seasonEnd={end_season}&team=&type={perspective}&csv=true"

# TODO: usage docs


def statcast_bat_tracking_leaderboard(
    start_dt: str,
    end_dt: str,
    min_swings: int | str = "q",
    perspective: str = "batter",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves bat tracking leaderboard data from Baseball Savant

    Args:
        start_dt (str): start date in format 'YYYY-MM-DD'
        end_dt (str): end date in format 'YYYY-MM-DD'
        min_swings (int | str, optional): Minimum swing count to be included in the data ("q" stands for qualified). Defaults to "q".
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
    start_season = start_dt.year
    end_season = end_dt.year
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
                start_season=start_season,
                end_season=end_season,
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
    min_swings: int | str = "q",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves exit velocity barrels leaderboard data from Baseball Savant

    Args:
        year (int): What year to retrieve data from
        perspective (str, optional): What perspective to return data from. Options are: 'batter', 'pitcher', 'batter-team', or 'pitcher-team'. Defaults to "batter".
        min_swings (int | str, optional): minimum number of swings to be included in the data ("q" returns all qualified players). Defaults to "q".
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
    min_balls_in_play: int | str = "q",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves expected statistics leaderboard data from Baseball Savant

    Args:
        year (int): Year to retrieve data from
        perspective (str, optional): What perspective to return data from. Options are: 'batter', 'pitcher', 'batter-team', or 'pitcher-team'. Defaults to "batter".
        min_balls_in_play (int | str, optional): Minimum number of balls in play to be included in the data ("q" returns all qualified players). Defaults to "q".
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

    if hand not in ["R", "L", ""]:
        raise ValueError("hand must be one of 'R', 'L', or ''")
    df_list = []

    for t in ["avg_speed", "n_", "avg_spin"]:
        df = pl.read_csv(
            requests.get(
                PITCH_ARSENALS_URL.format(
                    year=year, min_pitches=min_pitches, type=t, hand=hand
                )
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


ARM_VALUE_URL = "https://baseballsavant.mlb.com/leaderboard/baserunning?game_type=All&n={min_oppurtunities}&key_base_out=All&season_end={end_season}&season_start={start_season}&split={split_years}&team=&type={perspective}&with_team_only=1&csv=true"


def statcast_arm_value_leaderboard(
    start_year: int,
    end_year: int,
    split_years: bool = False,
    perspective: str = "Fld",
    min_oppurtunities: int | str = "top",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves arm value leaderboard data from Baseball Savant

    Args:
        start_year (int): First year to retrieve data from
        end_year (int): Last year to retrieve data from
        split_years (bool, optional): Whether or not to split the data by year. Defaults to False.
        perspective (str, optional): What perspective to return data from. Options are: 'Fld' (data for fielders), 'Pit' (data for defenders while pitchers are pitching) or 'Pitching+Team' (team arm values on defense). Defaults to "Fld".
        min_oppurtunities (int | str, optional): Minimum number of oppurtunities to be included in the data ("top" returns all qualified players). Defaults to "top".
        return_pandas (bool, optional): Whether or not to return the data as a Pandas DataFrame or not. Defaults to False (Polars DataFrame will be returned).

    Raises:
        ValueError: If start_year or end_year are None
        ValueError: If start_year or end_year are before 2016
        ValueError: If start_year is after end_year
        ValueError: If perspective is not one of 'Fld', 'Pit', 'Pitching+Team'
        ValueError: If min_oppurtunities is an int and less than 1
        ValueError: If min_oppurtunities is a string and not 'top'

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame containing the arm value leaderboard data
    """
    if start_year is None or end_year is None:
        raise ValueError("start_year and end_year must be provided")
    if start_year < 2016 or end_year < 2016:
        raise ValueError(
            "Dates must be after 2016 as arm value data is only available from 2016 onwards"
        )
    if start_year > end_year:
        raise ValueError("start_year must be before end_year")
    if perspective not in [
        "Fld",
        "Pit",
        "Pitching+Team",
    ]:
        raise ValueError("perspective must be one of 'Fld', 'Pit' or 'Pitching+Team'")
    if type(min_oppurtunities) is int:
        if min_oppurtunities < 1:
            raise ValueError("min_oppurtunities must be at least 1")
    elif type(min_oppurtunities) is str:
        if min_oppurtunities != "top":
            raise ValueError(
                "if min_oppurtunities is a string, it must be 'top', representing qualified players"
            )
    df = pl.read_csv(
        requests.get(
            ARM_VALUE_URL.format(
                end_season=end_year,
                start_season=start_year,
                split_years="yes" if split_years else "no",
                perspective=perspective,
                min_oppurtunities=min_oppurtunities,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


CATCHER_BLOCKING_URL = "https://baseballsavant.mlb.com/leaderboard/catcher-blocking?game_type=All&n={min_pitches}&season_end={end_season}&season_start={start_season}&split={split_years}&team=&type={perspective}&with_team_only=1&sortColumn=diff_runner_pbwp&sortDirection=desc&players=&selected_idx=0&csv=true"


def statcast_catcher_blocking_leaderboard(
    start_year: int,
    end_year: int,
    min_pitches: str | int = "q",
    split_years: bool = False,
    perspective: str = "Cat",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves catcher blocking leaderboard data from Baseball Savant

    Args:
        start_year (int): First year to retrieve data from
        end_year (int): Last year to retrieve data from
        min_pitches (str | int, optional): Minimum number of pitches to be included in the data ("q" returns all qualified players). Defaults to "q".
        split_years (bool, optional): Whether or not to split the data by year. Defaults to False.
        perspective (str, optional): What perspective to return data from. Options are: 'Cat' (data for catchers), 'League' (league-wide data), 'Pit' (data for defenders while pitchers are pitching) or 'Pitching+Team' (team arm values on defense). Defaults to "Cat".
        return_pandas (bool, optional): Whether or not to return the data as a Pandas DataFrame or not. Defaults to False (Polars DataFrame will be returned).

    Raises:
        ValueError: If start_year or end_year are None
        ValueError: If start_year or end_year are before 2018
        ValueError: If start_year is after end_year
        ValueError: If perspective is not one of 'Cat', 'League', 'Pit', 'Pitching+Team'
        ValueError: If min_pitches is an int and less than 1
        ValueError: If min_pitches is a string and not 'q'

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame containing the catcher blocking leaderboard data
    """
    if start_year is None or end_year is None:
        raise ValueError("start_year and end_year must be provided")
    if start_year < 2018 or end_year < 2018:
        raise ValueError(
            "Dates must be after 2018 as catcher blocking data is only available from 2018 onwards"
        )
    if start_year > end_year:
        raise ValueError("start_year must be before end_year")
    if type(min_pitches) is int:
        if min_pitches < 1:
            raise ValueError("min_pitches must be at least 1")
    elif type(min_pitches) is str:
        if min_pitches != "q":
            raise ValueError("if min_pitches is a string, it must be 'q' for qualified")
    if perspective not in ["Cat", "League", "Pit", "Pitching+Team"]:
        raise ValueError(
            "perspective must be one of 'Cat', 'League', 'Pit', or 'Pitching+Team'"
        )
    df = pl.read_csv(
        requests.get(
            CATCHER_BLOCKING_URL.format(
                min_pitches=min_pitches,
                end_season=end_year,
                start_season=start_year,
                split_years="yes" if split_years else "no",
                perspective=perspective,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


CATCHER_FRAMING_URL = "https://baseballsavant.mlb.com/catcher_framing?year={year}&team=&min={min_pitches_called}&type={perspective}&sort=4%2C1&csv=true"


def statcast_catcher_framing_leaderboard(
    year: int,
    min_pitches_called: int | str = "q",
    perspective: str = "catcher",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves catcher framing leaderboard data from Baseball Savant

    Args:
        year (int): Year to retrieve data from (2015-2025) or 0 for all years
        min_pitches (int | str, optional): Minimum number of pitches to be included in the data ("q" returns all qualified players). Defaults to "q".
        perspective (str, optional): What perspective to return data from. Options are: 'catcher', 'pitcher', 'batter', 'fielding_team', 'batting_team'. Defaults to "catcher".
        return_pandas (bool, optional): Whether or not to return the data as a Pandas DataFrame or not. Defaults to False (Polars DataFrame will be returned).

    Raises:
        ValueError: if year is None
        ValueError: if year is before 2015 or after 2025 or not equal to 0
        ValueError: if min_pitches is an int and less than 1
        ValueError: if min_pitches is a string and not 'q'
        ValueError: if perspective is not one of 'catcher', 'pitcher', 'batter', 'fielding_team', 'batting_team'

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame containing the catcher framing leaderboard data
    """
    if year is None:
        raise ValueError("year must be provided")
    if (year < 2015 and year != 0) or (year > 2025):
        raise ValueError(
            "Dates must be between 2015 and 2025 as catcher framing data is only available from 2015 onwards"
        )
    if type(min_pitches_called) is int:
        if min_pitches_called < 1:
            raise ValueError("min_pitches must be at least 1")
    elif type(min_pitches_called) is str:
        if min_pitches_called != "q":
            raise ValueError("if min_pitches is a string, it must be 'q' for qualified")
    if perspective not in [
        "catcher",
        "pitcher",
        "batter",
        "fielding_team",
        "batting_team",
    ]:
        raise ValueError(
            "perspective must be one of 'catcher', 'pitcher', 'batter', 'fielding_team', or 'batting_team'"
        )
    df = pl.read_csv(
        requests.get(
            CATCHER_FRAMING_URL.format(
                year=year,
                min_pitches_called=min_pitches_called,
                perspective=perspective,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


CATCHER_POPTIME_URL = "https://baseballsavant.mlb.com/leaderboard/poptime?year={year}&team=&min2b={min_2b_attempts}&min3b={min_3b_attempts}&csv=true"


def statcast_catcher_poptime_leaderboard(
    year: int,
    min_2b_attempts: int = 5,
    min_3b_attempts: int = 0,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves catcher pop time leaderboard data from Baseball Savant

    Args:
        year (int): Year to retrieve data from
        min_2b_attempts (int, optional): Minimum number of 2B attempts to be included in the data. Defaults to 5.
        min_3b_attempts (int, optional): Minimum number of 3B attempts to be included in the data. Defaults to 0.
        return_pandas (bool, optional): Whether or not to return the data as a Pandas DataFrame or not. Defaults to False (Polars DataFrame will be returned).

    Raises:
        ValueError: If year is None
        ValueError: If year is before 2015
        ValueError: If min_2b_attempts is less than 0
        ValueError: If min_3b_attempts is less than 0

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame containing the catcher pop time leaderboard data
    """
    if year is None:
        raise ValueError("year must be provided")
    if year < 2015:
        raise ValueError(
            "Dates must be after 2015 as catcher pop time data is only available from 2015 onwards"
        )
    if min_2b_attempts < 0:
        raise ValueError("min_2b_attempts must be at least 0")
    if min_3b_attempts < 0:
        raise ValueError("min_3b_attempts must be at least 0")
    df = pl.read_csv(
        requests.get(
            CATCHER_POPTIME_URL.format(
                year=year,
                min_2b_attempts=min_2b_attempts,
                min_3b_attempts=min_3b_attempts,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


OUTFIELD_CATCH_PROB_URL = "https://baseballsavant.mlb.com/leaderboard/catch_probability?type=player&min={min_oppurtunities}&year={year}&total=5&sort=2&sortDir=desc&csv=true"


def statcast_outfield_catch_probability_leaderboard(
    year: str | int = None,
    min_opportunities: int | str = "q",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if year is None:
        raise ValueError("year must be provided")
    if type(year) is int:
        if year < 2016:
            raise ValueError(
                "Dates must be after 2016 as outfield catch probability data is only available from 2016 onwards"
            )
    elif type(year) is str:
        if year != "ALL":
            raise ValueError("if year is a string, it must be 'ALL'")
    if type(min_opportunities) is int:
        if min_opportunities < 1:
            raise ValueError("min_oppurtunities must be at least 1")
    elif type(min_opportunities) is str:
        if min_opportunities != "q":
            raise ValueError(
                "if min_oppurtunities is a string, it must be 'q' for qualified"
            )
    df = pl.read_csv(
        requests.get(
            OUTFIELD_CATCH_PROB_URL.format(
                year=year,
                min_oppurtunities=min_opportunities,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


OOA_URL = "https://baseballsavant.mlb.com/leaderboard/outs_above_average?type={perspective}&startYear={start_year}&endYear={end_year}&split={split_years}&team=&range=year&min={min_attempts}&pos=&roles=&viz=hide&csv=true"


def statcast_outsaboveaverage_leaderboard(
    start_year: int,
    end_year: int,
    perspective: str = "Fielder",
    split_years: bool = False,
    min_opportunities: int | str = "q",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves outs above average leaderboard data from Baseball Savant

    Args:
        start_year (int): First year to retrieve data from
        end_year (int): Last year to retrieve data from
        perspective (str, optional): What perspective to return data from. Options are: 'Fielder', 'Pitcher', 'Batter', 'Batting_Team', 'Fielding_Team'. Defaults to "Fielder".
        split_years (bool, optional): Whether or not to split the data by year. Defaults to False.
        min_opportunities (int | str, optional): Minimum number of oppurtunities to be included in the data ("q" returns all qualified players). Defaults to "q".
        return_pandas (bool, optional): Whether or not to return the data as a Pandas DataFrame or not. Defaults to False (Polars DataFrame will be returned).

    Raises:
        ValueError: If start_year or end_year are None
        ValueError: If start_year or end_year are before 2016
        ValueError: If start_year is after end_year
        ValueError: If perspective is not one of 'Fielder', 'Pitcher', 'Batter', 'Batting_Team', 'Fielding_Team'
        ValueError: If min_opportunities is an int and less than 1
        ValueError: If min_opportunities is a string and not 'q'

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame containing the outs above average leaderboard data
    """
    if start_year is None or end_year is None:
        raise ValueError("start_year and end_year must be provided")
    if start_year < 2016 or end_year < 2016:
        raise ValueError(
            "Dates must be after 2016 as outs above average data is only available from 2016 onwards"
        )
    if end_year < start_year:
        raise ValueError("start_year must be before end_year")
    if perspective not in [
        "Fielder",
        "Pitcher",
        "Batter",
        "Batting_Team",
        "Fielding_Team",
    ]:
        raise ValueError(
            "perspective must be one of 'Fielder', 'Pitcher', 'Batter', 'Batting_Team', or 'Fielding_Team'"
        )
    if type(min_opportunities) is int:
        if min_opportunities < 1:
            raise ValueError("min_opportunities must be at least 1")
    elif type(min_opportunities) is str:
        if min_opportunities != "q":
            raise ValueError(
                "if min_opportunities is a string, it must be 'q' for qualified"
            )
    df = pl.read_csv(
        requests.get(
            OOA_URL.format(
                perspective=perspective,
                start_year=start_year,
                end_year=end_year,
                split_years="yes" if split_years else "no",
                min_attempts=min_opportunities,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


BASERUNNING_RV_URL = "https://baseballsavant.mlb.com/leaderboard/baserunning-run-value?game_type=All&season_start={start_year}&season_end={end_year}&sortColumn=runner_runs_XB_swipe&sortDirection=desc&split={split_years}&n={min_oppurtunities}&team=&type={perspective}&with_team_only=1&csv=true"


def statcast_baserunning_run_value_leaderboard(
    start_year: int,
    end_year: int,
    perspective: str = "Run",
    split_years: bool = False,
    min_oppurtunities: int | str = "q",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves baserunning run value leaderboard data from Baseball Savant

    Args:
        start_year (int): First year to retrieve data from
        end_year (int): Last year to retrieve data from
        perspective (str, optional): What perspective to return data from. Options are: 'Run', 'League', 'Batting+Team', 'Pitching+Team'. Defaults to "Run".
        split_years (bool, optional): Whether or not to split the data by year. Defaults to False.
        min_oppurtunities (int | str, optional): Minimum number of oppurtunities to be included in the data ("q" returns all qualified players). Defaults to "q".
        return_pandas (bool, optional): Whether or not to return the data as a Pandas DataFrame or not. Defaults to False (Polars DataFrame will be returned).

    Raises:
        ValueError: If start_year or end_year are None
        ValueError: If start_year or end_year are before 2016
        ValueError: If start_year is after end_year
        ValueError: If perspective is not one of 'Run', 'League', 'Batting+Team', 'Pitching+Team'
        ValueError: If min_oppurtunities is an int and less than 1
        ValueError: If min_oppurtunities is a string and not 'q'

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame containing the baserunning run value leaderboard data
    """
    if start_year is None or end_year is None:
        raise ValueError("start_year and end_year must be provided")
    if start_year < 2016 or end_year < 2016:
        raise ValueError(
            "Dates must be after 2016 as baserunning run value data is only available from 2016 onwards"
        )
    if start_year > end_year:
        raise ValueError("start_year must be before end_year")
    if perspective not in ["Run", "League", "Batting+Team", "Pitching+Team"]:
        raise ValueError(
            "perspective must be one of 'Run', 'League', 'Batting+Team', or 'Pitching+Team'"
        )
    if type(min_oppurtunities) is int:
        if min_oppurtunities < 1:
            raise ValueError("min_oppurtunities must be at least 1")
    elif type(min_oppurtunities) is str:
        if min_oppurtunities != "q":
            raise ValueError(
                "if min_oppurtunities is a string, it must be 'q' for qualified"
            )
    df = pl.read_csv(
        requests.get(
            BASERUNNING_RV_URL.format(
                start_year=start_year,
                end_year=end_year,
                perspective=perspective,
                split_years="yes" if split_years else "no",
                min_oppurtunities=min_oppurtunities,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


BASESTEALING_RUN_VALUE_URL = "https://baseballsavant.mlb.com/leaderboard/basestealing-run-value?game_type=All&n={min_sb_oppurtunities}&pitch_hand={pitch_hand}&runner_moved={runner_movement}&target_base={target_base}&prior_pk=All&season_end={end_year}&season_start={start_year}&sortColumn=simple_stolen_on_running_act&sortDirection=desc&split={split_years}&team=&type={perspective}&with_team_only=1&expanded=0&csv=true"


def statcast_basestealing_runvalue_leaderboard(
    start_year: int,
    end_year: int,
    min_sb_oppurtunities: int | str = "q",
    pitch_hand: str = "All",
    runner_movement: str = "All",
    target_base: str = "All",
    split_years: bool = False,
    perspective: str = "Bat",
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Retrieves basestealing run value leaderboard data from Baseball Savant

    Args:
        start_year (int): First year to retrieve data from
        end_year (int): Last year to retrieve data from
        min_sb_oppurtunities (int | str, optional): Minimum number of oppurtunities to be included in the data ("q" returns all qualified players). Defaults to "q".
        pitch_hand (str, optional): Hand of the pitcher to filter by. Options are: 'All', 'R', 'L'. Defaults to "All".
        runner_movement (str, optional): Movement of the runner to filter by. Options are: 'All', 'Advance', 'Out', 'Hold'. Defaults to "All".
        target_base (str, optional): Target base to filter by. Options are: 'All', '2B', '3B'. Defaults to "All".
        split_years (bool, optional): Whether or not to split the data by year. Defaults to False.
        perspective (str, optional): What perspective to return data from. Options are: 'Run', 'League', 'Batting+Team'. Defaults to "Run".
        return_pandas (bool, optional): Whether or not to return the data as a Pandas DataFrame or not. Defaults to False (Polars DataFrame will be returned).

    Raises:
        ValueError: If start_year or end_year are None
        ValueError: If start_year or end_year are before 2016
        ValueError: If start_year is after end_year
        ValueError: If min_sb_oppurtunities is an int and less than 1
        ValueError: If min_sb_oppurtunities is a string and not 'q'
        ValueError: If pitch_hand is not one of 'All', 'R', 'L'
        ValueError: If runner_movement is not one of 'All', 'Advance', 'Out', 'Hold'
        ValueError: If target_base is not one of 'All', '2B', '3B'
        ValueError: If perspective is not one of 'Run', 'League', 'Batting+Team'

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame containing the basestealing run value leaderboard data
    """
    if start_year is None or end_year is None:
        raise ValueError("start_year and end_year must be provided")
    if start_year < 2016 or end_year < 2016:
        raise ValueError(
            "Dates must be after 2016 as basestealing run value data is only available from 2016 onwards"
        )
    if start_year > end_year:
        raise ValueError("start_year must be before end_year")
    if type(min_sb_oppurtunities) is int:
        if min_sb_oppurtunities < 1:
            raise ValueError("min_sb_oppurtunities must be at least 1")
    elif type(min_sb_oppurtunities) is str:
        if min_sb_oppurtunities != "q":
            raise ValueError(
                "if min_sb_oppurtunities is a string, it must be 'q' for qualified"
            )
    if pitch_hand not in ["All", "R", "L"]:
        raise ValueError("pitch_hand must be one of 'All', 'R', or 'L'")
    if runner_movement not in ["All", "Advance", "Out", "Hold"]:
        raise ValueError(
            "runner_movement must be one of 'All', 'Advance', 'Out', or 'Hold'"
        )
    if target_base not in ["All", "2B", "3B"]:
        raise ValueError("target_base must be one of 'All', '2B', or '3B'")
    if perspective not in [
        "Bat",
        "Batting+Team",
        "League",
    ]:
        raise ValueError(
            "perspective must be one of 'Bat', 'Batting+Team', or 'League'"
        )
    df = pl.read_csv(
        requests.get(
            BASESTEALING_RUN_VALUE_URL.format(
                min_sb_oppurtunities=min_sb_oppurtunities,
                pitch_hand=pitch_hand,
                end_year=end_year,
                start_year=start_year,
                split_years="yes" if split_years else "no",
                perspective=perspective,
                target_base=target_base,
                runner_movement=runner_movement,
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


PARK_FACTORS_BY_YEAR_LEADERBOARD_URL = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year={year}&batSide={bat_side}&condition={condition}&rolling={rolling_years}&parks=mlb"


def statcast_park_factors_leaderboard_by_years(
    year: int,
    bat_side: Literal["L", "R", ""] = "",
    condition: Literal["All", "Day", "Night", "Roof Closed", "Open Air"] = "All",
    rolling_years: int = 3,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    if year is None:
        raise ValueError("year must be provided")
    if year < 1999:
        raise ValueError("year must be after 1999")
    if bat_side not in ["L", "R", ""]:
        raise ValueError("bat_side must be one of 'L', 'R', or ''")
    if condition not in ["All", "Day", "Night", "Roof Closed", "Open Air"]:
        raise ValueError(
            "condition must be one of 'All', 'Day', 'Night', 'Roof Closed', 'Open Air'"
        )
    if rolling_years < 1 or rolling_years > 3:
        raise ValueError("rolling_years must be between 1 and 3")

    resp = requests.get(
        PARK_FACTORS_BY_YEAR_LEADERBOARD_URL.format(
            year=year,
            bat_side=bat_side,
            condition=condition,
            rolling_years=rolling_years,
        )
    )
    soup = BeautifulSoup(resp.content, "html.parser")
    data_thing = soup.select_one(
        "#leaderboard_statcast-park-factors > div.article-template > script"
    )
    data_string = data_thing.text.split("\n")[1]
    further = data_string.split("[")[1]
    further = further.split("]")[0]
    data = json.loads(f"[{further}]")
    df = pl.DataFrame(data)
    df = df.drop(
        [
            "grouping_venue_conditions",
            "key_is_year_rolling",
            "key_num_years_rolling",
            "key_year",
            "key_bat_side",
            "venue_id",
            "main_team_id",
        ]
    )
    df = df.rename(
        {
            "venue_name": "stadium_name",
            "name_display_club": "team_name",
        }
    )
    df = df.with_columns(
        pl.exclude(["stadium_name", "team_name", "year_range"]).cast(pl.Int32)
    )
    cols = df.columns
    cols.insert(2, cols.pop(cols.index("year_range")))
    df = df.select(cols)
    return df if not return_pandas else df.to_pandas()


PARK_FACTORS_DISTANCE_LEADERBOARD_URL = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=distance&year={year}&batSide=&stat=index_wOBA&condition=All&rolling=3&parks=mlb&csv=true"


def statcast_park_factors_leaderboard_distance(
    year: int, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    if year is None:
        raise ValueError("year must be provided")
    if year > 2024 or year < 2016:
        raise ValueError("year must be between 2016 and 2024")

    resp = requests.get(
        PARK_FACTORS_DISTANCE_LEADERBOARD_URL.format(
            year=year,
        )
    )

    soup = BeautifulSoup(resp.content, "html.parser")
    data = soup.select_one(
        "#leaderboard_statcast-park-factors > div.article-template > script"
    )
    data = data.text.split("\n")[1]
    data = data.split("[")[1]
    data = data.split("]")[0]
    data = json.loads(f"[{data}]")

    df = pl.DataFrame(data)
    df = df.with_columns(
        pl.col(
            [
                "year",
                "venue_id",
                "main_team_id",
                "elevation_feet",
                "n",
                "avg_roof",
                "avg_daytime",
                "n_year_venue_roof_for_cool_hot_code",
            ]
        ).cast(pl.Int32),
        pl.col(
            [
                "avg_temperature",
                "extra_distance",
                "temperature_extra_distance",
                "elevation_extra_distance",
                "roof_extra_distance",
                "environment_extra_distance",
                "avg_temp_cool",
                "extra_distance_cool",
                "avg_temp_warm",
                "extra_distance_warm",
                "avg_temp_hot",
                "extra_distance_hot",
            ]
        ),
    )
    return df if not return_pandas else df.to_pandas()
