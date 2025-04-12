from enum import Enum

import pandas as pd
import polars as pl
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pybaseballstats.utils.bref_singleton import BREFSingleton
from pybaseballstats.utils.bref_utils import _extract_table

bref = BREFSingleton.instance()


class BREFTeams(Enum):
    ANGELS = "ANA"
    DIAMONDBACKS = "ARI"
    BRAVES = "ATL"
    ORIOLES = "BAL"
    RED_SOX = "BOS"
    CUBS = "CHC"
    WHITE_SOX = "CHW"
    REDS = "CIN"
    GUARDIANS = "CLE"
    ROCKIES = "COL"
    TIGERS = "DET"
    MARLINS = "FLA"
    ASTROS = "HOU"
    ROYALS = "KCR"
    DODGERS = "LAD"
    BREWERS = "MIL"
    TWINS = "MIN"
    METS = "NYM"
    YANKEES = "NYY"
    ATHLETICS = "OAK"
    PHILLIES = "PHI"
    PIRATES = "PIT"
    PADRES = "SDP"
    MARINERS = "SEA"
    GIANTS = "SFG"
    CARDINALS = "STL"
    RAYS = "TBD"
    RANGERS = "TEX"
    BLUE_JAYS = "TOR"
    NATIONALS = "WSN"


BREF_TEAM_BATTING_URL = (
    "https://www.baseball-reference.com/teams/{team_code}/{year}-batting.shtml"
)


def team_standard_batting(
    team: BREFTeams,
    year: int,
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
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
