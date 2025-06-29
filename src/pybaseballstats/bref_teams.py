import pandas as pd
import polars as pl
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pybaseballstats.consts.bref_consts import BREF_TEAM_BATTING_URL, BREFTeams
from pybaseballstats.utils.bref_utils import BREFSingleton, _extract_table

bref = BREFSingleton.instance()


def team_standard_batting(
    team: BREFTeams,
    year: int,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Returns a DataFrame of team standard batting data for a given year. NOTE: This function uses Selenium to scrape the data, so it may be slow.

    Args:
        team (BREFTeams): Which team to pull data from. Use the BREFTeams enum to get the correct team code. You can use the show_options() method to see all available teams.
        year (int): Which year to pull data from
        return_pandas (bool, optional): Whether or not to return the DataFrame as a pandas DataFrame. Defaults to False.

    Returns:
        pl.DataFrame | pd.DataFrame: A DataFrame of team standard batting data for the given year. If False, returns a polars DataFrame. If True, returns a pandas DataFrame.
    """
    with bref.get_driver() as driver:
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
    return (
        team_standard_batting_df
        if not return_pandas
        else team_standard_batting_df.to_pandas()
    )


def team_value_batting(
    team: BREFTeams,
    year: int,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    """Return a DataFrame of team value batting data for a given year. NOTE: This function uses Selenium to scrape the data, so it may be slow.

    Args:
        team (BREFTeams): Which team to pull data from. Use the BREFTeams enum to get the correct team code. You can use the show_options() method to see all available teams.
        year (int): Which year to pull data from
        return_pandas (bool, optional): Whether to return a pandas DataFrame or Polars DataFrame. Defaults to False (polars DataFrame).

    Returns:
        pl.DataFrame | pd.DataFrame: _description_
    """
    with bref.get_driver() as driver:
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
    return (
        team_value_batting_df
        if not return_pandas
        else team_value_batting_df.to_pandas()
    )
