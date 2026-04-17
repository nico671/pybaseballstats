import io
from datetime import datetime
from typing import List, Literal

import polars as pl
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from pybaseballstats.consts.statcast_leaderboard_consts import (
    ABS_CHALLENGES_LEADERBOARD_URL,
    ACTIVE_SPIN_LEADERBOARD_URL,
    ARM_ANGLE_LEADERBOARD_URL,
    ARM_STRENGTH_LEADERBOARD_URL,
    ARM_STRENGTH_POS_INPUT_MAP,
    PARK_FACTOR_DIMENSIONS_URL,
    PARK_FACTOR_DISTANCE_URL,
    PARK_FACTOR_YEARLY_URL,
    SPIN_DIRECTION_LEADERBOARD_URL,
    TIMER_INFRACTIONS_LEADERBOARD_URL,
    StatcastLeaderboardsTeams,
)

__all__ = [
    "StatcastLeaderboardsTeams",
    "park_factor_yearly_leaderboard",
    "park_factor_distance_leaderboard",
    "park_factor_dimensions_leaderboard",
    "timer_infractions_leaderboard",
    "arm_strength_leaderboard",
    "abs_challenges_leaderboard",
    "spin_direction_leaderboard",
    "active_spin_leaderboard",
    "arm_angle_leaderboard",
]


# region random
def park_factor_dimensions_leaderboard(
    season: int, metric: Literal["distance", "height"] = "distance"
):
    """Return Baseball Savant park-dimension leaderboard data.

    Args:
        season (int): Season year.
        metric (Literal["distance", "height"], optional): Fence metric set.

    Raises:
        ValueError: If ``metric`` is not ``"distance"`` or ``"height"``.
        ValueError: If ``season`` is outside valid supported years.

    Returns:
        pl.DataFrame: Park-dimension leaderboard data.
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
            page.goto(url, wait_until="networkidle")
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


def park_factor_yearly_leaderboard(
    season: int,
    bat_side: Literal["L", "R", ""] = "",
    conditions: Literal["All", "Day", "Night", "Open Air", "Roof Closed"] = "All",
    rolling_years: int = 3,  # 1,2,3
) -> pl.DataFrame:
    """Return Baseball Savant park-factor leaderboard data.

    Args:
        season (int): Season year.
        bat_side (Literal["L", "R", ""], optional): Batter-side filter.
        conditions (Literal["All", "Day", "Night", "Open Air", "Roof Closed"], optional):
            Game-condition filter.
        rolling_years (int, optional): Rolling-year window.

    Raises:
        ValueError: If ``bat_side`` is invalid.
        ValueError: If ``conditions`` is invalid.
        ValueError: If ``rolling_years`` is not 1, 2, or 3.
        ValueError: If ``season`` is outside valid supported years.

    Returns:
        pl.DataFrame: Park-factor leaderboard data.
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


def park_factor_distance_leaderboard(season: int) -> pl.DataFrame:
    """Return Baseball Savant park-factor distance leaderboard data.

    Args:
        season (int): Season year.

    Raises:
        ValueError: If ``season`` is outside valid supported years.

    Returns:
        pl.DataFrame: Park-factor distance leaderboard data.
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


def timer_infractions_leaderboard(
    season: int,
    perspective: Literal["Pit", "Bat", "Cat", "Team"] = "Pit",
    min_pitches: int = 1,
) -> pl.DataFrame:
    """Return Baseball Savant pitch-timer infraction leaderboard data.

    Args:
        season (int): Season year.
        perspective (Literal["Pit", "Bat", "Cat", "Team"], optional):
            Leaderboard perspective.
        min_pitches (int, optional): Minimum pitch-count threshold.

    Raises:
        ValueError: If ``perspective`` is invalid.
        ValueError: If ``min_pitches`` is less than 1.
        ValueError: If ``season`` is outside valid supported years.

    Returns:
        pl.DataFrame: Timer-infraction leaderboard data.
    """
    if perspective not in ["Pit", "Bat", "Cat", "Team"]:
        raise ValueError("perspective must be one of 'Pit', 'Bat', 'Cat', or 'Team'")
    if min_pitches < 1:
        raise ValueError("min_pitches must be at least 1")
    curr_season = (
        datetime.now().year if datetime.now().month >= 3 else datetime.now().year - 1
    )
    if season < 2023 or season > curr_season:
        raise ValueError(f"Season must be between 2023 and {curr_season}")

    resp = requests.get(
        TIMER_INFRACTIONS_LEADERBOARD_URL.format(
            perspective=perspective, season=season, min_pitches=min_pitches
        )
    )
    df = pl.read_csv(io.StringIO(resp.text))
    df = df.rename(
        {
            "entity_name": "player_name"
            if perspective in ["Pit", "Bat", "Cat"]
            else "team_name",
            "entity_id": "player_id"
            if perspective in ["Pit", "Bat", "Cat"]
            else "team_id",
        }
    )
    return df


def abs_challenges_leaderboard(
    season: int,
    challenge_type: Literal[
        "batter",
        "batting-team",
        "catcher",
        "pitcher",
        "catching-team",
        "team-summary",
        "league",
    ] = "batter",
    game_type: Literal["regular", "spring", "playoff"] = "regular",
    level: Literal["mlb", "aaa"] = "mlb",
    challenging_teams: List[StatcastLeaderboardsTeams] | None = None,
    opposing_teams: List[StatcastLeaderboardsTeams] | None = None,
    pitch_types: List[
        Literal["FF", "SI", "FC", "CH", "FS", "FO", "SC", "CU", "SL", "ST", "SV", "KN"]
    ]
    | None = None,
    attack_zone: List[Literal["11", "12", "13", "14", "16", "17", "18", "19"]]
    | None = None,
    in_zone: bool | None = None,
    min_challenges: int = 0,
    min_opp_challenges: int = 0,
) -> pl.DataFrame:
    """Return Baseball Savant ABS challenge leaderboard data.

    Args:
        season (int): Season year. Must be ``2025`` or later.
        challenge_type (Literal[...], optional): Leaderboard grouping. One of
            ``"batter"``, ``"batting-team"``, ``"catcher"``, ``"pitcher"``,
            ``"catching-team"``, ``"team-summary"``, or ``"league"``.
        game_type (Literal["regular", "spring", "playoff"], optional):
            Game-type filter.
        level (Literal["mlb", "aaa"], optional): Level filter.
        challenging_teams (List[StatcastLeaderboardsTeams], optional):
            Restrict to challenging organizations.
        opposing_teams (List[StatcastLeaderboardsTeams], optional):
            Restrict to opposing organizations.
        pitch_types (List[Literal[...]] | None, optional): Restrict to one or
            more pitch types from ``FF, SI, FC, CH, FS, FO, SC, CU, SL, ST, SV, KN``.
        attack_zone (List[Literal[...]] | None, optional): Restrict to one or
            more shadow-zone buckets from ``11, 12, 13, 14, 16, 17, 18, 19``.
        in_zone (bool | None, optional): If ``True``, include only in-zone
            challenges; if ``False``, out-of-zone only; if ``None``, no filter.
        min_challenges (int, optional): Minimum number of challenges.
        min_opp_challenges (int, optional): Minimum opponent challenge count.

    Raises:
        ValueError: If any parameter fails validation.

    Returns:
        pl.DataFrame: ABS challenges leaderboard data.
    """
    # Validate inputs

    # season must be greater than 2025
    if season < 2025:
        raise ValueError("Season must be 2025 or later")

    # level must be one of the specified options
    if level not in ["mlb", "aaa"]:
        raise ValueError("Invalid level. Must be one of 'mlb' or 'aaa'")

    # challenge_type must be one of the specified options
    if challenge_type not in [
        "batter",
        "batting-team",
        "catcher",
        "pitcher",
        "catching-team",
        "team-summary",
        "league",
    ]:
        raise ValueError(
            "Invalid challenge_type. Must be one of 'batter', 'batting-team', 'catcher', 'pitcher', 'catching-team', 'team-summary', or 'league'"
        )

    # game_type must be one of the specified options
    if game_type not in ["regular", "spring", "playoff"]:
        raise ValueError(
            "Invalid game_type. Must be one of 'regular', 'spring', or 'playoff'"
        )
    # challenging_teams and opposing_teams must be lists of StatcastLeaderboardsTeams enums or None
    if challenging_teams is not None:
        if not isinstance(challenging_teams, list) or not all(
            isinstance(team, StatcastLeaderboardsTeams) for team in challenging_teams
        ):
            raise ValueError(
                "challenging_teams must be a list of StatcastLeaderboardsTeams enums or None"
            )
        else:
            challenging_teams_param_str = "|".join(
                str(team.value) for team in challenging_teams
            )
    else:
        challenging_teams_param_str = ""
    if opposing_teams is not None:
        if not isinstance(opposing_teams, list) or not all(
            isinstance(team, StatcastLeaderboardsTeams) for team in opposing_teams
        ):
            raise ValueError(
                "opposing_teams must be a list of StatcastLeaderboardsTeams enums or None"
            )
        else:
            opposing_teams_param_str = "|".join(
                str(team.value) for team in opposing_teams
            )
    else:
        opposing_teams_param_str = ""
    # pitch_types must be a list of the specified options or None
    if pitch_types is not None:
        valid_pitch_types = [
            "FF",
            "SI",
            "FC",
            "CH",
            "FS",
            "FO",
            "SC",
            "CU",
            "SL",
            "ST",
            "SV",
            "KN",
        ]
        if not isinstance(pitch_types, list) or not all(
            pitch in valid_pitch_types for pitch in pitch_types
        ):
            raise ValueError(
                f"pitch_types must be a list of the following options or None: {valid_pitch_types}"
            )
        else:
            pitch_types_param_str = "|".join(pitch_types)
    else:
        pitch_types_param_str = ""

    # attack_zone must be a list of the specified options or None
    if attack_zone is not None:
        valid_attack_zones = ["11", "12", "13", "14", "16", "17", "18", "19"]
        if not isinstance(attack_zone, list) or not all(
            zone in valid_attack_zones for zone in attack_zone
        ):
            raise ValueError(
                f"attack_zone must be a list of the following options or None: {valid_attack_zones}"
            )
        else:
            attack_zone_param_str = "|".join(attack_zone)
    else:
        attack_zone_param_str = ""
    # in_zone must be a boolean or None
    if in_zone is not None and not isinstance(in_zone, bool):
        raise ValueError("in_zone must be a boolean or None")
    if in_zone is True:
        in_zone_param_str = "in"
    elif in_zone is False:
        in_zone_param_str = "out"
    else:
        in_zone_param_str = ""

    # min_challenges and min_opp_challenges must be non-negative integers
    if not isinstance(min_challenges, int) or min_challenges < 0:
        raise ValueError("min_challenges must be a non-negative integer")
    if not isinstance(min_opp_challenges, int) or min_opp_challenges < 0:
        raise ValueError("min_opp_challenges must be a non-negative integer")

    url = ABS_CHALLENGES_LEADERBOARD_URL.format(
        in_zone=in_zone_param_str,
        challenging_teams=challenging_teams_param_str,
        game_type=game_type,
        level=level,
        opposing_teams=opposing_teams_param_str,
        pitch_types=pitch_types_param_str,
        attack_zone=attack_zone_param_str,
        season=season,
        challenge_type=challenge_type,
        min_challenges=min_challenges,
        min_opp_challenges=min_opp_challenges,
    )
    df = pl.read_csv(io.StringIO(requests.get(url).text))
    return df


# endregion


# region fielding
def arm_strength_leaderboard(
    stat_type: Literal["player", "team"] = "player",
    year: int | str = 2025,  # All for all years (9999) is passed in
    min_throws: int = 50,
    pos: Literal[
        "All", "2b_ss_3b", "outfield", "1b", "2b", "3b", "ss", "lf", "cf", "rf"
    ] = "All",
    team: StatcastLeaderboardsTeams | None = None,
) -> pl.DataFrame:
    """Return Baseball Savant arm-strength leaderboard data.

    Args:
        stat_type (Literal["player", "team"], optional): Aggregate by player or team.
        year (int | str, optional): Season year, or ``"All"`` for all available years.
        min_throws (int, optional): Minimum throw threshold.
        pos (Literal[...], optional): Position group filter.
        team (StatcastLeaderboardsTeams | None, optional): Optional team filter.

    Raises:
        ValueError: If ``stat_type`` is invalid.
        ValueError: If ``year`` is invalid.
        ValueError: If ``min_throws`` is less than 1.
        ValueError: If ``pos`` is invalid.
        ValueError: If ``team`` is not ``None`` or ``StatcastLeaderboardsTeams``.

    Returns:
        pl.DataFrame: Arm-strength leaderboard data.
    """
    if stat_type not in ["player", "team"]:
        raise ValueError("stat_type must be either 'player' or 'team'")
    if isinstance(year, int) and (year < 2020 or year > datetime.now().year):
        raise ValueError(f"year must be between 2020 and {datetime.now().year}")

    if isinstance(year, str) and year != "All":
        raise ValueError(
            "year must be an integer between 2020 and the current year, or 'All'"
        )
    if isinstance(year, str) and year == "All":
        year = 9999

    if min_throws < 1:
        raise ValueError("min_throws must be at least 1")
    if pos not in ARM_STRENGTH_POS_INPUT_MAP.keys():
        raise ValueError(
            f"pos must be one of {list(ARM_STRENGTH_POS_INPUT_MAP.keys())}"
        )
    if team is not None and not isinstance(team, StatcastLeaderboardsTeams):
        raise ValueError(
            "team must be an instance of StatcastLeaderboardsTeams or None"
        )
    team_value = team.value if team is not None else ""
    url = ARM_STRENGTH_LEADERBOARD_URL.format(
        stat_type=stat_type,
        year=year,
        min_throws=min_throws,
        pos=ARM_STRENGTH_POS_INPUT_MAP[pos],
        team=team_value,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text), truncate_ragged_lines=True)
    if stat_type == "player":
        df = df.drop(["team_name"])
    if stat_type == "team":
        df = df.drop(
            [
                "fielder_name",
                "player_id",
                "primary_position",
                "primary_position_name",
                "total_throws",
                "total_throws_inf",
                "total_throws_of",
                "arm_inf",
                "arm_of",
            ]
        )
    return df


# endregion


# region pitching
def spin_direction_leaderboard(  # NOTE: removed pov parameter because the returned data is the same regardless of pov, i think baseball savant just changes it on the frontend but the underlying data is the same
    season: int | str = "ALL",
    team: StatcastLeaderboardsTeams | None = None,
    pitch_type: Literal[
        "FF", "CH", "CU", "FC", "FO", "KN", "SC", "SI", "SL", "SV", "FS", "ST", "ALL"
    ] = "ALL",
    pitcher_handedness: Literal["R", "L", "ALL"] = "ALL",
    min_pitches: int | str = "q",
) -> pl.DataFrame:
    # validate season input, can either be int from 2020 to current year, or "ALL"
    if isinstance(season, int):
        if season < 2020 or season > datetime.now().year:
            raise ValueError(f"season must be between 2020 and {datetime.now().year}")
    elif isinstance(season, str):
        if season != "ALL":
            raise ValueError("season must be an integer or 'ALL'")
    else:
        raise ValueError("season must be an integer or 'ALL'")

    # validate team input, must be an instance of StatcastLeaderboardsTeams or None
    if team is not None and not isinstance(team, StatcastLeaderboardsTeams):
        raise ValueError(
            "team must be an instance of StatcastLeaderboardsTeams or None"
        )
    team_id_param = str(team.value) if team is not None else ""

    # validate pitch_type input, must be one of the specified options
    if pitch_type not in [
        "FF",
        "CH",
        "CU",
        "FC",
        "FO",
        "KN",
        "SC",
        "SI",
        "SL",
        "SV",
        "FS",
        "ST",
        "ALL",
    ]:
        raise ValueError(
            "pitch_type must be one of 'FF', 'CH', 'CU', 'FC', 'FO', 'KN', 'SC', 'SI', 'SL', 'SV', 'FS', 'ST', or 'ALL'"
        )

    # validate pitcher_handedness input, must be one of the specified options
    if pitcher_handedness not in ["R", "L", "ALL"]:
        raise ValueError("pitcher_handedness must be 'R', 'L', or 'ALL'")
    throws_param = pitcher_handedness if pitcher_handedness != "ALL" else ""

    # validate min_pitches input, must be a positive integer or "q"
    if isinstance(min_pitches, int):
        if min_pitches < 1:
            raise ValueError("min_pitches must be a positive integer")
    elif isinstance(min_pitches, str):
        if min_pitches != "q":
            raise ValueError("min_pitches must be a positive integer or 'q'")
    else:
        raise ValueError("min_pitches must be a positive integer or 'q'")
    min_pitches_param = str(min_pitches)

    url = SPIN_DIRECTION_LEADERBOARD_URL.format(
        season=season,
        min_pitches=min_pitches_param,
        pitch_type=pitch_type,
        team_id=team_id_param,
        throws=throws_param,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    df = df.rename({"last_name, first_name": "player_name"})
    return df


def active_spin_leaderboard(
    season: int,  # starts from 2017 to current year
    min_pitches: int = 100,  # >= 1
    stat_method: Literal[
        "spin-based", "observed"
    ] = "spin-based",  # to understand options, there is a writeup here: https://baseballsavant.mlb.com/leaderboard/active-spin, also spin-based is only available from 2020 onwards, observed is available from 2017 onwards
    pitcher_handedness: Literal["R", "L", "ALL"] = "ALL",
):
    # validate season input
    if season < 2017 or season > datetime.now().year:
        raise ValueError(f"season must be between 2017 and {datetime.now().year}")
    # validate min_pitches input
    if min_pitches < 1:
        raise ValueError("min_pitches must be at least 1")
    # validate stat_method input
    if stat_method not in ["spin-based", "observed"]:
        raise ValueError("stat_method must be 'spin-based' or 'observed'")
    if stat_method == "spin-based" and season < 2020:
        raise ValueError("spin-based stat_method is only available from 2020 onwards")
    # validate pitcher_handedness input
    if pitcher_handedness not in ["R", "L", "ALL"]:
        raise ValueError("pitcher_handedness must be 'R', 'L', or 'ALL'")

    throws_param = pitcher_handedness if pitcher_handedness != "ALL" else ""
    url = ACTIVE_SPIN_LEADERBOARD_URL.format(
        season=season,
        stat_method=stat_method,
        min_pitches=min_pitches,
        pitcher_handedness=throws_param,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    df = df.rename({"entity_name": "player_name", "entity_id": "player_id"})
    return df


# TODO: tests for this function
def arm_angle_leaderboard(  # NOTE: ignoring season param because start/end_date filtering is allowed
    start_date: str = "2020-01-01",  # MM-DD-YYYY, 2020-01-01 is the earliest possible start date
    end_date: str = datetime.today().strftime(
        "%Y-%m-%d"
    ),  # MM-DD-YYYY must be after start_date and cannot be in the future
    team: List[StatcastLeaderboardsTeams]
    | None = None,  # 0+ teams, separated by |, if empty then ""
    season_type: List[Literal["R", "WC", "DS", "CS", "WS"]]
    | None = None,  # 0+ season types, separated by |, if empty then "", mappings (R-> R, WC->F, DS->D, CS->L, WS->W)
    pitcher_handedness: Literal["R", "L", "ALL"] = "ALL",  # all maps to ""
    batter_handedness: Literal["R", "L", "ALL"] = "ALL",  # all maps to ""
    pitch_type: List[
        Literal["FF", "SI", "FC", "CH", "FS", "FO", "SC", "CU", "SL", "ST", "SV", "KN"]
    ]
    | None = None,  # 0+ pitch types, separated by |, if empty then ""
    min_pitches: int
    | str = "q",  # must be at least 1 if int, or "q" for qualifying threshold if str
    group_by: List[
        Literal[
            "season", "month", "pitch_type", "game_type", "bat_side", "fielding_team"
        ]
    ]
    | None = None,  # 0-4 group by options, separated by |, if empty then "", options map as follows: season->year, month->api_game_date_month_text, pitch_type->api_pitch_type_group03, game_type->game_type, bat_side->bat_side, fielding_team->fld_team_id
    min_group_size: int = 1,  # must be at least 1, groups smaller than this will be filtered out
):
    # validate date inputs
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("start_date must be in MM-DD-YYYY format")
    try:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("end_date must be in MM-DD-YYYY format")
    if end_date_obj < start_date_obj:
        raise ValueError("end_date must be after start_date")
    if end_date_obj > datetime.today():
        raise ValueError("end_date cannot be in the future")
    # construct season string as all years included in the date range, separated by |, e.g. 2020|2021|2022
    seasons_inferred = "|".join(
        str(year) for year in range(start_date_obj.year, end_date_obj.year + 1)
    )
    # validate team input
    if team is not None:
        if not isinstance(team, list) or not all(
            isinstance(t, StatcastLeaderboardsTeams) for t in team
        ):
            raise ValueError(
                "team must be a list of StatcastLeaderboardsTeams enums or None"
            )
        team_param = "|".join(str(t.value) for t in team)
    else:
        team_param = ""

    # validate season_type input
    season_type_mapping = {
        "R": "R",
        "WC": "F",
        "DS": "D",
        "CS": "L",
        "WS": "W",
    }
    if season_type is not None:
        if not isinstance(season_type, list) or not all(
            st in season_type_mapping for st in season_type
        ):
            raise ValueError(
                f"season_type must be a list of the following options or None: {list(season_type_mapping.keys())}"
            )
        season_type_param = "|".join(season_type_mapping[st] for st in season_type)
    else:
        season_type_param = ""

    # validate pitcher_handedness input
    if pitcher_handedness not in ["R", "L", "ALL"]:
        raise ValueError("pitcher_handedness must be 'R', 'L', or 'ALL'")
    throws_param = pitcher_handedness if pitcher_handedness != "ALL" else ""

    # validate batter_handedness input
    if batter_handedness not in ["R", "L", "ALL"]:
        raise ValueError("batter_handedness must be 'R', 'L', or 'ALL'")
    bat_side_param = batter_handedness if batter_handedness != "ALL" else ""
    # validate pitch_type input
    valid_pitch_types = [
        "FF",
        "SI",
        "FC",
        "CH",
        "FS",
        "FO",
        "SC",
        "CU",
        "SL",
        "ST",
        "SV",
        "KN",
    ]
    if pitch_type is not None:
        if not isinstance(pitch_type, list) or not all(
            pt in valid_pitch_types for pt in pitch_type
        ):
            raise ValueError(
                f"pitch_type must be a list of the following options or None: {valid_pitch_types}"
            )
        pitch_type_param = "|".join(pitch_type)
    else:
        pitch_type_param = ""

    # validate min_pitches input
    if isinstance(min_pitches, int):
        if min_pitches < 1:
            raise ValueError("min_pitches must be at least 1")
        min_pitches_param = str(min_pitches)
    elif isinstance(min_pitches, str):
        if min_pitches != "q":
            raise ValueError("min_pitches must be a positive integer or 'q'")
        min_pitches_param = min_pitches
    else:
        raise ValueError("min_pitches must be a positive integer or 'q'")

    # validate group_by input
    group_by_mapping = {
        "season": "year",
        "month": "api_game_date_month_text",
        "pitch_type": "api_pitch_type_group03",
        "game_type": "game_type",
        "bat_side": "bat_side",
        "fielding_team": "fld_team_id",
    }
    if group_by is not None:
        if not isinstance(group_by, list) or not all(
            gb in group_by_mapping for gb in group_by
        ):
            raise ValueError(
                f"group_by must be a list of the following options or None: {list(group_by_mapping.keys())}"
            )
        if len(group_by) > 4:
            raise ValueError("group_by cannot have more than 4 options")
        group_by_param = "|".join(group_by_mapping[gb] for gb in group_by)
    else:
        group_by_param = ""

    # validate min_group_size input
    if min_group_size < 1:
        raise ValueError("min_group_size must be at least 1")

    url = ARM_ANGLE_LEADERBOARD_URL.format(
        bat_side=bat_side_param,
        start_date=start_date,
        end_date=end_date,
        game_type=season_type_param,
        group_by=group_by_param,
        min_total_pitches=min_pitches_param,
        min_group_size=min_group_size,
        pitch_hand=throws_param,
        pitch_type=pitch_type_param,
        team=team_param,
        seasons_inferred=seasons_inferred,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    if "api_pitch_type_group03" in df.columns:
        df = df.rename({"api_pitch_type_group03": "pitch_type"})
    if "api_game_date_month_text" in df.columns:
        df = df.rename(
            {"api_game_date_month_text": "month", "api_game_date_month_mm": "month_num"}
        )
    return df


# endregion

# if __name__ == "__main__":
#     df = spin_direction_leaderboard(
#         season="ALL",
#         team=StatcastLeaderboardsTeams.ASTROS,
#         pitch_type="FF",
#         pitcher_handedness="R",
#         min_pitches=100,
#     )
#     print(df, df.columns)
