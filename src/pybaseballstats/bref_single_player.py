import pandas as pd
import polars as pl
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pybaseballstats.utils.bref_singleton import BREFSingleton
from pybaseballstats.utils.bref_utils import (
    BREF_SINGLE_PLAYER_SABERMETRIC_FIELDING_URL,
    BREF_SINGLE_PLAYER_URL,
    _extract_table,
)

bref = BREFSingleton.instance()


# TODO: usage documentation for all functions
def single_player_standard_batting(
    player_code: str, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    """Returns a DataFrame of a player's standard batting statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.
        return_pandas (bool, optional): If True, returns a pandas DataFrame. If False, returns a polars DataFrame. Defaults to False.

    Returns:
        pl.DataFrame | pd.DataFrame: Either a polars DataFrame or a pandas DataFrame containing the player's standard batting statistics.
    """
    last_name_initial = player_code[0].lower()
    with bref.get_driver() as driver:
        driver.get(
            BREF_SINGLE_PLAYER_URL.format(
                initial=last_name_initial, player_code=player_code
            )
        )
        wait = WebDriverWait(driver, 15)
        standard_stats_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content"))
        )
        soup = BeautifulSoup(
            standard_stats_table.get_attribute("outerHTML"), "html.parser"
        )
    standard_stats_table = soup.find("div", {"id": "all_players_standard_batting"})
    standard_stats_table = standard_stats_table.find("table")
    standard_stats_df = pl.DataFrame(_extract_table(standard_stats_table))
    standard_stats_df = standard_stats_df.with_columns(
        pl.col(
            [
                "age",
                "b_hbp",
                "b_ibb",
                "b_sh",
                "b_sf",
                "b_games",
                "b_pa",
                "b_ab",
                "b_r",
                "b_h",
                "b_doubles",
                "b_triples",
                "b_hr",
                "b_rbi",
                "b_sb",
                "b_cs",
                "b_bb",
                "b_so",
                "b_onbase_plus_slugging_plus",
                "b_rbat_plus",
                "b_tb",
                "b_gidp",
            ]
        ).cast(pl.Int32),
        pl.col(
            [
                "b_war",
                "b_batting_avg",
                "b_onbase_perc",
                "b_slugging_perc",
                "b_onbase_plus_slugging",
                "b_roba",
            ]
        ).cast(pl.Float32),
    )
    standard_stats_df = standard_stats_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("b_", ""))
    )
    standard_stats_df = standard_stats_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
    )
    standard_stats_df = standard_stats_df.with_columns(
        pl.lit(player_code).alias("key_bbref")
    )
    return standard_stats_df if not return_pandas else standard_stats_df.to_pandas()


def single_player_value_batting(
    player_code: str, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    """Returns a DataFrame of a player's value batting statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.
        return_pandas (bool, optional): If True, returns a pandas DataFrame. If False, returns a polars DataFrame. Defaults to False.


    Returns:
        pl.DataFrame | pd.DataFrame: Either a polars DataFrame or a pandas DataFrame containing the player's value batting statistics.
    """
    last_name_initial = player_code[0].lower()
    with bref.get_driver() as driver:
        driver.get(
            BREF_SINGLE_PLAYER_URL.format(
                initial=last_name_initial, player_code=player_code
            )
        )
        wait = WebDriverWait(driver, 15)
        standard_stats_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content"))
        )
        soup = BeautifulSoup(
            standard_stats_table.get_attribute("outerHTML"), "html.parser"
        )
    value_batting_table = soup.find("div", {"id": "all_players_value_batting"})
    value_batting_table = value_batting_table.find("table")
    value_batting_df = pl.DataFrame(_extract_table(value_batting_table))
    value_batting_df = value_batting_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("b_", ""))
    )

    value_batting_df = value_batting_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
    )
    value_batting_df = value_batting_df.with_columns(
        pl.col(
            [
                "age",
                "pa",
                "runs_batting",
                "runs_baserunning",
                "runs_fielding",
                "runs_double_plays",
                "runs_position",
                "raa",
                "runs_replacement",
                "rar",
                "rar_off",
            ]
        ).cast(pl.Int32),
        pl.col(
            [
                "waa",
                "war",
                "waa_win_perc",
                "waa_win_perc_162",
                "war_off",
                "war_def",
            ]
        ).cast(pl.Float32),
    )
    value_batting_df = value_batting_df.with_columns(
        pl.lit(player_code).alias("key_bbref")
    )
    return value_batting_df if not return_pandas else value_batting_df.to_pandas()


def single_player_advanced_batting(
    player_code: str, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    """Returns a DataFrame of a player's advanced batting statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.
        return_pandas (bool, optional): If True, returns a pandas DataFrame. If False, returns a polars DataFrame. Defaults to False.


    Returns:
        pl.DataFrame | pd.DataFrame: Either a polars DataFrame or a pandas DataFrame containing the player's advanced batting statistics.
        This includes statistics such as stolen base percentage, extra bases taken percentage, run scoring percentage, and more.
    """
    last_name_initial = player_code[0].lower()
    with bref.get_driver() as driver:
        driver.get(
            BREF_SINGLE_PLAYER_URL.format(
                initial=last_name_initial, player_code=player_code
            )
        )
        wait = WebDriverWait(driver, 15)
        standard_stats_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content"))
        )
        soup = BeautifulSoup(
            standard_stats_table.get_attribute("outerHTML"), "html.parser"
        )
    advanced_batting_table = soup.find("div", {"id": "all_players_advanced_batting"})

    advanced_batting_table = advanced_batting_table.find("table")
    advanced_batting_df = pl.DataFrame(_extract_table(advanced_batting_table))
    advanced_batting_df = advanced_batting_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("b_", ""))
    )
    advanced_batting_df = advanced_batting_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
    )
    advanced_batting_df = advanced_batting_df.with_columns(
        pl.all().str.replace("%", "")
    )
    advanced_batting_df = advanced_batting_df.with_columns(
        pl.col(
            [
                "age",
                "pa",
                "rbat_plus",
            ]
        ).cast(pl.Int32),
        pl.col(
            [
                "stolen_base_perc",
                "extra_bases_taken_perc",
                "run_scoring_perc",
                "baseout_runs",
                "cwpa_bat",
                "wpa_bat",
                "roba",
                "batting_avg_bip",
                "iso_slugging",
                "home_run_perc",
                "strikeout_perc",
                "base_on_balls_perc",
                "avg_exit_velo",
                "hard_hit_perc",
                "ld_perc",
                "fperc",
                "gperc",
                "gfratio",
                "pull_perc",
                "center_perc",
                "oppo_perc",
            ]
        ).cast(pl.Float32),
    )
    advanced_batting_df = advanced_batting_df.with_columns(
        pl.lit(player_code).alias("key_bbref")
    )
    return advanced_batting_df if not return_pandas else advanced_batting_df.to_pandas()


def single_player_standard_fielding(
    player_code: str, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    """Returns a DataFrame of a player's standard fielding statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.
        return_pandas (bool, optional): If True, returns a pandas DataFrame. If False, returns a polars DataFrame. Defaults to False.


    Returns:
        pl.DataFrame | pd.DataFrame: Either a polars DataFrame or a pandas DataFrame containing the player's standard fielding statistics.
        This includes statistics such as fielding percentage, innings played, and total chances.
    """
    last_name_initial = player_code[0].lower()
    with bref.get_driver() as driver:
        driver.get(
            BREF_SINGLE_PLAYER_URL.format(
                initial=last_name_initial, player_code=player_code
            )
        )
        wait = WebDriverWait(driver, 15)
        standard_stats_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content"))
        )
        soup = BeautifulSoup(
            standard_stats_table.get_attribute("outerHTML"), "html.parser"
        )
    table_wrapper = soup.find("div", {"id": "div_players_standard_fielding"})
    table = table_wrapper.find("table")
    standard_fielding_df = pl.DataFrame(_extract_table(table))
    standard_fielding_df = standard_fielding_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("f_", ""))
    )
    standard_fielding_df = standard_fielding_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
    )
    standard_fielding_df = standard_fielding_df.with_columns(
        pl.col(
            [
                "age",
                "games",
                "games_started",
                "cg",
                "chances",
                "po",
                "assists",
                "errors",
                "dp",
                "tz_runs_total",
                "tz_runs_total_per_year",
                "drs_total",
                "drs_total_per_year",
            ]
        ).cast(pl.Int32),
        pl.col(
            [
                "fielding_perc",
                "innings",
                "fielding_perc_lg",
                "range_factor_per_nine",
                "range_factor_per_nine_lg",
                "range_factor_per_game",
                "range_factor_per_game_lg",
            ]
        ).cast(pl.Float32),
    )
    standard_fielding_df = standard_fielding_df.with_columns(
        pl.lit(player_code).alias("key_bbref")
    )
    return (
        standard_fielding_df if not return_pandas else standard_fielding_df.to_pandas()
    )


def single_player_sabermetric_fielding(
    player_code: str, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    """Returns a DataFrame of a player's advanced fielding statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.
        return_pandas (bool, optional): If True, returns a pandas DataFrame. If False, returns a polars DataFrame. Defaults to False.
    Returns:
        pl.DataFrame | pd.DataFrame: Either a polars DataFrame or a pandas DataFrame containing the player's advanced fielding statistics.
    """
    last_name_initial = player_code[0].lower()
    with bref.get_driver() as driver:
        driver.get(
            BREF_SINGLE_PLAYER_SABERMETRIC_FIELDING_URL.format(
                initial=last_name_initial, player_code=player_code
            )
        )
        wait = WebDriverWait(driver, 15)
        standard_stats_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#content"))
        )
        soup = BeautifulSoup(
            standard_stats_table.get_attribute("outerHTML"), "html.parser"
        )
    sabermetric_fielding_table = soup.find("div", {"id": "div_advanced_fielding"})
    sabermetric_fielding_table = sabermetric_fielding_table.find("table")
    sabermetric_fielding_df = pl.DataFrame(_extract_table(sabermetric_fielding_table))
    sabermetric_fielding_df = sabermetric_fielding_df.fill_null(0)
    sabermetric_fielding_df = sabermetric_fielding_df.with_columns(
        pl.all().exclude(["team_ID", "pos", "lg_ID"]).cast(pl.Int32)
    )
    sabermetric_fielding_df = sabermetric_fielding_df.with_columns(
        pl.lit(player_code).alias("key_bbref")
    )
    return (
        sabermetric_fielding_df
        if not return_pandas
        else sabermetric_fielding_df.to_pandas()
    )


def single_player_salaries(
    player_code: str, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    """Returns a DataFrame of a player's salary history.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.
        return_pandas (bool, optional): If True, returns a pandas DataFrame. If False, returns a polars DataFrame. Defaults to False.

    Returns:
        pl.DataFrame | pd.DataFrame: A DataFrame containing the player's salary history.
        This includes the year, team, league, and salary.
    """
    last_name_initial = player_code[0].lower()
    with bref.get_driver() as driver:
        driver.get(
            BREF_SINGLE_PLAYER_URL.format(
                initial=last_name_initial, player_code=player_code
            )
        )
        wait = WebDriverWait(driver, 15)
        salaries_table = wait.until(
            EC.presence_of_element_located((By.ID, "all_br-salaries"))
        )
        soup = BeautifulSoup(salaries_table.get_attribute("outerHTML"), "html.parser")
        salaries_table = soup.find("table")
    salaries_df = pl.DataFrame(_extract_table(salaries_table))
    salaries_df = salaries_df.with_columns(
        pl.col("Salary")
        .str.replace("\\$", "")
        .str.replace(",", "")
        .str.replace("\\*", "")
        .cast(pl.Int32),
    )

    salaries_df = salaries_df.rename({"Salary": "salary ($)"})
    return salaries_df if not return_pandas else salaries_df.to_pandas()
