import pandas as pd
import polars as pl
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pybaseballstats.utils.bref_singleton import BREFSingleton
from pybaseballstats.utils.bref_utils import MANAGER_TENDENCY_URL, MANAGERS_URL

bref = BREFSingleton.instance()


# TODO: usage docs for all functions
def managers_basic_data(
    year: int, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    """Returns a DataFrame of manager data for a given year. NOTE: This function uses Selenium to scrape the data, so it may be slow.

    Args:
        year (int): Which year to pull manager data from
        return_pandas (bool, optional): Whether or not to return the data as a pandas DataFrame. Defaults to False (returning a polars DataFrame).

    Raises:
        ValueError: If year is None
        ValueError: If year is less than 1871
        TypeError: If year is not an integer

    Returns:
        pl.DataFrame | pd.DataFrame: A DataFrame of manager data for the given year. If False, returns a polars DataFrame. If True, returns a pandas DataFrame.
    """
    if not year:
        raise ValueError("Year must be provided")
    if not isinstance(year, int):
        raise TypeError("Year must be an integer")
    if year < 1871:
        raise ValueError("Year must be greater than 1871")
    with bref.get_driver() as driver:
        try:
            driver.get(MANAGERS_URL.format(year=year))
            wait = WebDriverWait(driver, 15)
            draft_table = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#div_manager_record"))
            )

            soup = BeautifulSoup(draft_table.get_attribute("outerHTML"), "lxml")
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    table = soup.find("table", {"id": "manager_record"})

    thead = soup.find_all("thead")[0]
    thead_rows = thead.find_all("tr")
    headers = []
    row = thead_rows[0]
    for th in row.find_all("th"):
        headers.append(th.attrs["data-stat"])
    headers.remove("ranker")

    tbody = table.find_all("tbody")[0]
    row_data = {}

    for h in headers:
        row_data[h] = []
    body_rows = tbody.find_all("tr")
    for tr in body_rows:
        for td in tr.find_all("td"):
            row_data[td.attrs["data-stat"]].append(td.get_text(strip=True))
    df = pl.DataFrame(row_data)
    df = df.select(pl.all().replace("", "0"))
    df = df.with_columns(
        [
            pl.col("mgr_replay_success_rate")
            .str.replace("%", "")
            .str.replace("", "0")
            .cast(pl.Float32),
            pl.col(
                [
                    "W",
                    "L",
                    "ties",
                    "G",
                    "mgr_challenge_count",
                    "mgr_overturn_count",
                    "mgr_ejections",
                ]
            ).cast(pl.Int32),
            pl.col(["win_loss_perc", "finish", "win_loss_perc_post"]).cast(pl.Float32),
            pl.col("W_post").cast(pl.Int32).alias("postseason_wins"),
            pl.col("L_post").cast(pl.Int32).alias("postseason_losses"),
        ]
    ).drop(["W_post", "L_post"])
    return df if not return_pandas else df.to_pandas()


def manager_tendencies_data(
    year: int, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    """Returns a DataFrame of manager tendencies data for a given year. NOTE: This function uses Selenium to scrape the data, so it may be slow.

    Args:
        year (int): Which year to pull manager tendencies data from
        return_pandas (bool, optional): Whether or not to return the data as a pandas DataFrame. Defaults to False (returning a polars DataFrame).

    Raises:
        ValueError: If year is None
        ValueError: If year is less than 1871
        TypeError: If year is not an integer


    Returns:
        pl.DataFrame | pd.DataFrame: A DataFrame of manager tendencies data for the given year. If False, returns a polars DataFrame. If True, returns a pandas DataFrame.
    """
    if not year:
        raise ValueError("Year must be provided")
    if not isinstance(year, int):
        raise TypeError("Year must be an integer")
    if year < 1871:
        raise ValueError("Year must be greater than 1871")

    with bref.get_driver() as driver:
        driver.get(MANAGER_TENDENCY_URL.format(year=year))
        wait = WebDriverWait(driver, 15)
        draft_table = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#manager_tendencies"))
        )

        soup = BeautifulSoup(draft_table.get_attribute("outerHTML"), "lxml")
    table = soup.find("table", {"id": "manager_tendencies"})
    thead = soup.find_all("thead")[0]

    thead_rows = thead.find_all("tr")
    thead_rows = thead_rows[1]
    headers = []
    for th in thead_rows.find_all("th"):
        headers.append(th.attrs["data-stat"])
    headers.remove("ranker")
    headers = list(set(headers))
    tbody = table.find_all("tbody")[0]
    row_data = {}

    body_rows = tbody.find_all("tr")
    for tr in body_rows:
        for td in tr.find_all("td"):
            if td.attrs["data-stat"] not in row_data:
                row_data[td.attrs["data-stat"]] = []
            row_data[td.attrs["data-stat"]].append(td.get_text(strip=True))
    df = pl.DataFrame(row_data)
    df = df.select(pl.all().str.replace("", "0").str.replace("%", ""))
    df = df.with_columns(
        pl.col(
            [
                "age",
                "manager_games",
                "steal_2b_chances",
                "steal_2b_attempts",
                "steal_2b_rate_plus",
                "steal_3b_chances",
                "steal_3b_attempts",
                "steal_3b_rate_plus",
                "sac_bunt_chances",
                "sac_bunts",
                "sac_bunt_rate_plus",
                "ibb_chances",
                "ibb",
                "ibb_rate_plus",
                "pinch_hitters_plus",
                "pinch_runners_plus",
                "pitchers_used_per_game_plus",
            ]
        ).cast(pl.Int32),
        pl.col(
            [
                "steal_2b_rate",
                "steal_3b_rate",
                "sac_bunt_rate",
                "ibb_rate",
                "pinch_hitters",
                "pinch_runners",
                "pitchers_used_per_game",
            ]
        ).cast(pl.Float32),
    )
    df = df.with_columns(
        pl.col(
            [
                "manager",
                "team_ID",
            ]
        ).str.replace("0", "")
    )
    return df if not return_pandas else df.to_pandas()
