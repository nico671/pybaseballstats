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
    start_dt, end_dt = _handle_dates(start_dt, end_dt)
    if start_dt.year < 2023 or end_dt.year < 2023:
        raise ValueError(
            "Dates must be after 2023 as bat tracking data is only available from 2023 onwards"
        )
    if start_dt > end_dt:
        raise ValueError("Start date must be before end date")
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
    if year < 2019:
        raise ValueError(
            "Dates must be after 2019 as pitch arsenal data is only available from 2019 onwards"
        )
    if pitcher_batter not in ["pitcher", "batter"]:
        raise ValueError("pitcher_batter must be either 'pitcher' or 'batter'")
    df = pl.read_csv(
        requests.get(
            PITCH_ARSENAL_URL.format(pitcher_batter="pitcher", year=year)
        ).content,
        truncate_ragged_lines=True,
    )
    return df if not return_pandas else df.to_pandas()


PITCHING_ACTIVE_SPIN_URL = "https://baseballsavant.mlb.com/leaderboard/active-spin?year={year}_spin-based&min=50&hand=&csv=true"


def statcast_pitching_active_spin(
    year: int, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    if year < 2017:
        raise ValueError(
            "Dates must be after 2017 as spin tracking data is only available from 2017 onwards"
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
    if start_dt is not None and end_dt is not None:
        start_dt, end_dt = _handle_dates(start_dt, end_dt)
        if season is not None:
            print(
                "WARNING: season parameter will be ignored as start_dt and end_dt are provided"
            )
            season = ""
    if start_dt.year < 2023 or end_dt.year < 2023:
        raise ValueError(
            "Dates must be after 2023 as arm angle data is only available from 2023 onwards"
        )
    if start_dt > end_dt:
        raise ValueError("Start date must be before end date")
    df = pl.read_csv(
        requests.get(
            PITCHING_ARM_ANGLE_URL.format(
                start_dt=start_dt, end_dt=end_dt, season=season
            )
        ).content
    )
    return df if not return_pandas else df.to_pandas()


ARM_STRENGTH_URL = "https://baseballsavant.mlb.com/leaderboard/arm-strength?type=player&year={year}&minThrows=50&pos=&team=&csv=true"


def statcast_arm_stats(
    year: int, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    if year < 2020:
        raise ValueError(
            "Dates must be after 2020 as arm strength data is only available from 2020 onwards"
        )
    df = pl.read_csv(
        requests.get(ARM_STRENGTH_URL.format(year=year)).content,
        truncate_ragged_lines=True,
    )
    return df if not return_pandas else df.to_pandas()
