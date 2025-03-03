import pandas as pd
import polars as pl
import requests

from pybaseballstats.utils.statcast_utils import _handle_dates

BAT_TRACKING_URL = "https://baseballsavant.mlb.com/leaderboard/bat-tracking?attackZone=&batSide=&contactType=&count=&dateStart={start_dt}&dateEnd={end_dt}&gameType=&groupBy=&isHardHit=&minSwings={min_swings}&minGroupSwings=1&pitchHand=&pitchType=&seasonStart=&seasonEnd=&team=&type={perspective}&csv=true"


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
