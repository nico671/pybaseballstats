import re
from datetime import datetime
from typing import Literal

import polars as pl
from bs4 import BeautifulSoup

from pybaseballstats.consts.bref_consts import (
    BREF_TEAMS_BATTING_BASE_URL,
    BREF_TEAMS_FIELDING_BASE_URL,
    BREF_TEAMS_PITCHING_BASE_URL,
    BREF_TEAMS_ROSTER_URL,
    BREF_TEAMS_SCHEDULE_RESULTS_URL,
    BREFTeams,
)
from pybaseballstats.utils.bref_utils import (
    BREFSession,
    _extract_table,
    _goto_and_get_stable_html,
    resolve_bref_team_code,
)

session = BREFSession.instance()  # type: ignore[attr-defined]

__all__ = [
    "BREFTeams",
    "game_by_game_schedule_results",
    "roster_and_appearances",
    "batting_orders",
    "batting",
    "pitching",
    "fielding",
]


# region random functions


def batting_orders(team: BREFTeams, year: int) -> pl.DataFrame:
    """Return a per-game batting-orders table for a team season.

    The function extracts the Baseball Reference table with class ``grid_table``
    and caption ``Batting Orders`` from the team page:
    ``https://www.baseball-reference.com/teams/{team_code}/{year}-batting-orders.shtml``.

    Each returned row represents one game and includes:
    - game metadata: game number, game date, home/away, W/L result, final score,
            and whether the opposing starting pitcher was left-handed (``#`` marker)
        - opponent details: opponent team code and opposing starter name (when present)
    - batting-order slots: for each slot 1 through 9, the player name and the
      defensive position listed for that player

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the page request fails.
        ValueError: If the batting-orders grid table is not found.

    Returns:
        pl.DataFrame: Per-game batting orders with metadata and lineup columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    if year < 1871:
        raise ValueError("Year must be greater than or equal to 1871.")

    team_code = resolve_bref_team_code(team=team, year=year)
    url = f"https://www.baseball-reference.com/teams/{team_code}/{year}-batting-orders.shtml"
    resp = session.get(url)
    if resp is None:
        raise ValueError(f"Failed to fetch batting orders for {team.name} in {year}.")

    soup = BeautifulSoup(resp.content, "html.parser")

    table = None
    for candidate in soup.find_all("table", class_="grid_table"):
        caption = candidate.find("caption")
        if caption and "Batting Orders" in caption.get_text(strip=True):
            table = candidate
            break

    if table is None or table.tbody is None:
        raise ValueError(
            f"No batting-orders grid table found for {team.name} in {year}."
        )

    inning_slots = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th"]
    rows: list[dict[str, str | int | bool | None]] = []

    for tr in table.tbody.find_all("tr"):
        header_cell = tr.find("th", {"data-stat": "header"})
        if header_cell is None:
            continue

        header_text = " ".join(header_cell.stripped_strings)
        if header_text.startswith("Game ("):
            continue

        game_number_match = re.search(r"^(\d+)\.", header_text)
        result_match = re.search(r"\b([WL])\s*\(", header_text)
        score_match = re.search(r"\((\d+-\d+)\)", header_text)

        game_number = int(game_number_match.group(1)) if game_number_match else None
        result = result_match.group(1) if result_match else None
        final_score = score_match.group(1) if score_match else None

        home_or_away: str | None = None
        if " vs " in header_text:
            home_or_away = "home"
        elif " at " in header_text:
            home_or_away = "away"

        date_text = None
        date_link = header_cell.find("a", href=re.compile(r"^/boxes/"))
        if date_link is not None:
            date_text = date_link.get_text(strip=True)

        game_date_iso: str | None = None
        if date_text is not None:
            try:
                parsed_date = datetime.strptime(f"{year} {date_text}", "%Y %a,%m/%d")
                game_date_iso = parsed_date.date().isoformat()
            except ValueError:
                game_date_iso = date_text

        opponent_code: str | None = None
        opponent_link = header_cell.find(
            "a", href=re.compile(r"^/teams/.+?-batting-orders\.shtml")
        )
        if opponent_link is not None:
            opponent_code = opponent_link.get_text(strip=True) or None

        opposing_starter_name: str | None = None
        if date_link is not None:
            starter_title = str(date_link.get("title"))
            if starter_title:
                starter_match = re.search(r"facing:\s*(.+)$", starter_title)
                opposing_starter_name = (
                    starter_match.group(1).strip()
                    if starter_match
                    else starter_title.strip()
                )

        row: dict[str, str | int | bool | None] = {
            "game_number": game_number,
            "game_date": game_date_iso,
            "home_or_away": home_or_away,
            "opponent_code": opponent_code,
            "result": result,
            "won": result == "W" if result is not None else None,
            "final_score": final_score,
            "opposing_starter_left_handed": header_text.endswith("#"),
            "opposing_starter_name": opposing_starter_name,
        }

        for idx, slot in enumerate(inning_slots, start=1):
            batting_cell = tr.find("td", {"data-stat": slot})
            player_name: str | None = None
            field_position: str | None = None

            if batting_cell is not None:
                player_link = batting_cell.find("a")
                if player_link is not None:
                    player_name = str(player_link.get("title")) or player_link.get_text(
                        strip=True
                    )

                position_tag = batting_cell.find("small")
                if position_tag is not None:
                    field_position = position_tag.get_text(strip=True).lstrip("-")

            row[f"batting_{idx}_player"] = player_name
            row[f"batting_{idx}_field_pos"] = field_position

        rows.append(row)

    return pl.DataFrame(rows)


def game_by_game_schedule_results(team: BREFTeams, year: int) -> pl.DataFrame:
    """Return game-by-game schedule/results for a team season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the page request fails.
        ValueError: If the schedule/results table is not found.

    Returns:
        pl.DataFrame: Team schedule and results rows from Baseball Reference.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    team_code = resolve_bref_team_code(team=team, year=year)
    url = BREF_TEAMS_SCHEDULE_RESULTS_URL.format(team_code=team_code, year=year)
    resp = session.get(url)
    if resp is None:
        raise ValueError(f"Failed to fetch data for {team.name} in {year}.")

    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find("table", id="team_schedule")
    if table is None:
        raise ValueError(f"No schedule/results table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop(
        "boxscore"
    )  # drop boxscore column since it just has a link to the boxscore page which isn't useful for our purposes
    return df


def roster_and_appearances(team: BREFTeams, year: int) -> pl.DataFrame:
    """Return roster and appearances data for a team season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        AssertionError: If the roster/appearances table is not found.

    Returns:
        pl.DataFrame: Team roster and appearances rows from Baseball Reference.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    team_code = resolve_bref_team_code(team=team, year=year)
    with session.get_page() as page:
        content = _goto_and_get_stable_html(
            page,
            BREF_TEAMS_ROSTER_URL.format(team_code=team_code, year=year),
        )
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="appearances")
    assert table is not None, (
        f"No roster/appearances table found for {team.name} in {year}."
    )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")
    return df


# endregion


# region batting functions
def batting(
    team: BREFTeams,
    year: int,
    metric_type: Literal[
        "standard",
        "value",
        "advanced",
        "sabermetric",
        "ratio",
        "win_probability",
        "baserunning",
        "situational",
        "pitches",
        "cumulative",
    ] = "standard",
) -> pl.DataFrame:
    """Return team batting statistics for one season and metric family.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
        metric_type (Literal[...], optional): Batting table family to fetch.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If ``metric_type`` is not supported.
        ValueError: If ``year`` is before 1871.
        ValueError: If the requested batting table is not found.

    Returns:
        pl.DataFrame: Requested batting table with normalized column names.
    """

    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    if metric_type not in [
        "standard",
        "value",
        "advanced",
        "sabermetric",
        "ratio",
        "win_probability",
        "baserunning",
        "situational",
        "pitches",
        "cumulative",
    ]:
        raise ValueError(
            "Invalid metric type. Must be one of: 'standard', 'value', 'advanced', 'sabermetric', 'ratio', 'win_probability', 'baserunning', 'situational', 'pitches', 'cumulative'."
        )
    if year < 1871:
        raise ValueError("Year must be greater than or equal to 1871.")

    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        content = _goto_and_get_stable_html(page, url)
        soup = BeautifulSoup(content, "html.parser")
    table_id = f"players_{metric_type}_batting"
    table = soup.find("table", id=table_id)
    if table is None:
        raise ValueError(
            f"No {metric_type} batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    if "ranker" in df.columns:
        df = df.drop("ranker")  # drop index column
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    if "name_display" in df.columns:
        df = df.rename({"name_display": "player_name"})
    if "player" in df.columns:
        df = df.rename({"player": "player_name"})
    df = df.filter(pl.col("player_name") != "League Average")
    return df


# endregion

# region pitching functions


def pitching(
    team: BREFTeams,
    year: int,
    metric_type: Literal[
        "standard",
        "value",
        "advanced",
        "ratio",
        "batting_against",
        "win_probability",
        "starting",
        "relief",
        "baserunning_situational",
        "cumulative",
    ] = "standard",
) -> pl.DataFrame:
    """Return team pitching statistics for one season and metric family.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
        metric_type (Literal[...], optional): Pitching table family to fetch.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If ``metric_type`` is not supported.
        ValueError: If ``year`` is before 1871.
        ValueError: If the requested pitching table is not found.

    Returns:
        pl.DataFrame: Requested pitching table with normalized column names.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    if metric_type not in [
        "standard",
        "value",
        "advanced",
        "ratio",
        "batting_against",
        "win_probability",
        "starting",
        "relief",
        "baserunning_situational",
        "cumulative",
    ]:
        raise ValueError(
            "Invalid metric type. Must be one of: 'standard', 'value', 'advanced', 'ratio', 'batting_against', 'win_probability', 'starting', 'relief', 'baserunning_situational', 'cumulative'."
        )
    if year < 1871:
        raise ValueError("Year must be greater than or equal to 1871.")

    table_ids = {
        "standard": "players_standard_pitching",
        "value": "players_value_pitching",
        "advanced": "players_advanced_pitching",
        "ratio": "players_ratio_pitching",
        "batting_against": "players_batting_pitching",
        "win_probability": "players_win_probability_pitching",
        "starting": "players_starter_pitching",
        "relief": "players_reliever_pitching",
        "baserunning_situational": "players_basesituation_pitching",
        "cumulative": "players_cumulative_pitching",
    }

    table_id = table_ids[metric_type]

    url = BREF_TEAMS_PITCHING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        content = _goto_and_get_stable_html(page, url)
        soup = BeautifulSoup(content, "html.parser")

    table = soup.find("table", id=table_id)
    if table is None:
        raise ValueError(
            f"No {metric_type} pitching table found for {team.name} in {year}."
        )

    data = _extract_table(table)
    if metric_type == "cumulative":
        # This table exposes duplicated columns in markup, so normalize all
        # extracted columns to the row count of the player column.
        reference_row_count = len(data.get("player", []))
        normalized_data: dict[str, list[str | int | float | None]] = {}
        for column_name, series in data.items():
            values = series.to_list()

            if (
                column_name == "earned_run_avg_plus"
                and reference_row_count > 0
                and len(values) == reference_row_count * 2
            ):
                values = values[::2]

            if reference_row_count > 0:
                if len(values) > reference_row_count:
                    values = values[:reference_row_count]
                elif len(values) < reference_row_count:
                    values = values + [None] * (reference_row_count - len(values))

            normalized_data[column_name] = values

        df = pl.DataFrame(normalized_data)
    else:
        df = pl.DataFrame(data)

    if "ranker" in df.columns:
        df = df.drop("ranker")

    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("p_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))

    if "PA_unknown" in df.columns:
        df = df.drop("PA_unknown")

    if "name_display" in df.columns:
        df = df.rename({"name_display": "player_name"})
    if "player" in df.columns:
        df = df.rename({"player": "player_name"})

    if "player_name" in df.columns:
        df = df.filter(pl.col("player_name") != "League Average")

    return df


# endregion


# region fielding functions
def fielding(
    team: BREFTeams,
    year: int,
    metric_type: Literal["standard", "advanced"],
    position: Literal[
        "",
        "all",
        "c",
        "1b",
        "2b",
        "3b",
        "ss",
        "lf",
        "cf",
        "rf",
        "of",
        "p",
        "dh",
        "c_baserunning",
    ] = "",
) -> pl.DataFrame:
    """Return team fielding statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
        metric_type (Literal["standard", "advanced"]): Metric family to fetch.
        position (Literal[...], optional): Position table selector.
            - For ``metric_type="standard"``: ``""`` or ``"all"`` (all fielders),
              ``"c"``, ``"1b"``, ``"2b"``, ``"3b"``, ``"ss"``, ``"lf"``,
              ``"cf"``, ``"rf"``, ``"of"``, ``"p"``, ``"dh"``.
            - For ``metric_type="advanced"``: ``"c"``, ``"c_baserunning"``,
              ``"1b"``, ``"2b"``, ``"3b"``, ``"ss"``, ``"lf"``, ``"cf"``,
              ``"rf"``, ``"p"``.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If ``metric_type`` is invalid.
        ValueError: If ``position`` is invalid for the selected metric type.
        ValueError: If the requested fielding table is not found.

    Returns:
        pl.DataFrame: Requested fielding table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")

    standard_table_ids = {
        "": "players_standard_fielding",
        "all": "players_standard_fielding",
        "c": "players_standard_fielding_c",
        "1b": "players_standard_fielding_1b",
        "2b": "players_standard_fielding_2b",
        "3b": "players_standard_fielding_3b",
        "ss": "players_standard_fielding_ss",
        "lf": "players_standard_fielding_lf",
        "cf": "players_standard_fielding_cf",
        "rf": "players_standard_fielding_rf",
        "of": "players_standard_fielding_of",
        "p": "players_standard_fielding_p",
        "dh": "players_DH_games",
    }
    advanced_table_ids = {
        "c": "players_advanced_fielding_c",
        "c_baserunning": "players_advanced_fielding_c_baserunning",
        "1b": "players_advanced_fielding_1b",
        "2b": "players_advanced_fielding_2b",
        "3b": "players_advanced_fielding_3b",
        "ss": "players_advanced_fielding_ss",
        "lf": "players_advanced_fielding_lf",
        "cf": "players_advanced_fielding_cf",
        "rf": "players_advanced_fielding_rf",
        "p": "players_advanced_fielding_p",
    }

    if metric_type not in {"standard", "advanced"}:
        raise ValueError("metric_type must be either 'standard' or 'advanced'")

    if metric_type == "standard":
        if position not in standard_table_ids:
            valid_standard_positions = ", ".join(
                repr(pos) for pos in standard_table_ids
            )
            raise ValueError(
                "Invalid position for standard fielding. "
                f"Valid values are: {valid_standard_positions}."
            )
        table_id = standard_table_ids[position]
    else:
        if position in {"", "all"}:
            raise ValueError(
                "Position ''/'all' is only valid for standard fielding; "
                "advanced fielding does not have an all-positions table."
            )
        if position not in advanced_table_ids:
            valid_advanced_positions = ", ".join(
                repr(pos) for pos in advanced_table_ids
            )
            raise ValueError(
                "Invalid position for advanced fielding. "
                f"Valid values are: {valid_advanced_positions}."
            )
        table_id = advanced_table_ids[position]

    url = BREF_TEAMS_FIELDING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        content = _goto_and_get_stable_html(page, url)
        soup = BeautifulSoup(content, "html.parser")

    table = soup.find("table", id=table_id)
    if table is None:
        raise ValueError(
            f"No {metric_type} fielding table '{table_id}' found for {team.name} in {year}."
        )

    data = _extract_table(table)
    df = pl.DataFrame(data)

    if "ranker" in df.columns:
        df = df.drop("ranker")

    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("f_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    return df


# endregion
