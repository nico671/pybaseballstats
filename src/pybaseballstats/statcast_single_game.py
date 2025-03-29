import asyncio
import datetime
import io
from contextlib import contextmanager

import pandas as pd
import polars as pl
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pybaseballstats.statcast import statcast_date_range_pitch_by_pitch
from pybaseballstats.utils.statcast_utils import ROOT_URL, SINGLE_GAME, _add_extra_stats

STATCAST_SINGLE_GAME_EV_PV_WP_URL = "https://baseballsavant.mlb.com/gamefeed?date={game_date}&gamePk={game_pk}&chartType=pitch&legendType=pitchName&playerType=pitcher&inning=&count=&pitchHand=&batSide=&descFilter=&ptFilter=&resultFilter=&hf={stat_type}&sportId=1&liveAb=#{game_pk}"


# TODO: usage docs
@contextmanager
def get_driver():
    """Provides a WebDriver instance that automatically quits on exit."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    try:
        yield driver  # Hands control back to the calling function
    finally:
        driver.quit()  # Ensures WebDriver is always closed


def statcast_single_game_pitch_by_pitch(
    game_pk: int, extra_stats: bool = False, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    """Pulls statcast data for a single game.

    Args:
        game_pk (int): game_pk of the game you want to pull data for
        extra_stats (bool): whether or not to include extra stats
        return_pandas (bool, optional): whether or not to return as a Pandas DataFrame. Defaults to False (returns Polars LazyFrame).

    Returns:
        pl.DataFrame | pd.DataFrame: DataFrame of statcast data for the game
    """
    response = requests.get(
        ROOT_URL + SINGLE_GAME.format(game_pk=game_pk),
    )
    statcast_content = response.content
    if not extra_stats:
        df = pl.scan_csv(io.StringIO(statcast_content.decode("utf-8"))).collect()
    else:
        df = pl.scan_csv(io.StringIO(statcast_content.decode("utf-8")))
        start_dt = df.select(pl.col("game_date").min())
        end_dt = df.select(pl.col("game_date").max())
        df = asyncio.run(
            _add_extra_stats(df, start_dt, end_dt, return_pandas)
        ).collect()
    return df if not return_pandas else df.to_pandas()


def get_available_game_pks_for_date(
    game_date: str,
):
    available_games = {}
    df = statcast_date_range_pitch_by_pitch(game_date, game_date).collect()
    if df.shape[0] == 0 or df.shape[1] == 0:
        # No games found for the specified date
        print(
            "No games found for the specified date. Please check the date format / date and try again."
        )
        return available_games
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
    try:
        dt_object = datetime.datetime.strptime(game_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Incorrect date format. Please use YYYY-MM-DD format.")
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

    with get_driver() as driver:
        # Use the URL from the previous cell
        driver.get(
            STATCAST_SINGLE_GAME_EV_PV_WP_URL.format(
                game_date=game_date_str, game_pk=game_pk, stat_type="exitVelocity"
            )
        )

        # Wait for the chart to load
        wait = WebDriverWait(driver, 10)
        ev_table = wait.until(
            EC.presence_of_element_located(
                (By.ID, "exitVelocityTable_{game_pk}".format(game_pk=game_pk))
            )
        )
        ev_table_html = ev_table.get_attribute("outerHTML")

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
            pl.col("bat_speed").str.replace("⚡", "").cast(pl.Float32),
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
    game_date_str = _handle_single_game_date(game_date)
    with get_driver() as driver:
        driver.get(
            STATCAST_SINGLE_GAME_EV_PV_WP_URL.format(
                game_date=game_date_str, game_pk=game_pk, stat_type="pitchVelocity"
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
            pl.col("Inning").cast(pl.Int8),
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


def get_statcast_single_game_wp_table(
    game_pk: int,
    game_date: str,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    game_date_str = _handle_single_game_date(game_date)
    with get_driver() as driver:
        # Use the URL from the previous cell
        driver.get(
            STATCAST_SINGLE_GAME_EV_PV_WP_URL.format(
                game_date=game_date_str, game_pk=game_pk, stat_type="winProbability"
            )
        )

        # Wait for the chart to load
        wait = WebDriverWait(driver, 10)
        wp_table = wait.until(
            EC.presence_of_element_located(
                (By.ID, "tableWinProbability_{game_pk}".format(game_pk=game_pk))
            )
        )
        wp_table_html = wp_table.get_attribute("outerHTML")

    soup = BeautifulSoup(wp_table_html, "html.parser")
    table = soup.find("table")

    thead = table.thead
    headers_tr = thead.find("tr", {"class": "tr-component-row"})
    headers = [th.text for th in headers_tr.find_all("th") if th.text != ""]

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

    df = pl.DataFrame(row_data)
    df = df.rename(
        {
            "#": "game_pa_number",
            "Batter": "batter_name",
            "Pitcher": "pitcher_name",
            "Diff": "win_probability_diff",
        }
    )
    df = df.with_columns(
        pl.all().replace("", None),
    )

    df = df.with_columns(
        [
            pl.col("game_pa_number").cast(pl.Int16),
            pl.col("win_probability_diff").cast(pl.Float32),
            pl.col("Home WP%").cast(pl.Float32),
            pl.col("Away WP%").cast(pl.Float32),
        ]
    )
    return df if not return_pandas else df.to_pandas()
