from typing import Literal

import polars as pl
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

PARK_FACTOR_DIMENSIONS_URL = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=dimensions&year={season}&batSide=&stat=index_wOBA&condition=All&rolling=3&parks=mlb&fenceStatType={metric_type}&csv=true"


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
    url = PARK_FACTOR_DIMENSIONS_URL.format(season=season, metric_type=metric)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector("#parkFactors")
        page.wait_for_selector("#ddlSeason")
        selection_wrapper_html = page.inner_html("#season-container > div")

        table_html = page.inner_html("#parkFactors")

        page.close()
        browser.close()
    selection_wrapper = BeautifulSoup(selection_wrapper_html, "html.parser")
    table_soup = BeautifulSoup(table_html, "html.parser")
    season_options_selection_elt = selection_wrapper.find("select", {"id": "ddlSeason"})
    valid_seasons = [
        int(option.get("value"))
        for option in season_options_selection_elt.find_all("option")
    ]
    if season not in valid_seasons:
        raise ValueError(
            f"Season {season} is not valid. Valid seasons are: {valid_seasons}"
        )
    table = table_soup.find("table")
    table_data = {}
    index_to_stat_mapping = {}
    thead = table.find("thead")
    for tr in thead.find_all("tr"):
        if tr.get("class") != ["tr-component-row"]:
            continue
        for th in tr.find_all("th"):
            if th.text.strip() == "Rk.":
                continue
            if metric == "distance":
                if "venue-info-height-col" in th.get("class", []):
                    continue
            elif metric == "height":
                if "venue-info-dist-col" in th.get("class", []):
                    continue
            table_data[th.text.strip()] = []
            index_to_stat_mapping[len(table_data) - 1] = th.text.strip()
    tbody = table.find("tbody")
    for row in tbody.find_all("tr"):
        if "default-table-row" not in row.get("class", []):  # skip non-data rows
            continue
        i = 0
        for td in row.find_all("td"):
            if td.get("class") is None:
                continue  # skip if no class attribute
            if "tr-data" in td.get("class", []):
                if "venue-info-height-col" in td.get(
                    "class", []
                ) or "venue-info-dist-col" in td.get("class", []):
                    if metric == "distance":
                        if "venue-info-height-col" in td.get(
                            "class", []
                        ):  # skip height column if we're looking at distance
                            continue
                    elif metric == "height":
                        if "venue-info-dist-col" in td.get(
                            "class", []
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
    return df


if __name__ == "__main__":
    distance_df = park_factor_dimensions(2025, "distance")
    print(distance_df)
    height_df = park_factor_dimensions(2025, "height")
    print(height_df)
