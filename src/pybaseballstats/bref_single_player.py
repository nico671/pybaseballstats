import pandas as pd
import polars as pl
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pybaseballstats.utils.bref_singleton import BREFSingleton

bref = BREFSingleton.instance()
BREF_SINGLE_PLAYER_BATTING_URL = (
    "https://www.baseball-reference.com/players/{initial}/{player_code}.shtml"
)


def _extract_table(table):
    trs = table.tbody.find_all("tr")
    row_data = {}
    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) == 0:
            continue
        for td in tds:
            data_stat = td.attrs["data-stat"]
            if data_stat not in row_data:
                row_data[data_stat] = []
            row_data[data_stat].append(td.string)
    return row_data


# TODO: docsttrings for all functions
# TODO: decide whether or not to merge these 3 functions
# TODO: usage documentation for all functions
def single_player_standard_batting(
    player_code: str, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    last_name_initial = player_code[0].lower()
    with bref.get_driver() as driver:
        driver.get(
            BREF_SINGLE_PLAYER_BATTING_URL.format(
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
    last_name_initial = player_code[0].lower()
    with bref.get_driver() as driver:
        driver.get(
            BREF_SINGLE_PLAYER_BATTING_URL.format(
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
    last_name_initial = player_code[0].lower()
    with bref.get_driver() as driver:
        driver.get(
            BREF_SINGLE_PLAYER_BATTING_URL.format(
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
