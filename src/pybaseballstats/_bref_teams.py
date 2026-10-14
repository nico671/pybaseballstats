import re
from datetime import datetime
from typing import Literal

import polars as pl
from bs4 import BeautifulSoup

from pybaseballstats._consts.bref_consts import (
    BREF_TEAMS_BATTING_BASE_URL,
    BREF_TEAMS_FIELDING_BASE_URL,
    BREF_TEAMS_PITCHING_BASE_URL,
    BREF_TEAMS_ROSTER_URL,
    BREF_TEAMS_SCHEDULE_RESULTS_URL,
    BREFTeams,
)
from pybaseballstats._utils.bref_utils import (
    _extract_table,
    _required_table,
    _source_schema_errors,
    resolve_bref_team_code,
)
from pybaseballstats._utils.session_utils import BREF_SESSION as session

__all__ = [
    "BREFTeams",
    "game_by_game_schedule_results",
    "roster_and_appearances",
    "batting_orders",
    "batting",
    "pitching",
    "fielding",
]


def _check_team_year(team: BREFTeams, year: int) -> None:
    if not isinstance(team, BREFTeams):
        raise TypeError("team must be a BREFTeams value")
    if type(year) is not int:
        raise TypeError("year must be an integer")
    if year < 1871:
        raise ValueError("year must be at least 1871")


# region random functions


@_source_schema_errors
def batting_orders(team: BREFTeams, year: int, verbose: bool = False) -> pl.DataFrame:
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
        TypeError: If ``team`` is not a ``BREFTeams`` value.
        RuntimeError: If the page request fails.
        RuntimeError: If the batting-orders grid table is not found.

    Returns:
        pl.DataFrame: Per-game batting orders with metadata and lineup columns.
    """
    _check_team_year(team, year)

    team_code = resolve_bref_team_code(team=team, year=year)
    url = f"https://www.baseball-reference.com/teams/{team_code}/{year}-batting-orders.shtml"
    resp = session.get(url, verbose=verbose)

    soup = BeautifulSoup(resp.content, "html.parser")

    table = None
    for candidate in soup.find_all("table", class_="grid_table"):
        caption = candidate.find("caption")
        if caption and "Batting Orders" in caption.get_text(strip=True):
            table = candidate
            break

    if table is None or table.tbody is None:
        raise RuntimeError(
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


@_source_schema_errors
def game_by_game_schedule_results(
    team: BREFTeams, year: int, verbose: bool = False
) -> pl.DataFrame:
    """Return game-by-game schedule/results for a team season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
        verbose (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.

    Raises:
        TypeError: If ``team`` is not a ``BREFTeams`` value.
        RuntimeError: If the page request fails.
        RuntimeError: If the schedule/results table is not found.

    Returns:
        pl.DataFrame: Team schedule and results rows from Baseball Reference.
    """
    _check_team_year(team, year)
    team_code = resolve_bref_team_code(team=team, year=year)
    url = BREF_TEAMS_SCHEDULE_RESULTS_URL.format(team_code=team_code, year=year)
    resp = session.get(url, verbose=verbose)

    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find("table", id="team_schedule")
    if table is None:
        raise RuntimeError(
            f"No schedule/results table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop(
        "boxscore"
    )  # drop boxscore column since it just has a link to the boxscore page which isn't useful for our purposes
    return df


@_source_schema_errors
def roster_and_appearances(
    team: BREFTeams, year: int, verbose: bool = False
) -> pl.DataFrame:
    """Return roster and appearances data for a team season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
        verbose (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.

    Raises:
        TypeError: If ``team`` is not a ``BREFTeams`` value.
        RuntimeError: If the roster/appearances table is not found.

    Returns:
        pl.DataFrame: Team roster and appearances rows from Baseball Reference.
    """
    _check_team_year(team, year)
    team_code = resolve_bref_team_code(team=team, year=year)
    url = BREF_TEAMS_ROSTER_URL.format(team_code=team_code, year=year)
    resp = session.get(url, verbose=verbose)
    df = _required_table(resp.text, "appearances", "roster_and_appearances")
    df = df.drop("ranker")
    return df


# endregion


# region batting functions
@_source_schema_errors
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
    verbose: bool = False,
) -> pl.DataFrame:
    """Return team batting statistics for one season and metric family.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
        metric_type (Literal[...], optional): Batting table family to fetch.
            Supported metric families are ``"standard"``, ``"value"``, ``"advanced"``,
            ``"sabermetric"``, ``"ratio"``, ``"win_probability"``, ``"baserunning"``,
            ``"situational"``, ``"pitches"``, and ``"cumulative"``.
        verbose: (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.

    Raises:
        TypeError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If ``metric_type`` is not supported.
        ValueError: If ``year`` is before 1871.
        RuntimeError: If the requested batting table is not found.

    Returns:
        pl.DataFrame: Requested batting table with normalized column names.
    """

    _check_team_year(team, year)
    if not isinstance(metric_type, str):
        raise TypeError("metric_type must be a string")
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

    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    table_id = f"players_{metric_type}_batting"
    resp = session.get(url, verbose=verbose)
    df = _required_table(resp.text, table_id, "batting")
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


@_source_schema_errors
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
    verbose: bool = False,
) -> pl.DataFrame:
    """Return team pitching statistics for one season and metric family.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
        metric_type (Literal[...], optional): Pitching table family to fetch.
            Supported metric families are ``"standard"``, ``"value"``, ``"advanced"``,
            ``"ratio"``, ``"batting_against"``, ``"win_probability"``, ``"starting"``,
            ``"relief"``, ``"baserunning_situational"``, and ``"cumulative"``.
        verbose: (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.

    Raises:
        TypeError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If ``metric_type`` is not supported.
        ValueError: If ``year`` is before 1871.
        RuntimeError: If the requested pitching table is not found.

    Returns:
        pl.DataFrame: Requested pitching table with normalized column names.
    """
    _check_team_year(team, year)
    if not isinstance(metric_type, str):
        raise TypeError("metric_type must be a string")
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
    resp = session.get(url, verbose=verbose)
    df = _required_table(resp.text, table_id, "pitching")

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
@_source_schema_errors
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
    verbose: bool = False,
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
        verbose (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.

    Raises:
        TypeError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If ``metric_type`` is invalid.
        ValueError: If ``position`` is invalid for the selected metric type.
        RuntimeError: If the requested fielding table is not found.

    Returns:
        pl.DataFrame: Requested fielding table with typed numeric columns.
    """
    _check_team_year(team, year)
    if not isinstance(metric_type, str):
        raise TypeError("metric_type must be a string")
    if not isinstance(position, str):
        raise TypeError("position must be a string")

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
    resp = session.get(url, verbose=verbose)
    df = _required_table(resp.text, table_id, "fielding")

    if "ranker" in df.columns:
        df = df.drop("ranker")

    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("f_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    return df


# endregion
