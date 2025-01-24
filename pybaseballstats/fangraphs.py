from enum import Enum
from typing import List

import pandas as pd
import polars as pl
import requests
from bs4 import BeautifulSoup
from polars import selectors as cs
from tqdm import tqdm

url = "https://www.fangraphs.com/leaders/major-league?pos={pos}&stats=bat&lg={league}&qual={min_at_bats}&type={stat_type}&season={end_season}&season1={start_season}&ind=0&startdate={start_date}&enddate={end_date}&month=0&team=0&pagenum=1&pageitems=2000000000"


# Define the available stat types as an Enum
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


def get_table_data(
    stat_type, pos, league, start_date, end_date, min_at_bats, start_season, end_season
):
    url = "https://www.fangraphs.com/leaders/major-league?pos={pos}&stats=bat&lg={league}&qual={min_at_bats}&type={stat_type}&season={end_season}&season1={start_season}&ind=0&startdate={start_date}&enddate={end_date}&month=0&team=0&pagenum=1&pageitems=2000000000"
    url = url.format(
        pos=pos,
        league=league,
        min_at_bats=min_at_bats,
        stat_type=stat_type,
        start_date=start_date,
        end_date=end_date,
        start_season=start_season,
        end_season=end_season,
    )
    # Assuming `cont` contains the HTML content
    cont = requests.get(url).content.decode("utf-8")

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(cont, "html.parser")

    # Find the main table using the provided CSS selector
    main_table = soup.select_one(
        "#content > div.leaders-major_leaders-major__table__hcmbm > div.fg-data-grid.table-type > div.table-wrapper-outer > div > div.table-scroll > table"
    )

    # Find the table header
    thead = main_table.find("thead")

    # Extract column names from the data-col-id attribute of the <th> elements, excluding "divider"
    headers = [
        th["data-col-id"]
        for th in thead.find_all("th")
        if "data-col-id" in th.attrs and th["data-col-id"] != "divider"
    ]

    # Find the table body within the main table
    tbody = main_table.find("tbody")

    # Initialize a list to store the extracted data
    data = []

    # Iterate over each row in the table body
    for row in tbody.find_all("tr"):
        row_data = {header: None for header in headers}  # Initialize with None
        for cell in row.find_all("td"):
            col_id = cell.get("data-col-id")

            if col_id and col_id != "divider":
                # if col_id == "Name":
                #     row_data[col_id] = cell.find("a").text
                #     if cell.find("a"):
                #         row_data[col_id] = cell.find("a").text
                #     elif cell.find("span"):
                #         row_data[col_id] = cell.find("span").text
                #     else:
                #         text = cell.text.strip()
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
                        except Exception as e:
                            print(e)
                            print(cell.attrs["data-col-id"])
                            row_data[col_id] = text
        # Print row_data for debugging
        data.append(row_data)

    # Create a Polars DataFrame from the extracted data
    df = pl.DataFrame(data, infer_schema_length=None)
    return df


def show_fangraphs_batting_stat_types():
    for stat_type in FangraphsBattingStatType:
        print(stat_type)


def show_batting_pos_options():
    print("c,1b,2b,3b,ss,lf,cf,rf,dh,of,p,all")


# TODO: Add more options
# - Add support for specifying team (team=) options are given by ints so need to make an enum for that
# - add support for restricting only to active roster players (rost=) (0 for all, 1 for active roster)
# - add support for season type (postseason=) ("" for regular season, "Y" for all postseason, "W" for world series, "L" for league championship series, "D" for division series, "F" for wild card game)
# - add support for handedness (hand=) ("" for all, "R" for right handed batters, "L" for left handed batters, "S" for switch hitters)
# - add support for age (age=) ("start_age,end_age")
def fangraphs_batting_range(
    start_date: str = None,
    end_date: str = None,
    start_season: str = None,
    end_season: str = None,
    stat_types: List[FangraphsBattingStatType] = None,
    return_pandas: bool = False,
    pos: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    league: FangraphsLeagueTypes = FangraphsLeagueTypes.ALL,
    min_at_bats: str = "y",
) -> pl.DataFrame | pd.DataFrame:
    """Pulls batting data from Fangraphs for a given date range or season range. Additional options include filtering by position and league, as well as the ability to specify which stats to pull.

    Args:
        start_date (str, optional): First date for which you want to pull data for, format should follow "yyyy-mm-dd" (ex. ("2024-04-01")). Defaults to None.
        end_date (str, optional): Last date for which you want to pull data for, format should follow "yyyy-mm-dd" (ex. ("2024-06-01")). Defaults to None.
        start_season (str, optional): First season for which you want to pull data for, format should follow "yyyy" (ex. ("2023")). Defaults to None.
        end_season (str, optional): Last season for which you want to pull data for, format should follow "yyyy" (ex. ("2024")). Defaults to None.
        stat_types (List[FangraphsBattingStatType], optional): What stat types to include in the data. Defaults to None (all data types will be retrieved).
        return_pandas (bool, optional): Should the returned dataframe be a Polars Dataframe (False) or a Pandas dataframe (True). Defaults to False.
        pos (FangraphsBattingPosTypes, optional): What batter positions you want to include in your search. Defaults to FangraphsBattingPosTypes.ALL.
        league (FangraphsLeagueTypes, optional): What leagues you want included in your search. Defaults to FangraphsLeagueTypes.ALL.
        min_at_bats (str, optional): Minimum number of at bats to be included in the dataset (ex min_at_bats="123"). Defaults to "y" (qualified hitters).

    Raises:
        ValueError: If both date range (start_date and end_date) and season range (start_season and end_season) are not provided.
        ValueError: If stat_types is an empty list (if you are trying to get all stat_types pass in None).

    Returns:
        pl.DataFrame | pd.DataFrame: A Polars or Pandas DataFrame containing the requested data.
    """
    if (start_date is None or end_date is None) and (
        start_season is None or end_season is None
    ):
        raise ValueError(
            "Either start_date and end_date must not be None or start_season and end_season must not be None"
        )
    df_list = []
    if stat_types is None:
        stat_types = {}
        for stat_type in FangraphsBattingStatType:
            stat_types[stat_type] = stat_type.value
    elif len(stat_types) == 0:
        raise ValueError("stat_types must not be an empty list")
    if min_at_bats != "y":
        print(
            "Warning: setting a custom minimum at bats value may result in missing data"
        )
    for stat_type in tqdm(stat_types, desc="Fetching data"):
        # print(f"Fetching data for {stat_type}...")
        print(league)
        df = get_table_data(
            stat_type=stat_types[stat_type],
            pos=pos,
            league=league,
            start_date=start_date if start_date is not None else "",
            end_date=end_date if end_date is not None else "",
            min_at_bats=min_at_bats,
            start_season=start_season if start_season is not None else "",
            end_season=end_season if end_season is not None else "",
        )
        if df is not None:
            # print(f"Data fetched for {stat_type}")
            df_list.append(df)
        else:
            print(f"Warning: No data returned for {stat_type}")

    df = df_list[0]
    for i in range(1, len(df_list)):
        df = df.join(df_list[i], on="Name", how="full").select(
            ~cs.ends_with("_right"),
        )
    return df.to_pandas() if return_pandas else df


def fangraphs_pitching_date_range():
    print("Not implemented yet.")


def fangraphs_pitching_season_range():
    print("Not implemented yet.")


def fangraphs_fielding_date_range():
    print("Not implemented yet.")


def fangraphs_fielding_season_range():
    print("Not implemented yet.")
