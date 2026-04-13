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
    "standard_batting",
    "value_batting",
    "advanced_batting",
    "sabermetric_batting",
    "ratio_batting",
    "win_probability_batting",
    "baserunning_batting",
    "situational_batting",
    "pitches_batting",
    "career_cumulative_batting",
    "standard_pitching",
    "value_pitching",
    "advanced_pitching",
    "ratio_pitching",
    "batting_against_pitching",
    "win_probability_pitching",
    "starting_pitching",
    "relief_pitching",
    "baserunning_situational_pitching",
    "career_cumulative_pitching",
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
        "career_cumulative",
    ],
) -> pl.DataFrame:

    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
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
        df = df.rename({"name_display": "player"})
    df = df.filter(pl.col("player") != "League Average")
    return df


# region batting functions
def standard_batting(team: BREFTeams, year: int):
    """Return standard team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the page request fails.
        ValueError: If the standard batting table is not found.

    Returns:
        pl.DataFrame: Standard batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    resp = session.get(url)
    if resp is None:
        raise ValueError(f"Failed to fetch data for {team.name} in {year}.")
    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find("table", id="players_standard_batting")
    if table is None:
        raise ValueError(f"No standard batting table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")  # drop index column
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    return df


def value_batting(team: BREFTeams, year: int):
    """Return value team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the value batting table is not found.

    Returns:
        pl.DataFrame: Value batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
    soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_value_batting")
    if table is None:
        raise ValueError(f"No value batting table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")  # drop index column
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))

    return df


def advanced_batting(team: BREFTeams, year: int):
    """Return advanced team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the advanced batting table is not found.

    Returns:
        pl.DataFrame: Advanced batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_advanced_batting")
    if table is None:
        raise ValueError(f"No advanced batting table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")  # drop index column
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))

    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.with_columns(
        pl.col("gperc").alias("gb_perc"),
        pl.col("fperc").alias("fb_perc"),
        pl.col("gfratio").alias("gb_fb_ratio"),
    ).drop(["gperc", "fperc", "gfratio"])
    df = df.filter(pl.col("name_display") != "League Average")
    return df


def sabermetric_batting(team: BREFTeams, year: int):
    """Return sabermetric team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the sabermetric batting table is not found.

    Returns:
        pl.DataFrame: Sabermetric batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_sabermetric_batting")
    if table is None:
        raise ValueError(
            f"No sabermetric batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    return df


def ratio_batting(team: BREFTeams, year: int):
    """Return ratio team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the ratio batting table is not found.

    Returns:
        pl.DataFrame: Ratio batting table with typed numeric and percent columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_ratio_batting")
    if table is None:
        raise ValueError(f"No ratio batting table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    return df


def win_probability_batting(team: BREFTeams, year: int):
    """Return win-probability team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the win probability batting table is not found.

    Returns:
        pl.DataFrame: Win probability batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_win_probability_batting")
    if table is None:
        raise ValueError(
            f"No win probability batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    return df


def baserunning_batting(team: BREFTeams, year: int):
    """Return baserunning team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the baserunning batting table is not found.

    Returns:
        pl.DataFrame: Baserunning batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_baserunning_batting")
    if table is None:
        raise ValueError(
            f"No baserunning batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    # df = df.drop("ranker")  # drop index column
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    return df


def situational_batting(team: BREFTeams, year: int):
    """Return situational team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the situational batting table is not found.

    Returns:
        pl.DataFrame: Situational batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_situational_batting")
    if table is None:
        raise ValueError(
            f"No situational batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    return df


def pitches_batting(team: BREFTeams, year: int):
    """Return pitches/plate-discipline team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the pitches batting table is not found.

    Returns:
        pl.DataFrame: Pitches batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_pitches_batting")
    if table is None:
        raise ValueError(f"No pitches batting table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    return df


def career_cumulative_batting(team: BREFTeams, year: int):
    """Return cumulative career batting summaries for the team roster.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the cumulative batting table is not found.

    Returns:
        pl.DataFrame: Cumulative batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_cumulative_batting")
    if table is None:
        raise ValueError(
            f"No cumulative batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    return df


# endregion

# region pitching functions


def standard_pitching(team: BREFTeams, year: int):
    """Return standard team pitching statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the page request fails.
        ValueError: If the standard pitching table is not found.
    Returns:
        pl.DataFrame: Standard pitching table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_PITCHING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    resp = session.get(url)
    if resp is None:
        raise ValueError(f"Failed to fetch data for {team.name} in {year}.")
    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find("table", id="players_standard_pitching")
    if table is None:
        raise ValueError(f"No standard pitching table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")  # drop index column
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("p_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    return df


def value_pitching(team: BREFTeams, year: int):
    """Return value team pitching statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the value pitching table is not found.
    Returns:
        pl.DataFrame: Value pitching table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_PITCHING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_value_pitching")
    if table is None:
        raise ValueError(f"No value pitching table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")  # drop index column
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("p_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    return df


def advanced_pitching(team: BREFTeams, year: int):
    """Return advanced team pitching statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the advanced pitching table is not found.
    Returns:
        pl.DataFrame: Advanced pitching table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_PITCHING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_advanced_pitching")
    if table is None:
        raise ValueError(f"No advanced pitching table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")  # drop index column
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("p_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    return df


def ratio_pitching(team: BREFTeams, year: int):
    """Return ratio team pitching statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the ratio pitching table is not found.
    Returns:
        pl.DataFrame: Ratio pitching table with typed numeric and percent columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_PITCHING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_ratio_pitching")
    if table is None:
        raise ValueError(f"No ratio pitching table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("p_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))

    df = df.filter(pl.col("player") != "League Average")
    return df


def batting_against_pitching(team: BREFTeams, year: int):
    """Return team pitching against batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the pitching against batting table is not found.
    Returns:
        pl.DataFrame: Pitching against batting table with typed numeric columns.
    """

    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_PITCHING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_batting_pitching")
    if table is None:
        raise ValueError(
            f"No pitching against batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("p_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.drop("PA_unknown")
    df = df.filter(pl.col("player") != "League Average")
    return df


def win_probability_pitching(team: BREFTeams, year: int):
    """Return team pitching win probability statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the pitching win probability table is not found.
    Returns:
        pl.DataFrame: Pitching win probability table with typed numeric columns.
    """

    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_PITCHING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_win_probability_pitching")
    if table is None:
        raise ValueError(
            f"No pitching win probability table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("p_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    return df


def starting_pitching(team: BREFTeams, year: int):
    """Return team starting pitching statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the starting pitching table is not found.
    Returns:
        pl.DataFrame: Starting pitching table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_PITCHING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_starter_pitching")
    if table is None:
        raise ValueError(f"No starting pitching table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("p_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    return df


def relief_pitching(team: BREFTeams, year: int):
    """Return team relief pitching statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the relief pitching table is not found.
    Returns:
        pl.DataFrame: Relief pitching table with typed numeric columns.
    """

    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_PITCHING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_reliever_pitching")
    if table is None:
        raise ValueError(f"No relief pitching table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("p_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    return df


def baserunning_situational_pitching(team: BREFTeams, year: int):
    """Return team pitching baserunning statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the pitching baserunning table is not found.
    Returns:
        pl.DataFrame: Pitching baserunning table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_PITCHING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_basesituation_pitching")
    if table is None:
        raise ValueError(
            f"No pitching baserunning table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("p_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    return df


def career_cumulative_pitching(team: BREFTeams, year: int):
    """Return cumulative career pitching summaries for the team roster.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.
    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the cumulative pitching table is not found.
    Returns:
        pl.DataFrame: Cumulative pitching table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_PITCHING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_cumulative_pitching")
    if table is None:
        raise ValueError(
            f"No cumulative pitching table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    # this table exposes a duplicated era column in the markup, which produces mismatched column lengths from raw extraction
    # to work around this, we extract manually and normalize lengths to the player column length, keeping one of the duplicated columns if necessary
    reference_row_count = len(data.get("player", []))
    normalized_data: dict[str, list[str | int | float | None]] = {}
    for column_name, series in data.items():
        values = series.to_list()

        if (
            column_name == "earned_run_avg_plus"
            and reference_row_count > 0
            and len(values) == reference_row_count * 2
        ):
            # Keep one value per player row.
            values = values[::2]

        if reference_row_count > 0:
            if len(values) > reference_row_count:
                values = values[:reference_row_count]
            elif len(values) < reference_row_count:
                values = values + [None] * (reference_row_count - len(values))

        normalized_data[column_name] = values

    df = pl.DataFrame(normalized_data)
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
