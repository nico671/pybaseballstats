import polars as pl
from bs4 import BeautifulSoup

from pybaseballstats.consts.bref_consts import (
    BREF_TEAMS_ROSTER_URL,
    BREF_TEAMS_SCHEDULE_RESULTS_URL,
    BREFTeams,
    resolve_bref_team_code,
)
from pybaseballstats.utils.bref_utils import BREFSession, _extract_table

session = BREFSession.instance()  # type: ignore[attr-defined]

__all__ = ["BREFTeams", "game_by_game_schedule_results", "roster_and_appearances"]


def game_by_game_schedule_results(team: BREFTeams, year: int) -> pl.DataFrame:
    """Returns a dataframe of game by game results for a given MLB team in a given season

    Args:
        team (BREFTeams): The team for which to fetch the schedule and results. This should be a member of the BREFTeams enum, which contains the valid team codes used by Baseball Reference.
        year (int): The year for which to fetch the schedule and results. This should be a valid MLB season year (e.g., 2020, 2021, etc.).

    Raises:
        ValueError: If the team parameter is not a valid member of the BREFTeams enum, a ValueError is raised indicating that the team code is invalid and must be one of the defined enum members.
        ValueError: If the data cannot be fetched or parsed correctly, a ValueError is raised with an appropriate message. This can occur if the team code or year is invalid, if the structure of the webpage has changed, or if there are network issues preventing access to the page.
        ValueError: If the schedule/results table cannot be found on the page, a ValueError is raised indicating that the expected table structure may have changed or that the team/year combination is invalid.

    Returns:
        pl.DataFrame: A Polars DataFrame containing the game by game schedule and results for the specified team and year. The DataFrame includes columns such as date, opponent, home/away status, runs scored, runs allowed, and other relevant game information as extracted from the Baseball Reference page.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    team_code = resolve_bref_team_code(team=team, year=year)
    url = BREF_TEAMS_SCHEDULE_RESULTS_URL.format(team_code=team_code, year=year)
    resp = session.get(url)
    if resp is None:
        print(url)
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
    """Returns a dataframe of the roster and appearances for a given MLB team in a given season

    Args:
        team (BREFTeams): The team for which to fetch the roster and appearances. This should be a member of the BREFTeams enum, which contains the valid team codes used by Baseball Reference.
        year (int): The year for which to fetch the roster and appearances. This should be a valid MLB season year (e.g., 2020, 2021, etc.).

    Raises:
        ValueError: If the data cannot be fetched or parsed correctly, a ValueError is raised with an appropriate message. This can occur if the team code or year is invalid, if the structure of the webpage has changed, or if there are network issues preventing access to the page.
        ValueError: If the roster/appearances table cannot be found on the page, a ValueError is raised indicating that the expected table structure may have changed or that the team/year combination is invalid.
    Returns:
        pl.DataFrame: A Polars DataFrame containing the roster and appearances for the specified team and year. The DataFrame includes columns such as player name, position, games played, and other relevant information as extracted from the Baseball Reference page.
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
    print(
        BREF_TEAMS_ROSTER_URL.format(team_code=team_code, year=year),
    )
    table = soup.find("table", id="appearances")
    assert table is not None, (
        f"No roster/appearances table found for {team.name} in {year}."
    )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")
    return df


if __name__ == "__main__":
    df = roster_and_appearances(team=BREFTeams.ANGELS, year=2023)
    print(
        df,
        df.columns,
        df.with_columns(pl.col("games_started_all").cast(pl.Int64))
        .select(pl.col("games_started_all").max())
        .item(),
    )
