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
    resolve_bref_team_code,
)

session = BREFSession.instance()  # type: ignore[attr-defined]

__all__ = [
    "BREFTeams",
    "game_by_game_schedule_results",
    "roster_and_appearances",
    "batting",
    "pitching",
    "fielding",
]


# TODO: def lineups, batting orders
# region random functions


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
        page.goto(
            BREF_TEAMS_ROSTER_URL.format(team_code=team_code, year=year),
        )
        # page.wait_for_selector("#appearances > tbody")
        content = page.content()
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
        page.goto(url, wait_until="networkidle")
        content = page.content()
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
        page.goto(url, wait_until="networkidle")
        content = page.content()
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
        page.goto(url, wait_until="networkidle")
        content = page.content()
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

if __name__ == "__main__":
    df = pitching(team=BREFTeams.YANKEES, year=2025, metric_type="cumulative")
    print(df, df.columns, df.select(pl.col("W").max()).item())
