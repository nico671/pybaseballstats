import datetime
import io
from typing import Dict

import pandas as pd  # type: ignore[import-untyped]
import polars as pl
import requests
from bs4 import BeautifulSoup

from pybaseballstats.consts.statcast_consts import (
    STATCAST_SINGLE_GAME_EV_PV_WP_URL,
    STATCAST_SINGLE_GAME_URL,
)
from pybaseballstats.statcast import pitch_by_pitch_data
from pybaseballstats.utils.statcast_utils import get_page


def statcast_single_game_pitch_by_pitch(
    game_pk: int, return_pandas: bool = False
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
        STATCAST_SINGLE_GAME_URL.format(game_pk=game_pk),
    )
    statcast_content = response.content
    df = pl.scan_csv(io.StringIO(statcast_content.decode("utf-8"))).collect()
    return df if not return_pandas else df.to_pandas()


def get_available_game_pks_for_date(
    game_date: str,
) -> Dict[int, Dict[str, str]]:
    available_games: Dict[int, Dict[str, str]] = {}
    df = pitch_by_pitch_data(game_date, game_date)
    if df is None:
        print(
            "No games found for the specified date. Please check the date format / date and try again."
        )
        return available_games

    collected_df = df.collect() if hasattr(df, "collect") else df
    if collected_df.shape[0] == 0 or collected_df.shape[1] == 0:
        # No games found for the specified date
        print(
            "No games found for the specified date. Please check the date format / date and try again."
        )
        return available_games
    for i, group in collected_df.group_by("game_pk"):
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

    with get_page() as page:
        # Use the URL from the previous cell
        page.goto(
            STATCAST_SINGLE_GAME_EV_PV_WP_URL.format(
                game_date=game_date_str, game_pk=game_pk, stat_type="exitVelocity"
            )
        )

        # Wait for the chart to load
        page.wait_for_selector(f"#exitVelocityTable_{game_pk}", timeout=10000)
        ev_table_html = page.locator(f"#exitVelocityTable_{game_pk}").inner_html()

    soup = BeautifulSoup(ev_table_html, "html.parser")
    table = soup.find("table")
    assert table is not None, "Could not find table"

    # extract headers
    thead = table.find("thead")
    assert thead is not None, "Could not find table header"
    headers_tr = thead.find("tr", {"class": "tr-component-row"})
    assert headers_tr is not None, "Could not find header row"
    headers = [th.text for th in headers_tr.find_all("th") if th.text != ""]

    # extract data
    tbody = table.find("tbody")
    assert tbody is not None, "Could not find table body"
    row_data: Dict[str, list[str]] = {header: [] for header in headers}

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
                        link = cell.find("a")
                        if link:
                            cell_text = link.get_text(strip=True)

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
    with get_page() as page:
        page.goto(
            STATCAST_SINGLE_GAME_EV_PV_WP_URL.format(
                game_date=game_date_str, game_pk=game_pk, stat_type="pitchVelocity"
            )
        )

        # Wait for the chart to load
        page.wait_for_selector(f"#pitchVelocity_{game_pk}", timeout=10000)
        pv_table_html = page.locator(f"#pitchVelocity_{game_pk}").inner_html()

    soup = BeautifulSoup(pv_table_html, "html.parser")
    table = soup.find("table")
    assert table is not None, "Could not find table"

    # extract headers
    thead = table.find("thead")
    assert thead is not None, "Could not find table header"
    headers_tr = thead.find("tr", {"class": "tr-component-row"})
    assert headers_tr is not None, "Could not find header row"
    headers = [th.text for th in headers_tr.find_all("th") if th.text != ""]
    headers = headers[:-1]

    # extract data
    tbody = table.find("tbody")
    assert tbody is not None, "Could not find table body"
    row_data: Dict[str, list[str]] = {header: [] for header in headers}

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
                        link = cell.find("a")
                        if link:
                            cell_text = link.get_text(strip=True)

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
    with get_page() as page:
        # Use the URL from the previous cell
        page.goto(
            STATCAST_SINGLE_GAME_EV_PV_WP_URL.format(
                game_date=game_date_str, game_pk=game_pk, stat_type="winProbability"
            )
        )

        # Wait for the chart to load
        page.wait_for_selector(f"#tableWinProbability_{game_pk}", timeout=10000)
        wp_table_html = page.locator(f"#tableWinProbability_{game_pk}").inner_html()

    soup = BeautifulSoup(wp_table_html, "html.parser")
    table = soup.find("table")
    assert table is not None, "Could not find table"

    thead = table.find("thead")
    assert thead is not None, "Could not find table header"
    headers_tr = thead.find("tr", {"class": "tr-component-row"})
    assert headers_tr is not None, "Could not find header row"
    headers = [th.text for th in headers_tr.find_all("th") if th.text != ""]

    tbody = table.find("tbody")
    assert tbody is not None, "Could not find table body"
    row_data: Dict[str, list[str]] = {header: [] for header in headers}

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
                        link = cell.find("a")
                        if link:
                            cell_text = link.get_text(strip=True)

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
