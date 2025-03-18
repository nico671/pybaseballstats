import asyncio
from datetime import datetime
from typing import List, Literal, Optional, Tuple, Union

import aiohttp
import pandas as pd
import polars as pl
import polars.selectors as cs
from bs4 import BeautifulSoup
from tqdm import tqdm

from pybaseballstats.utils.consts import (
    FANGRAPHS_BATTING_URL,
    FANGRAPHS_FIELDING_URL,
    FANGRAPHS_PITCHING_URL,
    FangraphsBattingPosTypes,
    FangraphsBattingStatType,
    FangraphsFieldingStatType,
    FangraphsLeagueTypes,
    FangraphsPitchingStatType,
    FangraphsStatSplitTypes,
    FangraphsTeams,
)
from pybaseballstats.utils.statcast_utils import _handle_dates

FANGRAPHS_BATTING_API_URL = "https://www.fangraphs.com/api/leaders/major-league/data?age={age_range}&pos={pos}&stats=bat&lg={league}&qual={min_pa}&season={end_season}&season1={start_season}&startdate={start_date}&enddate={end_date}&month=0&hand={batting_hand}&team={team}&pageitems=2000000000&pagenum=1&ind=0&rost={active_roster_only}&players=0&postseason=&sort=21,d"


def fangraphs_validate_dates(
    start_date: str, end_date: str
) -> Tuple[datetime.date, datetime.date]:
    """Validate and convert date strings (YYYY-MM-DD) to datetime.date objects."""
    date_format = "%Y-%m-%d"

    try:
        start_dt = datetime.strptime(start_date, date_format).date()
        end_dt = datetime.strptime(end_date, date_format).date()
    except ValueError:
        raise ValueError(
            f"Dates must be in YYYY-MM-DD format. Got start_date='{start_date}', end_date='{end_date}'"
        )

    if start_dt > end_dt:
        raise ValueError(
            f"start_date ({start_dt}) cannot be after end_date ({end_dt})."
        )

    return start_dt, end_dt


def fangraphs_batting_input_val(
    start_date: Union[str, None] = None,
    end_date: Union[str, None] = None,
    start_season: Union[int, None] = None,
    end_season: Union[int, None] = None,
    min_pa: Union[str, int] = "q",
    stat_types: List[FangraphsBattingStatType] = None,
    fielding_position: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    active_roster_only: bool = False,
    team: FangraphsTeams = FangraphsTeams.ALL,
    league: Literal["nl", "al", ""] = "",
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    batting_hand: Literal["R", "L", "S", ""] = "",
    stat_split: Literal["", "ts", "ss"] = "",
):
    # start_date, end_date, start_season, end_season validation
    # Ensure that either (start_date & end_date) OR (start_season & end_season) are provided
    if (start_date and end_date) and (start_season and end_season):
        raise ValueError(
            "Specify either (start_date, end_date) OR (start_season, end_season), but not both."
        )

    if not (start_date and end_date) and not (start_season and end_season):
        raise ValueError(
            "You must provide either (start_date, end_date) OR (start_season, end_season)."
        )

    # Validate and convert dates if provided
    if start_date and end_date:
        start_date, end_date = fangraphs_validate_dates(start_date, end_date)
        start_season = None
        end_season = None
        print(f"Using date range: {start_date} to {end_date}")

    # Validate seasons if provided
    if start_season and end_season:
        if start_season > end_season:
            raise ValueError(
                f"start_season ({start_season}) cannot be after end_season ({end_season})."
            )
        print(f"Using season range: {start_season} to {end_season}")
        start_date = None
        end_date = None

    # min_pa validation
    if isinstance(min_pa, str):
        if min_pa not in ["q"]:
            raise ValueError("If min_pa is a string, it must be 'q' (qualified).")
    elif isinstance(min_pa, int):
        if min_pa < 0:
            raise ValueError("min_pa must be a positive integer.")
    else:
        raise ValueError("min_pa must be a string or integer.")

    # fielding_position validation
    if not isinstance(fielding_position, FangraphsBattingPosTypes):
        raise ValueError(
            "fielding_position must be a valid FangraphsBattingPosTypes value"
        )

    # active_roster_only validation
    if not isinstance(active_roster_only, bool):
        raise ValueError("active_roster_only must be a boolean value.")
    if active_roster_only:
        print("Only active roster players will be included.")
        active_roster_only = 1
    else:
        print("All players will be included.")
        active_roster_only = 0

    # team validation
    if not isinstance(team, FangraphsTeams):
        raise ValueError("team must be a valid FangraphsTeams value")
    print(f"Filtering by team: {team}")

    # league validation
    if league not in ["nl", "al", ""]:
        raise ValueError("league must be 'nl', 'al', or an empty string.")
    if league:
        print(f"Filtering by league: {league}")

    if (min_age is not None and max_age is None) or (
        min_age is None and max_age is not None
    ):
        raise ValueError("Both min_age and max_age must be provided or neither")

    if min_age is not None and max_age is not None:
        if min_age > max_age:
            raise ValueError(
                f"min_age ({min_age}) cannot be greater than max_age ({max_age})"
            )

        age_range_str = f"{min_age}%2C{max_age}"
        print(f"Filtering by age range: {min_age} to {max_age}")
    else:
        age_range_str = ""

    # batting_hand validation
    if batting_hand not in ["R", "L", "S", ""]:
        raise ValueError("batting_hand must be 'R', 'L', 'S', or an empty string.")

    # stat_split validation
    if stat_split not in ["", "ts", "ss"]:
        raise ValueError("stat_split must be '', 'ts', or 'ss'.")
    if stat_split:
        print(f"Using stat split: {stat_split}")
        if stat_split == "ts" or stat_split == "ss":
            if team != FangraphsTeams.ALL:
                print(
                    "Stat splits are only available for all teams. Ignoring stat_split."
                )
            else:
                team = f"{team.value}%2C{stat_split}"
    stat_cols = set()
    # stat_types validation
    if stat_types is None:
        for stat_type in FangraphsBattingStatType:
            for stat in stat_type.value:
                stat_cols.add(stat)
    else:
        for stat_type in stat_types:
            for stat in stat_type.value:
                stat_cols.add(stat)
    stat_types = list(stat_cols)
    return (
        start_date,
        end_date,
        start_season,
        end_season,
        min_pa,
        fielding_position,
        active_roster_only,
        team,
        league,
        age_range_str,
        batting_hand,
        stat_types,
    )


def gen_input_val(
    start_date: str = None,
    end_date: str = None,
    start_season: str = None,
    end_season: str = None,
    rost: int = 0,
    team: FangraphsTeams = FangraphsTeams.ALL,
    stat_split: FangraphsStatSplitTypes = FangraphsStatSplitTypes.PLAYER,
):
    # input validation
    if (start_date is None or end_date is None) and (
        start_season is None or end_season is None
    ):
        raise ValueError(
            "Either start_date and end_date must not be None or start_season and end_season must not be None"
        )

    elif (start_date is not None and end_date is None) or (
        start_date is None and end_date is not None
    ):
        raise ValueError(
            "Both start_date and end_date must be provided if one is provided"
        )

    elif (start_season is not None and end_season is None) or (
        start_season is None and end_season is not None
    ):
        raise ValueError(
            "Both start_season and end_season must be provided if one is provided"
        )
    if rost not in [0, 1]:
        raise ValueError("rost must be either 0 (all players) or 1 (active roster)")

    if stat_split.value != "":
        team = f"{team},{stat_split.value}"
    else:
        team = f"{team.value}"
    # convert start_date and end_date to datetime objects
    if start_date is not None and end_date is not None:
        start_date, end_date = _handle_dates(start_date, end_date)
    return start_date, end_date, start_season, end_season, team


def _construct_url(
    pos: str,
    league: str,
    qual: str,
    stat_type: int,
    start_date: str,
    end_date: str,
    start_season: str,
    end_season: str,
    handedness: str,
    rost: int,
    team: str,
    pitch_bat_fld: str,  # Add this parameter
    starter_reliever: str = "",
) -> str:
    """
    Constructs the URL from common parameters.
    For batting ('bat'), appends &handedness and &age.
    For pitching ('pitch'), uses the pitching URL; adjust as needed for fielding.
    """
    params = {
        "pos": pos,
        "league": league,
        "qual": qual,
        "stat_type": stat_type,
        "start_date": start_date if start_date is not None else "",
        "end_date": end_date if end_date is not None else "",
        "start_season": start_season if start_season is not None else "",
        "end_season": end_season if end_season is not None else "",
        "rost": rost,
        "team": team,
    }
    if pitch_bat_fld == "pit":
        url_template = FANGRAPHS_PITCHING_URL
        params["starter_reliever"] = starter_reliever
        params["handedness"] = handedness
    elif pitch_bat_fld == "bat":
        url_template = FANGRAPHS_BATTING_URL
        params["handedness"] = handedness
    elif pitch_bat_fld == "fld":
        url_template = FANGRAPHS_FIELDING_URL
    else:
        raise ValueError(
            "Unsupported category for pitch_bat_fld, use 'bat' or 'pit' or 'fld'."
        )
    print(url_template.format(**params))
    return url_template.format(**params)


async def _get_fangraphs_stats_async(
    start_date: str = None,
    end_date: str = None,
    start_season: str = None,
    end_season: str = None,
    stat_types: dict = None,
    return_pandas: bool = False,
    league: FangraphsLeagueTypes = FangraphsLeagueTypes.ALL,
    team: str = "",
    qual: str = "y",
    rost: int = 0,
    pos: str = "",
    handedness: str = "",
    pitch_bat_fld: str = "",
    starter_reliever: str = "",
) -> pl.DataFrame | pd.DataFrame:
    """Generic async function to fetch Fangraphs statistics."""
    if qual != "y":
        print("Warning: using a custom minimum value may result in missing data")

    async with aiohttp.ClientSession() as session:
        tasks = [
            get_table_data_async(
                session,
                stat_type=stat_types[stat],
                league=league,
                start_date=start_date,
                end_date=end_date,
                qual=qual,
                start_season=start_season,
                end_season=end_season,
                handedness=handedness,
                rost=rost,
                team=team,
                pos=pos,
                pitch_bat_fld=pitch_bat_fld,
                starter_reliever=starter_reliever,
            )
            for stat in stat_types
        ]
        df_list = [
            await t
            for t in tqdm(
                asyncio.as_completed(tasks), total=len(tasks), desc="Fetching data"
            )
        ]

    df = df_list[0]
    for next_df in df_list[1:]:
        df = df.join(next_df, on="Name", how="full").select(~cs.ends_with("_right"))

    return df.to_pandas() if return_pandas else df


async def fangraphs_batting_range_async(
    start_date: str = None,
    end_date: str = None,
    start_season: str = None,
    end_season: str = None,
    stat_types: List[FangraphsBattingStatType] = None,
    return_pandas: bool = False,
    pos: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    league: FangraphsLeagueTypes = FangraphsLeagueTypes.ALL,
    qual: str = "y",
    rost: int = 0,
    team: str = "",
    handedness: str = "",
) -> pl.DataFrame | pd.DataFrame:
    if stat_types is None:
        stat_types = {stat: stat.value for stat in list(FangraphsBattingStatType)}
    elif len(stat_types) == 0:
        raise ValueError("stat_types must not be an empty list")
    else:
        stat_types = {stat: stat.value for stat in stat_types}

    return await _get_fangraphs_stats_async(
        start_date=start_date,
        end_date=end_date,
        start_season=start_season,
        end_season=end_season,
        stat_types=stat_types,
        return_pandas=return_pandas,
        league=league,
        team=team,
        qual=qual,
        rost=rost,
        pos=pos.value,
        handedness=handedness,
        pitch_bat_fld="bat",
    )


async def fangraphs_pitching_range_async(
    start_date: str = None,
    end_date: str = None,
    start_season: str = None,
    end_season: str = None,
    stat_types: List[FangraphsPitchingStatType] = None,
    starter_reliever: str = "pit",
    return_pandas: bool = False,
    league: FangraphsLeagueTypes = FangraphsLeagueTypes.ALL,
    team: str = "",
    qual: str = "y",
    rost: int = 0,
    handedness: str = "",
) -> pl.DataFrame | pd.DataFrame:
    if stat_types is None:
        stat_types = {stat: stat.value for stat in list(FangraphsPitchingStatType)}
    elif len(stat_types) == 0:
        raise ValueError("stat_types must not be an empty list")
    else:
        stat_types = {stat: stat.value for stat in stat_types}

    return await _get_fangraphs_stats_async(
        start_date=start_date,
        end_date=end_date,
        start_season=start_season,
        end_season=end_season,
        stat_types=stat_types,
        return_pandas=return_pandas,
        league=league,
        team=team,
        qual=qual,
        rost=rost,
        handedness=handedness,
        pitch_bat_fld="pit",
        starter_reliever=starter_reliever,
    )


async def fangraphs_fielding_range_async(
    start_date: str = None,
    end_date: str = None,
    start_season: str = None,
    end_season: str = None,
    stat_types: List[FangraphsFieldingStatType] = None,
    return_pandas: bool = False,
    league: FangraphsLeagueTypes = FangraphsLeagueTypes.ALL,
    team: str = "",
    qual: str = "y",
    rost: int = 0,
    pos: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
) -> pl.DataFrame | pd.DataFrame:
    if stat_types is None:
        stat_types = {stat: stat.value for stat in list(FangraphsFieldingStatType)}
    elif len(stat_types) == 0:
        raise ValueError("stat_types must not be an empty list")
    else:
        stat_types = {stat: stat.value for stat in stat_types}

    return await _get_fangraphs_stats_async(
        start_date=start_date,
        end_date=end_date,
        start_season=start_season,
        end_season=end_season,
        stat_types=stat_types,
        return_pandas=return_pandas,
        league=league,
        team=team,
        qual=qual,
        rost=rost,
        pos=pos.value,
        pitch_bat_fld="fld",
    )


async def get_table_data_async(
    session,
    stat_type,
    league: FangraphsLeagueTypes = FangraphsLeagueTypes.ALL,
    start_date: str = "",
    end_date: str = "",
    qual: str = "y",
    start_season: str = None,
    end_season: str = None,
    handedness: str = "",
    rost: int = 0,
    team: str = "",
    pos: str = "",
    pitch_bat_fld: str = "",
    starter_reliever: str = "",
):
    # Use _construct_url to build the appropriate URL.
    url = _construct_url(
        pos=pos,
        league=league,
        qual=qual,
        stat_type=stat_type,
        start_date=start_date,
        end_date=end_date,
        start_season=start_season,
        end_season=end_season,
        handedness=handedness,
        rost=rost,
        team=team,
        starter_reliever=starter_reliever,
        pitch_bat_fld=pitch_bat_fld,
    )
    try:
        async with session.get(url) as response:
            cont = await response.text()
    except aiohttp.ClientOSError as e:
        print(f"ClientOSError: {e}")
        return pl.DataFrame()
    except aiohttp.ClientPayloadError as e:
        print(f"ClientPayloadError: {e}")
        return pl.DataFrame()
    except aiohttp.ClientResponseError as e:
        print(f"ClientResponseError: {e}")
        return pl.DataFrame()
    except Exception as e:
        print(f"Exception: {e}")
        return pl.DataFrame()

    soup = BeautifulSoup(cont, "html.parser")
    main_table = soup.select_one(
        "#content > div.leaders-major_leaders-major__table__hcmbm > div.fg-data-grid.table-type > div.table-wrapper-outer > div > div.table-scroll > table"
    )
    thead = main_table.find("thead")
    headers = [
        th["data-col-id"]
        for th in thead.find_all("th")
        if "data-col-id" in th.attrs and th["data-col-id"] != "divider"
    ]
    tbody = main_table.find("tbody")
    data = []
    for row in tbody.find_all("tr"):
        row_data = {header: None for header in headers}
        for cell in row.find_all("td"):
            col_id = cell.get("data-col-id")
            if col_id and col_id != "divider":
                if cell.find("a"):
                    row_data[col_id] = cell.find("a").text
                elif cell.find("span"):
                    row_data[col_id] = cell.find("span").text
                else:
                    text = cell.text.strip().replace("%", "")
                    if text == "":
                        row_data[col_id] = None
                    else:
                        try:
                            row_data[col_id] = float(text) if "." in text else int(text)
                        except ValueError:
                            row_data[col_id] = text
        data.append(row_data)

    df = pl.DataFrame(data, infer_schema_length=None)
    return df
