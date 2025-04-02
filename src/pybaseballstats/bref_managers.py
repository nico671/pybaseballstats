from contextlib import contextmanager

import pandas as pd
import polars as pl
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@contextmanager
def get_driver():
    """Provides a WebDriver instance that automatically quits on exit."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    try:
        yield driver  # Hands control to the function using it
    finally:
        driver.quit()  # Ensures WebDriver is always closed


MANAGERS_URL = "https://www.baseball-reference.com/leagues/majors/{year}-managers.shtml#manager_record"


def managers_basic_data(
    year: int, return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame:
    if not year:
        raise ValueError("Year must be provided")
    if not isinstance(year, int):
        raise TypeError("Year must be an integer")
    print("getting driver")
    with get_driver() as driver:
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
