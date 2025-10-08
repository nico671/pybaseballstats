from datetime import datetime

import dateparser
import polars as pl
import requests
from bs4 import BeautifulSoup

from pybaseballstats.consts.fangraphs_consts import (
    FG_SINGLE_GAME_URL,
    FangraphsSingleGameTeams,
)

__all__ = ["FangraphsSingleGameTeams", "fangraphs_single_game_play_by_play"]


def fangraphs_single_game_play_by_play(
    date: str,  # date in 'YYYY-MM-DD' format
    team: FangraphsSingleGameTeams,  # team name
) -> pl.DataFrame:
    """Returns a DataFrame of play-by-play data for a given date and team from Fangraphs.

    Args:
        date (str): date in 'YYYY-MM-DD' format, dictating which game to pull data from
        team (FangraphsSingleGameTeams): team name, use the FangraphsSingleGameTeams enum to get the correct team code. Use the show_options() method to see all available teams.
    Raises:
        ValueError: If date is in the future
        ValueError: If date is before 1977-04-06
        ValueError: If team is not of type FangraphsSingleGameTeams

    Returns:
        pl.DataFrame: A DataFrame of play-by-play data for the given date and team.
    """
    # validate date
    date_object = dateparser.parse(date)
    assert date_object, "date must be in 'YYYY-MM-DD' format"
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
    assert table, (
        "Error extracting data for the given date and team. Please validate inputs."
    )
    headers = table.thead.find_all("th")
    headers = [header.text for header in headers]
    headers = headers[:-2]
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
    return df


# TODO: extra stats from this page are available, could add in the future
