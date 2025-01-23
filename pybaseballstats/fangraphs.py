from enum import Enum
from typing import List

import pandas as pd
import polars as pl
import requests
from bs4 import BeautifulSoup

url = "https://www.fangraphs.com/leaders/major-league?pos={pos}&stats=bat&lg={league}&qual={qual}&type={stat_type}&season={end_season}&season1={start_season}&ind=0&startdate={start_date}&enddate={end_date}&month=0&team=0&pagenum=1&pageitems=2000000000"

# pos options: c, 1b,2b,3b, ss, lf, cf, rf, dh, of, p, all
# qual options: y, n
# league options: "", "al", "nl"
# start date, end date are strings in the format "yyyy-mm-dd"
# stat options: 8 (dashboard), 0 (standard), 1 (advanced), 2 (batted ball), 3 (win_probability), 6 (value), 23 (+stats),24 (statcast), 48 (violations)


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


def get_table_data(
    stat_type, pos, league, start_date, end_date, qual, start_season, end_season
):
    # Assuming `cont` contains the HTML content
    cont = requests.get(
        url.format(
            pos="all",
            league="",
            stat_type=stat_type,
            start_season=1900,
            end_season=2024,
            qual="y",
            start_date="",
            end_date="",
        )
    ).content.decode("utf-8")

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
        # Print row_data for debugging
        data.append(row_data)

    # Create a Polars DataFrame from the extracted data
    df = pl.DataFrame(data)
    return df


def show_fangraphs_batting_stat_types():
    for stat_type in FangraphsBattingStatType:
        print(stat_type)


def show_batting_pos_options():
    print("c,1b,2b,3b,ss,lf,cf,rf,dh,of,p,all")


def fangraphs_batting_date_range(
    start_date: str,
    end_date: str,
    stat_types: List[FangraphsBattingStatType] = None,
    return_pandas: bool = False,
    pos: str = "all",
    league: str = "",
    qual: str = "y",
) -> pl.DataFrame | pd.DataFrame:
    """Pulls Fangraphs batting data for a date range.

    Args:
        start_date (str): format "yyyy-mm-dd", ex) "2021-04-01"
        end_date (str): format "yyyy-mm-dd", ex) "2021-04-01"
        stat_types (List[FangraphsBattingStatType], optional): List of what Fangraphs stat types to include, more information can be found by calling pyb.show_fangraphs_stat_types(). Defaults to None, meaning all stat types will be returned.
        return_pandas (bool, optional): whether to return a Polars Dataframe (False) or a Pandas Dataframe (True). Defaults to False.
        pos (str, optional): What positions to return data for. More information can be found by calling pyb.show_batting_pos_options(). Defaults to "all".
        league (str, optional): What league to return data for, options are ""(all), "nl", "al". Defaults to "".
        qual (str, optional): whether or not to restrict to qualified batters, to return unqualified batters pass "n" as the argument. Defaults to "y".

    Returns:
        pl.DataFrame | pd.DataFrame: The requested data as a Polars or Pandas DataFrame.
    """
    df_list = []
    if stat_types is None:
        stat_types = FangraphsBattingStatType
    if len(stat_types) == 0:
        print(
            "Warning: No stat types provided, returning None, to return all stattypes, pass in None."
        )
        return None
    for stat_type in stat_types:
        print(f"Fetching data for {stat_type}...")
        df = get_table_data(
            stat_type=stat_types[stat_type.value],
            pos=pos,
            league=league,
            start_date=start_date,
            end_date=end_date,
            qual=qual,
            start_season="",
            end_season="",
        )
        if df is not None:
            print(f"Data fetched for {stat_type}")
            df_list.append(df)
        else:
            print(f"Warning: No data returned for {stat_type}")
    df = pl.concat(df_list, how="diagonal")
    df = df.select(pl.col("Name").drop_nulls())
    return df.to_pandas() if return_pandas else df


def fangraphs_batting_season_range(
    start_season,
    end_season,
    stat_types,
    return_pandas=False,
    pos="all",
    league="",
    qual="y",
) -> pl.DataFrame | pd.DataFrame:
    df_list = []
    if stat_types is None:
        stat_types = FangraphsBattingStatType
    if len(stat_types) == 0:
        print(
            "Warning: No stat types provided, returning None, to return all stattypes, pass in None."
        )
        return None
    for stat_type in stat_types:
        print(f"Fetching data for {stat_type}...")
        df = get_table_data(
            stat_type=stat_types[stat_type.value],
            pos=pos,
            league=league,
            start_date="",
            end_date="",
            qual=qual,
            start_season=start_season,
            end_season=end_season,
        )
        if df is not None:
            print(f"Data fetched for {stat_type}")
            df_list.append(df)
        else:
            print(f"Warning: No data returned for {stat_type}")
    df = pl.concat(df_list, how="diagonal")
    df = df.select(pl.col("Name").drop_nulls())
    return df.to_pandas() if return_pandas else df


def fangraphs_pitching_date_range():
    print("Not implemented yet.")


def fangraphs_pitching_season_range():
    print("Not implemented yet.")


def fangraphs_fielding_date_range():
    print("Not implemented yet.")


def fangraphs_fielding_season_range():
    print("Not implemented yet.")
