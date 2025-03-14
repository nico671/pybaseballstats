import datetime

import pandas as pd
import polars as pl
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pybaseballstats.statcast import statcast_date_range

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)


STATCAST_SINGLE_GAME_EV_AND_PV_URL = "https://baseballsavant.mlb.com/gamefeed?date={game_date}&gamePk={game_pk}&chartType=pitch&legendType=pitchName&playerType=pitcher&inning=&count=&pitchHand=&batSide=&descFilter=&ptFilter=&resultFilter=&hf={stat_type}&sportId=1&liveAb=#{game_pk}"


def get_available_game_pks_for_date(
    game_date: str,
):
    available_games = {}
    df = statcast_date_range(game_date, game_date).collect()
    for i, group in df.group_by("game_pk"):
        game_pk = group.select(pl.col("game_pk").first()).item()
        available_games[game_pk] = {}
        available_games[game_pk]["home_team"] = group.select(
            pl.col("home_team").first()
        ).item()
        available_games[game_pk]["away_team"] = group.select(
            pl.col("away_team").first()
        ).item()
    return available_games


def _handle_single_game_date(game_date: str):
    dt_object = datetime.datetime.strptime(game_date, "%Y-%m-%d")
    # Format date as month/day/year and replace slashes with %2F for URL encoding
    formatted_date = f"{dt_object.month}/{dt_object.day}/{dt_object.year}"
    url_encoded_date = formatted_date.replace("/", "%2F")
    return url_encoded_date


def get_statcast_single_game_exit_velocity(
    game_pk: int,
    game_date: str,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    game_date_str = _handle_single_game_date(game_date)
    try:
        # Use the URL from the previous cell
        driver.get(
            STATCAST_SINGLE_GAME_EV_AND_PV_URL.format(
                game_date=game_date_str, game_pk=game_pk, stat_type="exitVelocity"
            )
        )

        # Wait for the chart to load
        wait = WebDriverWait(driver, 10)
        print("exitVelocityTable_{game_pk}".format(game_pk=game_pk))
        ev_table = wait.until(
            EC.presence_of_element_located(
                (By.ID, "exitVelocityTable_{game_pk}".format(game_pk=game_pk))
            )
        )
        ev_table_html = ev_table.get_attribute("outerHTML")
        print(ev_table_html)

    finally:
        driver.quit()

    soup = BeautifulSoup(ev_table_html, "html.parser")
    table = soup.find("table")

    # extract headers
    thead = table.thead
    headers_tr = thead.find("tr", {"class": "tr-component-row"})
    headers = [th.text for th in headers_tr.find_all("th") if th.text != ""]

    # extract data
    tbody = table.tbody
    row_data = {header: [] for header in headers}

    for tr in tbody.find_all("tr"):
        cells = tr.find_all("td")

        # Create a mapping of filtered cells to their corresponding headers
        cell_data = {}
        header_index = 0

        for cell in cells:
            if cell.find("img", {"class": "table-team-logo"}):
                # # Skip team logo cells but increment header index
                # header_index += 1
                continue
            else:
                # Only process if we have a valid header
                if header_index < len(headers):
                    # Special handling for player name cells
                    if "player-mug-wrapper" in str(cell):
                        # Find the div that contains the player name
                        name_div = cell.find("div", {"style": "margin-left: 2px;"})
                        if name_div:
                            cell_text = name_div.get_text(strip=True)
                        else:
                            cell_text = cell.get_text(strip=True)
                    else:
                        cell_text = cell.get_text(strip=True)
                        if cell.find("a"):
                            cell_text = cell.find("a").get_text(strip=True)

                    header = headers[header_index]
                    cell_data[header] = cell_text

                header_index += 1

        # Now add all the data from this row to row_data
        for header, value in cell_data.items():
            row_data[header].append(value)

    # create df and clean df
    df = pl.DataFrame(row_data)

    df = df.drop("Rk.")
    df = df.rename(
        {
            "Batter": "batter_name",
            "PA": "num_pa",
            "Inning": "inning",
            "Result": "result",
            "Exit VeloExit Velocity (MPH)": "exit_velo",
            "LALaunch Angle (degrees)": "launch_angle",
            "Hit Dist.Hit Distance (feet)": "hit_distance",
            "BatSpeedBat Speed (mph)": "bat_speed",
            "PitchVelocityPitch Velocity (MPH)": "pitch_velocity",
            "xBAExpected Batting Average - based on exit velocity and launch angle": "xBA",
            "HR / ParkNumber of Parks where this would be a Home Run": "hr_in_how_many_parks",
        }
    )
    df = df.with_columns(
        pl.all().replace("", None),
    )
    df = df.with_columns(
        [
            pl.col("num_pa").cast(pl.Int8),
            pl.col("inning").cast(pl.Int8),
            pl.col("exit_velo").cast(pl.Float32),
            pl.col("launch_angle").cast(pl.Float32),
            pl.col("hit_distance").cast(pl.Int16),
            pl.col("bat_speed").cast(pl.Float32),
            pl.col("pitch_velocity").cast(pl.Float32),
            pl.col("xBA").cast(pl.Float32),
        ]
    )

    return df if not return_pandas else df.to_pandas()


def get_statcast_single_game_pitch_velocity(
    game_pk: int,
    game_date: str,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    try:
        driver.get(
            STATCAST_SINGLE_GAME_EV_AND_PV_URL.format(
                game_date=game_date, game_pk=game_pk, stat_type="pitchVelocity"
            )
        )

        # Wait for the chart to load
        wait = WebDriverWait(driver, 10)
        pv_table = wait.until(
            EC.presence_of_element_located(
                (By.ID, "pitchVelocity_{game_pk}".format(game_pk=game_pk))
            )
        )
        pv_table_html = pv_table.get_attribute("outerHTML")
    finally:
        driver.quit()
    soup = BeautifulSoup(pv_table_html, "html.parser")
    table = soup.find("table")

    # extract headers
    thead = table.thead
    headers_tr = thead.find("tr", {"class": "tr-component-row"})
    headers = [th.text for th in headers_tr.find_all("th") if th.text != ""]
    headers = headers[:-1]

    # extract data
    tbody = table.tbody
    row_data = {header: [] for header in headers}

    for tr in tbody.find_all("tr"):
        cells = tr.find_all("td")

        # Create a mapping of filtered cells to their corresponding headers
        cell_data = {}
        header_index = 0

        for cell in cells:
            if cell.find("img", {"class": "table-team-logo"}):
                # # Skip team logo cells but increment header index
                # header_index += 1
                continue
            else:
                # Only process if we have a valid header
                if header_index < len(headers):
                    # Special handling for player name cells
                    if "player-mug-wrapper" in str(cell):
                        # Find the div that contains the player name
                        name_div = cell.find("div", {"style": "margin-left: 2px;"})
                        if name_div:
                            cell_text = name_div.get_text(strip=True)
                        else:
                            cell_text = cell.get_text(strip=True)
                    elif "→" in str(cell) or "↑" in str(cell) or "↓" in str(cell):
                        continue
                    else:
                        cell_text = cell.get_text(strip=True)
                        if cell.find("a"):
                            cell_text = cell.find("a").get_text(strip=True)

                    header = headers[header_index]
                    cell_data[header] = cell_text

                header_index += 1

        # Now add all the data from this row to row_data
        for header, value in cell_data.items():
            row_data[header].append(value)

    # create df and clean df
    df = pl.DataFrame(row_data)
    df = df.drop(["Rk."])
    df = df.rename(
        {
            "Pitcher": "pitcher_name",
            "Batter": "batter_name",
            "Game Pitch #": "game_pitch_number",
            "Pitch": "pitcher_pitch_number",
            "PA": "game_pa_number",
            "Pitch Type": "pitch_type",
            "Pitch Vel  (MPH)": "pitch_velocity_mph",
            "Spin (RPM)": "spin_rate_rpm",
            "IVBInduced Vertical Break": "induced_vertical_break",
            "DropVertical Break": "drop_vertical_break",
            "HBreakHorizontal Break": "horizontal_break",
        }
    )
    df = df.with_columns(
        pl.all().replace("", None),
    )
    df = df.with_columns(
        [
            pl.col("game_pitch_number").cast(pl.Int32),
            pl.col("pitcher_pitch_number").cast(pl.Int16),
            pl.col("game_pa_number").cast(pl.Int16),
            pl.col("pitch_velocity_mph").cast(pl.Float32),
            pl.col("spin_rate_rpm").cast(pl.Float32),
            pl.col("induced_vertical_break").cast(pl.Float32),
            pl.col("drop_vertical_break").cast(pl.Float32),
            pl.col("horizontal_break").cast(pl.Float32),
        ]
    )
    return df if not return_pandas else df.to_pandas()
