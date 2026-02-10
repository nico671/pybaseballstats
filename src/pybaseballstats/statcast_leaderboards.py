from datetime import datetime
from typing import Literal

import polars as pl
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from pybaseballstats.consts.statcast_leaderboard_consts import (
    PARK_FACTOR_DIMENSIONS_URL,
    PARK_FACTOR_DISTANCE_URL,
    PARK_FACTOR_YEARLY_URL,
)


def park_factor_dimensions(
    season: int, metric: Literal["distance", "height"] = "distance"
):
    """Returns park dimension data from Baseball Savant

    Args:
        season (int): Which season to return data for. Must be between 2015 and the current season.
        metric (Literal["distance", "height"], optional): Which metric to return data for. Defaults to "distance".

    Raises:
        ValueError: If the metric is not "distance" or "height".
        ValueError: If the season is not between 2015 and the current season.

    Returns:
        pl.DataFrame: A DataFrame containing the park dimension data.
    """
    if metric not in ["distance", "height"]:
        raise ValueError("Metric must be either 'distance' or 'height'")
    curr_season = (
        datetime.now().year if datetime.now().month >= 3 else datetime.now().year - 1
    )
    if season < 2015 or season > curr_season:
        raise ValueError(f"Season must be between 2015 and {curr_season}")
    url = PARK_FACTOR_DIMENSIONS_URL.format(season=season, metric_type=metric)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url)
            page.wait_for_selector("#parkFactors")

            table_html = page.inner_html("#parkFactors")
        finally:
            page.close()
            browser.close()

    table_soup = BeautifulSoup(table_html, "html.parser")

    table = table_soup.find("table")
    assert table is not None, "Could not find data table on page"
    table_data: dict[str, list[str]] = {}
    index_to_stat_mapping = {}
    thead = table.find("thead")
    assert thead is not None, "Could not find table header element"
    for tr in thead.find_all("tr"):
        tr_class = tr.get("class")
        if tr_class != ["tr-component-row"]:
            continue
        for th in tr.find_all("th"):
            if th.text.strip() == "Rk.":
                continue
            if metric == "distance":
                th_class = th.get("class")
                if (
                    th_class
                    and isinstance(th_class, list)
                    and "venue-info-height-col" in th_class
                ):
                    continue
            elif metric == "height":
                th_class = th.get("class")
                if (
                    th_class
                    and isinstance(th_class, list)
                    and "venue-info-dist-col" in th_class
                ):
                    continue
            table_data[th.text.strip()] = []
            index_to_stat_mapping[len(table_data) - 1] = th.text.strip()
    tbody = table.find("tbody")
    assert tbody is not None, "Could not find table body element"
    for row in tbody.find_all("tr"):
        row_class = row.get("class")
        if (
            not row_class
            or not isinstance(row_class, list)
            or "default-table-row" not in row_class
        ):  # skip non-data rows
            continue
        i = 0
        for td in row.find_all("td"):
            td_class = td.get("class")
            if td_class is None:
                continue  # skip if no class attribute
            if not isinstance(td_class, list):
                continue
            if "tr-data" in td_class:
                if (
                    "venue-info-height-col" in td_class
                    or "venue-info-dist-col" in td_class
                ):
                    if metric == "distance":
                        if (
                            "venue-info-height-col" in td_class
                        ):  # skip height column if we're looking at distance
                            continue
                    elif metric == "height":
                        if (
                            "venue-info-dist-col" in td_class
                        ):  # skip distance column if we're looking at height
                            continue
                stat_name = index_to_stat_mapping.get(i)
                if stat_name:
                    table_data[stat_name].append(td.text.strip())
                    i += 1
    df = pl.DataFrame(table_data)
    # renaming columns
    if metric == "distance":
        df = df.rename(
            {
                "LF Line": "lf_line_distance_ft",
                "LF Gap": "lf_gap_distance_ft",
                "CF": "cf_distance_ft",
                "RF Gap": "rf_gap_distance_ft",
                "RF Line": "rf_line_distance_ft",
                "DeepestPointDeepest point of park. May or may not be one of 5 standard points displayed.": "deepest_point_distance_ft",
                "Playing FieldArea (sq. ft.)Fair Territory Only": "playing_field_area_sq_ft",
                "Avg. Fence  Distance": "avg_fence_distance_ft",
                "Avg. Fence Height": "avg_fence_height_ft",
                "Avg. HREstimated by averaging the (fence distance + fence height) throughout the entire outfield.": "avg_hr_distance_ft",
            }
        )
        df = df.with_columns(
            pl.all().str.replace(r"\([-+]\s*\d+\)", "").str.strip_chars_end(" ")
            # .cast(pl.Int64)
        )
        df = df.with_columns(
            pl.col("playing_field_area_sq_ft")
            .str.replace(r",", "")
            .str.replace(r"\s*\([-+]?\d+\.?\d*%\)", "")
            .cast(pl.Int64)
        )
        int_columns = [
            "lf_line_distance_ft",
            "lf_gap_distance_ft",
            "cf_distance_ft",
            "rf_gap_distance_ft",
            "rf_line_distance_ft",
            "deepest_point_distance_ft",
            "playing_field_area_sq_ft",
            "avg_fence_distance_ft",
            "avg_hr_distance_ft",
            "Season",
        ]
        float_columns = ["avg_fence_height_ft"]
        df = df.with_columns(
            pl.col(int_columns).cast(pl.Int64),
            pl.col(float_columns).cast(pl.Float64),
        )
    elif metric == "height":
        df = df.rename(
            {
                "LF Line": "lf_line_height_ft",
                "LF Gap": "lf_gap_height_ft",
                "CF": "cf_height_ft",
                "RF Gap": "rf_gap_height_ft",
                "RF Line": "rf_line_height_ft",
                "HighestPointHighest height of the fence. May or may not be one of 5 standard points displayed.": "highest_point_height_ft",
                "Playing FieldArea (sq. ft.)Fair Territory Only": "playing_field_area_sq_ft",
                "Avg. Fence  Distance": "avg_fence_distance_ft",
                "Avg. Fence Height": "avg_fence_height_ft",
                "Avg. HREstimated by averaging the (fence distance + fence height) throughout the entire outfield.": "avg_hr_distance_ft",
            }
        )
        df = df.with_columns(
            pl.all().str.replace(r"\([-+]\s*\d+\)", "").str.strip_chars_end(" ")
            # .cast(pl.Int64)
        )
        df = df.with_columns(
            pl.col("playing_field_area_sq_ft")
            .str.replace(r",", "")
            .str.replace(r"\s*\([-+]?\d+\.?\d*%\)", "")
            .cast(pl.Int64)
        )
        int_columns = [
            "lf_line_height_ft",
            "lf_gap_height_ft",
            "cf_height_ft",
            "rf_gap_height_ft",
            "rf_line_height_ft",
            "highest_point_height_ft",
            "playing_field_area_sq_ft",
            "avg_fence_distance_ft",
            "avg_hr_distance_ft",
            "Season",
        ]
        float_columns = ["avg_fence_height_ft"]
        df = df.with_columns(
            pl.col(int_columns).cast(pl.Int64),
            pl.col(float_columns).cast(pl.Float64),
        )
    return df


def park_factor_yearly(
    season: int,
    bat_side: Literal["L", "R", ""] = "",
    conditions: Literal["All", "Day", "Night", "Open Air", "Roof Closed"] = "All",
    rolling_years: int = 3,  # 1,2,3
) -> pl.DataFrame:
    """Returns park specific statistics from Baseball Savant.

    Args:
        season (int): Which season to return data for. Must be between 1999 and the current season.
        bat_side (Literal["L", "R", ""], optional): Optional value to restrict data by batter side. Defaults to "".
        conditions (Literal["All", "Day", "Night", "Open Air", "Roof Closed"], optional): Optional value to restrict data by game conditions. Defaults to "All".
        rolling_years (int, optional): Number of rolling years to include in the calculation. Calculated as rolling years backward from season parameter. Defaults to 3.

    Raises:
        ValueError: If bat_side is not "L", "R", or "".
        ValueError: If conditions is not "All", "Day", "Night", "Open Air", or "Roof Closed".
        ValueError: If rolling_years is not 1, 2, or 3.
        ValueError: If season is not between 1999 and the current season.
    Returns:
        pl.DataFrame: DataFrame containing park specific statistics.
    """
    if bat_side not in ["L", "R", ""]:
        raise ValueError("bat_side must be 'L', 'R', or ''")
    if conditions not in ["All", "Day", "Night", "Open Air", "Roof Closed"]:
        raise ValueError(
            "conditions must be one of 'All', 'Day', 'Night', 'Open Air', or 'Roof Closed'"
        )
    if rolling_years not in [1, 2, 3]:
        raise ValueError("rolling_years must be 1, 2, or 3")
    curr_season = (
        datetime.now().year if datetime.now().month >= 3 else datetime.now().year - 1
    )
    if season < 1999 or season > curr_season:
        raise ValueError(f"Season must be between 1999 and {curr_season}")

    url = PARK_FACTOR_YEARLY_URL.format(
        season=season,
        bat_side=bat_side,
        condition=conditions,
        rolling_years=rolling_years,
    )
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url)
            page.wait_for_selector("#parkFactors")

            table_html = page.inner_html("#parkFactors")
        finally:
            page.close()
            browser.close()

    table_soup = BeautifulSoup(table_html, "html.parser")

    table = table_soup.find("table")
    assert table is not None, "Could not find data table on page"
    table_data: dict[str, list[str | None]] = {}
    index_to_stat_mapping = {}
    thead = table.find("thead")
    assert thead is not None, "Could not find table header element"
    for tr in thead.find_all("tr"):
        tr_class = tr.get("class")
        if tr_class != ["tr-component-row"]:
            continue
        for th in tr.find_all("th"):
            if th.text.strip() == "Rk.":
                continue
            table_data[th.text.strip()] = []
            index_to_stat_mapping[len(table_data) - 1] = th.text.strip()
    tbody = table.find("tbody")
    assert tbody is not None, "Could not find table body element"
    for row in tbody.find_all("tr"):
        row_class = row.get("class")
        if (
            not row_class
            or not isinstance(row_class, list)
            or "default-table-row" not in row_class
        ):  # skip non-data rows
            continue
        i = 0
        for td in row.find_all("td"):
            td_class = td.get("class")
            if td_class is None:
                continue  # skip if no class attribute
            if not isinstance(td_class, list):
                continue
            if "tr-data" in td_class:
                stat_name = index_to_stat_mapping.get(i)
                if stat_name:
                    table_data[stat_name].append(
                        td.text.strip() if td.text.strip() != "" else None
                    )
                    i += 1
    df = pl.DataFrame(table_data)
    df = df.with_columns(
        pl.col(list(set(df.columns) - {"Team", "Year", "Venue", "PA"})).cast(pl.Int64)
    )
    return df


def park_factor_distance(season: int) -> pl.DataFrame:
    """Returns park factor distance data from Baseball Savant

    Args:
        season (int): Which season to return data for. Must be between 2016 and the current season.

    Raises:
        ValueError: If the season is not between 2016 and the current season.
    Returns:
        pl.DataFrame: A DataFrame containing the park factor distance data.
    """
    curr_season = (
        datetime.now().year if datetime.now().month >= 3 else datetime.now().year - 1
    )
    if season < 2016 or season > curr_season:
        raise ValueError(f"Season must be between 2016 and {curr_season}")

    url = PARK_FACTOR_DISTANCE_URL.format(season=season)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url)
            page.wait_for_selector("#parkFactors")

            table_html = page.inner_html("#parkFactors")
        finally:
            page.close()
            browser.close()

    table_soup = BeautifulSoup(table_html, "html.parser")
    thead = table_soup.find("thead")
    assert thead is not None, "Could not find table header element"
    table_data: dict[str, list[str | None]] = {}
    index_to_stat_mapping = {}
    for tr in thead.find_all("tr", {"class": "tr-component-row"}):
        for th in tr.find_all("th"):
            if th.text.strip() == "Rk.":
                continue
            if th.text.strip() == "Elev" and "Elev" in table_data:
                col_name = "Elevation"
            else:
                col_name = th.text.strip()
            table_data[col_name] = []
            index_to_stat_mapping[len(table_data) - 1] = col_name
    tbody = table_soup.find("tbody")
    assert tbody is not None, "Could not find table body element"

    for row in tbody.find_all("tr"):
        row_class = row.get("class")
        if (
            not row_class
            or not isinstance(row_class, list)
            or "default-table-row" not in row_class
        ):  # skip non-data rows
            continue
        i = 0
        for td in row.find_all("td"):
            td_class = td.get("class")
            if td_class is None:
                continue  # skip if no class attribute
            if not isinstance(td_class, list):
                continue
            if "tr-data" not in td_class:
                continue
            stat_name = index_to_stat_mapping.get(i)
            if stat_name:
                table_data[stat_name].append(
                    td.text.strip() if td.text.strip() != "" else None
                )
                i += 1
    df = pl.DataFrame(table_data)
    df = df.rename(
        {
            "Total": "total_extra_distance_ft",
            "Temp": "extra_distance_temp_effect_ft",
            "Elev": "extra_distance_elevation_effect_ft",
            "Env": "extra_distance_environment_effect_ft",
            "Roof": "extra_distance_roof_effect_ft",
            "Avg Temp": "avg_stadium_temperature_f",
            "Elevation": "stadium_elevation_ft",
            "Roof %": "pct_stadium_roofed",
            "Day %": "pct_stadium_day_games",
        }
    )
    int_cols = [
        "stadium_elevation_ft",
        "pct_stadium_roofed",
        "pct_stadium_day_games",
    ]
    float_cols = [
        "total_extra_distance_ft",
        "extra_distance_temp_effect_ft",
        "extra_distance_elevation_effect_ft",
        "extra_distance_environment_effect_ft",
        "extra_distance_roof_effect_ft",
        "avg_stadium_temperature_f",
    ]
    df = df.with_columns(
        pl.col(int_cols).str.replace(r",", "").cast(pl.Int64),
        pl.col(float_cols).str.replace(r",", "").cast(pl.Float64),
    )
    return df
