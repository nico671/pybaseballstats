import asyncio
from enum import Enum
from typing import List

import aiohttp
import pandas as pd
import polars as pl
import polars.selectors as cs
from bs4 import BeautifulSoup
from tqdm import tqdm


class FangraphsTeams(Enum):
    ALL = 0
    ANGELS = 1
    ASTROS = 17
    ATHLETICS = 10
    BLUE_JAYS = 14
    BRAVES = 16
    BREWERS = 23
    CARDINALS = 28
    CUBS = 17
    DIAMONDBACKS = 15
    DODGERS = 22
    GIANTS = 30
    GUARDIANS = 5
    MARINERS = 11
    MARLINS = 20
    METS = 25
    NATIONALS = 24
    ORIOLES = 2
    PADRES = 29
    PHILLIES = 26
    PIRATES = 27
    RANGERS = 13
    RAYS = 12
    RED_SOX = 3
    REDS = 18
    ROCKIES = 19
    ROYALS = 7
    TIGERS = 6
    TWINS = 8
    WHITE_SOX = 4
    YANKEES = 9


class FangraphsStatSplitTypes(Enum):
    PLAYER = ""
    TEAM = "ts"
    LEAGUE = "ss"


class FangraphsBattingStatType(Enum):
    DASHBOARD = 8
    STANDARD = 0
    ADVANCED = 1
    BATTED_BALL = 2
    WIN_PROBABILITY = 3
    VALUE = 6
    PLUS_STATS = 23
    STATCAST = 24
    VIOLATIONS = 48
    SPORTS_INFO_PITCH_TYPE = 4
    SPORTS_INFO_PITCH_VALUE = 7
    SPORTS_INFO_PLATE_DISCIPLINE = 5
    STATCAST_PITCH_TYPE = 9
    STATCAST_VELO = 10
    STATCAST_H_MOVEMENT = 11
    STATCAST_V_MOVEMENT = 12
    STATCAST_PITCH_TYPE_VALUE = 13
    STATCAST_PITCH_TYPE_VALUE_PER_100 = 14
    STATCAST_PLATE_DISCIPLINE = 15
    PITCH_INFO_PITCH_TYPE = 16
    PITCH_INFO_PITCH_VELOCITY = 17
    PITCH_INFO_H_MOVEMENT = 18
    PITCH_INFO_V_MOVEMENT = 19
    PITCH_INFO_PITCH_TYPE_VALUE = 20
    PITCH_INFO_PITCH_TYPE_VALUE_PER_100 = 21
    PITCH_INFO_PLATE_DISCIPLINE = 22


class FangraphsBattingPosTypes(Enum):
    CATCHER = "c"
    FIRST_BASE = "1b"
    SECOND_BASE = "2b"
    THIRD_BASE = "3b"
    SHORTSTOP = "ss"
    LEFT_FIELD = "lf"
    CENTER_FIELD = "cf"
    RIGHT_FIELD = "rf"
    DESIGNATED_HITTER = "dh"
    OUTFIELD = "of"
    PITCHER = "p"
    NON_PITCHER = "np"
    ALL = "all"

    def __str__(self):
        return self.value


class FangraphsLeagueTypes(Enum):
    ALL = ""
    NATIONAL_LEAGUE = "nl"
    AMERICAN_LEAGUE = "al"

    def __str__(self):
        return self.value


async def fangraphs_batting_range_async(
    start_date: str = None,
    end_date: str = None,
    start_season: str = None,
    end_season: str = None,
    stat_types: List[FangraphsBattingStatType] = None,
    return_pandas: bool = False,
    pos: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    league: FangraphsLeagueTypes = FangraphsLeagueTypes.ALL,
    min_at_bats: str = "y",
    rost: int = 0,
    team: str = "",
    handedness: str = "",
) -> pl.DataFrame | pd.DataFrame:
    # Prepare stat types dictionary
    if stat_types is None:
        stat_types = {stat: stat.value for stat in list(FangraphsBattingStatType)}
    elif len(stat_types) == 0:
        raise ValueError("stat_types must not be an empty list")
    if min_at_bats != "y":
        print("Warning: using a custom minimum at bats may result in missing data")

    async with aiohttp.ClientSession() as session:
        tasks = [
            get_table_data_async(
                session,
                stat_type=stat_types[stat],
                pos=pos,
                league=league,
                start_date=start_date,
                end_date=end_date,
                min_at_bats=min_at_bats,
                start_season=start_season,
                end_season=end_season,
                handedness=handedness,
                rost=rost,
                team=team,
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


async def get_table_data_async(
    session,
    stat_type,
    pos,
    league,
    start_date,
    end_date,
    min_at_bats,
    start_season,
    end_season,
    handedness,
    rost,
    team,
):
    url = (
        "https://www.fangraphs.com/leaders/major-league?"
        "pos={pos}&stats=bat&lg={league}&qual={min_at_bats}&type={stat_type}"
        "&season={end_season}&season1={start_season}&ind=0"
        "&startdate={start_date}&enddate={end_date}&hand={handedness}"
        "&rost={rost}&month=0&team={team}&pagenum=1&pageitems=2000000000"
    )
    url = url.format(
        pos=pos,
        league=league,
        min_at_bats=min_at_bats,
        stat_type=stat_type,
        start_date=start_date if start_date is not None else "",
        end_date=end_date if end_date is not None else "",
        start_season=start_season if start_season is not None else "",
        end_season=end_season if end_season is not None else "",
        handedness=handedness,
        rost=rost,
        team=team,
    )
    try:
        async with session.get(url) as response:
            cont = await response.text()
    except aiohttp.ClientOSError as e:
        print(f"ClientOSError: {e}")
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

    # Ensure "Name" column exists for joins
    df = pl.DataFrame(data, infer_schema_length=None)
    if "Name" not in df.columns:
        df = df.with_column(pl.lit(None).alias("Name"))
    return df
