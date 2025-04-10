from datetime import datetime
from enum import Enum

import dateparser
import pandas as pd
import polars as pl
import requests
from bs4 import BeautifulSoup

from pybaseballstats.utils.fangraphs_consts import (
    FG_SINGLE_GAME_URL,
)


# TODO: usage docs
class FangraphsSingleGameTeams(Enum):
    Angels = "Angels"
    Astros = "Astros"
    Athletics = "Athletics"
    Blue_Jays = "Blue+Jays"
    Braves = "Braves"
    Brewers = "Brewers"
    Cardinals = "Cardinals"
    Cubs = "Cubs"
    Diamondbacks = "Diamondbacks"
    Dodgers = "Dodgers"
    Giants = "Giants"
    Guardians = "Guardians"
    Mariners = "Mariners"
    Marlins = "Marlins"
    Mets = "Mets"
    Nationals = "Nationals"
    Orioles = "Orioles"
    Padres = "Padres"
    Phillies = "Phillies"
    Pirates = "Pirates"
    Rangers = "Rangers"
    Rays = "Rays"
    Red_Sox = "Red+Sox"
    Reds = "Reds"
    Rockies = "Rockies"
    Royals = "Royals"
    Tigers = "Tigers"
    Twins = "Twins"
    White_Sox = "White+Sox"
    Yankees = "Yankees"


def fangraphs_single_game_play_by_play(
    date: str,  # date in 'YYYY-MM-DD' format
    team: FangraphsSingleGameTeams,  # team name
    return_pandas: bool = False,
) -> pl.DataFrame | pd.DataFrame:
    # validate date
    date_object = dateparser.parse(date)
    date_string = date_object.strftime("%Y-%m-%d")
    if date_object > datetime.now():
        raise ValueError("Date cannot be in the future")
    if date_object < datetime(1977, 4, 6):
        raise ValueError("Date cannot be before 1977-04-06")

    if type(team) is not FangraphsSingleGameTeams:
        raise ValueError("team must be of type FangraphsSingleGameTeams")
    content = requests.get(
        FG_SINGLE_GAME_URL.format(date=date_string, team=team.value)
    ).content
    soup = BeautifulSoup(content, "html.parser")
    table = soup.find(
        "table", {"class": "rgMasterTable", "id": "WinsBox1_dgPlay_ctl00"}
    )
    headers = table.thead.find_all("th")
    headers = [header.text for header in headers]
    headers = headers[:-2]  # remove last two columns
    row_data = {}
    for header in headers:
        row_data[header] = []
    for tr in table.tbody.find_all("tr"):
        for i, td in enumerate(tr.find_all("td")):
            if "style" in td.attrs and td.attrs["style"] == "display:none;":
                continue
            row_data[headers[i]].append(td.text)
    df = pl.DataFrame(row_data)
    df = df.with_columns(
        [
            pl.col("Inn.").cast(pl.Int8),
            pl.col("Outs").cast(pl.Int8),
            pl.col("LI").cast(pl.Float32),
            pl.col("WPA").cast(pl.Float32),
            pl.col("RE").cast(pl.Float32),
            pl.col("WE").str.replace("%", "").cast(pl.Float32),
            pl.col("RE24").cast(pl.Float32),
        ]
    )
    df = df.rename(
        {
            "Inn.": "Inning",
            "Base": "Base State",
            "LI": "Leverage Index",
            "WPA": "Win Probability Added",
            "WE": "Win Expectancy",
            "RE24": "Run Expectancy",
        }
    )
    return df if not return_pandas else df.to_pandas()
