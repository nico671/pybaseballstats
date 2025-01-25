from enum import Enum

import bs4 as BeautifulSoup
import polars as pl
import requests


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
