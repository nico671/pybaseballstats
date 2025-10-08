import polars as pl
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pybaseballstats.consts.bref_consts import (
    BREF_TEAM_BATTING_URL,
    BREF_TEAM_RECORD_URL,
    BREFTeams,
)
from pybaseballstats.utils.bref_utils import (
    BREFSession,
    _extract_table,
    fetch_page_html,
)

session = BREFSession.instance()


def team_standard_batting(
    team: BREFTeams,
    year: int,
) -> pl.DataFrame:
    """Returns a DataFrame of team standard batting data for a given year. NOTE: This function uses Selenium to scrape the data, so it may be slow.

    Args:
        team (BREFTeams): Which team to pull data from. Use the BREFTeams enum to get the correct team code. You can use the show_options() method to see all available teams.
        year (int): Which year to pull data from

    Returns:
        pl.DataFrame: A Polars DataFrame of team standard batting data for the given year.
    """
    with session.get_driver() as driver:
        driver.get(BREF_TEAM_BATTING_URL.format(team_code=team.value, year=year))
        wait = WebDriverWait(driver, 15)
        team_standard_batting_table_wrapper = wait.until(
            EC.presence_of_element_located((By.ID, "div_players_standard_batting"))
        )
        soup = BeautifulSoup(
            team_standard_batting_table_wrapper.get_attribute("outerHTML"),
            "html.parser",
        )
    team_standard_batting_table = soup.find("table")
    team_standard_batting_df = pl.DataFrame(
        _extract_table(team_standard_batting_table), infer_schema_length=None
    )

    team_standard_batting_df = team_standard_batting_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("b_", ""))
    )

    team_standard_batting_df = team_standard_batting_df.rename(
        {"name_display": "player_name"}
    )
    team_standard_batting_df = team_standard_batting_df.with_columns(
        pl.col(
            [
                "age",
                "hbp",
                "ibb",
                "sh",
                "sf",
                "games",
                "pa",
                "ab",
                "r",
                "h",
                "doubles",
                "triples",
                "hr",
                "rbi",
                "sb",
                "cs",
                "bb",
                "so",
                "onbase_plus_slugging_plus",
                "rbat_plus",
                "tb",
                "gidp",
            ]
        ).cast(pl.Int32),
        pl.col(
            [
                "war",
                "batting_avg",
                "onbase_perc",
                "slugging_perc",
                "onbase_plus_slugging",
                "roba",
            ]
        ).cast(pl.Float32),
    )
    return team_standard_batting_df


def team_value_batting(
    team: BREFTeams,
    year: int,
) -> pl.DataFrame:
    """Return a DataFrame of team value batting data for a given year. NOTE: This function uses Selenium to scrape the data, so it may be slow.

    Args:
        team (BREFTeams): Which team to pull data from. Use the BREFTeams enum to get the correct team code. You can use the show_options() method to see all available teams.
        year (int): Which year to pull data from

    Returns:
        pl.DataFrame: A Polars DataFrame of team value batting data for the given year.
    """
    with session.get_driver() as driver:
        driver.get(
            BREF_TEAM_BATTING_URL.format(team_code=BREFTeams.NATIONALS.value, year=2024)
        )
        wait = WebDriverWait(driver, 15)
        team_value_batting_table_wrapper = wait.until(
            EC.presence_of_element_located((By.ID, "div_players_value_batting"))
        )
        soup = BeautifulSoup(
            team_value_batting_table_wrapper.get_attribute("outerHTML"), "html.parser"
        )
    team_value_batting_table = soup.find("table")
    team_value_batting_df = pl.DataFrame(
        _extract_table(team_value_batting_table), infer_schema_length=None
    )
    team_value_batting_df = team_value_batting_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("b_", ""))
    )

    team_value_batting_df = team_value_batting_df.rename(
        {"name_display": "player_name"}
    )

    team_value_batting_df = team_value_batting_df.with_columns(
        pl.col(
            [
                "age",
                "pa",
                "runs_batting",
                "runs_baserunning",
                "runs_double_plays",
                "runs_fielding",
                "runs_position",
                "raa",
                "runs_replacement",
                "rar",
                "rar_off",
            ]
        ).cast(pl.Int32),
        pl.col(
            ["waa", "war", "waa_win_perc", "waa_win_perc_162", "war_off", "war_def"]
        ).cast(pl.Float32),
    )
    return team_value_batting_df


def bref_teams_yearly_history(
    team: BREFTeams,
    start_season: int = None,
    end_season: int = None,
) -> pl.DataFrame:
    """Returns a DataFrame of franchise history data for a given team.

    Args:
        team (BREFTeams): The team to get data for.
        start_season (int, optional): The start season to filter by. Defaults to None.
        end_season (int, optional): The end season to filter by. Defaults to None.

    Raises:
        ValueError: _description_

    Returns:
        pl.DataFrame: _description_
    """
    if team is None:
        raise ValueError("Must provide a team")
    html = fetch_page_html(BREF_TEAM_RECORD_URL.format(team_code=team.value))
    soup = BeautifulSoup(html, "html.parser")
    franch_history_table = soup.find("table", {"id": "franchise_years"})
    df = pl.DataFrame(_extract_table(franch_history_table))
    df = df.with_columns(
        [
            pl.col(
                [
                    "G",
                    "W",
                    "L",
                    "ties",
                    "R",
                    "RA",
                    "batters_used",
                    "pitchers_used",
                    "year_ID",
                ]
            ).cast(pl.Int16),
            pl.col(
                [
                    "win_loss_perc",
                    "win_loss_perc_pythag",
                    "age_bat",
                    "age_pit",
                ]
            ).cast(pl.Float32),
        ]
    )
    df = df.with_columns(pl.col("games_back").str.replace("--", "0").cast(pl.Float32))
    if start_season:
        df = df.filter(pl.col("year_ID") >= start_season)
    if end_season:
        df = df.filter(pl.col("year_ID") <= end_season)
    return df
