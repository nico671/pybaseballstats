import asyncio
from typing import List

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
