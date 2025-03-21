# import pandas as pd
# import polars as pl
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait

# options = Options()
# options.add_argument("--headless")
# driver = webdriver.Chrome(options=options)
# BREF_DRAFT_URL = "https://www.baseball-reference.com/draft/index.fcgi?year_ID={draft_year}&draft_round={draft_round}&draft_type=junreg&query_type=year_round&from_type_hs=0&from_type_jc=0&from_type_4y=0&from_type_unk=0"


# def draft_order_by_round(
#     year: int, draft_round: int, return_pandas: bool = False
# ) -> pl.DataFrame | pd.DataFrame:
#     """Returns the draft order for a given round in a given year. NOTE: This function uses Selenium to scrape the data, so it may be slow.

#     Args:
#         year (int): Which year to pull draft data from
#         draft_round (int): Which round to pull draft data from
#         return_pandas (bool, optional): Whether or not to return the data as a pandas DataFrame. Defaults to False (returning a polars DataFrame).

#     Raises:
#         ValueError: If the year is before 1965
#         ValueError: If the draft round is not between 1 and 60

#     Returns:
#         pl.DataFrame | pd.DataFrame: A DataFrame of draft data for the given year and round
#     """
#     if year < 1965:
#         raise ValueError("Draft data is only available from 1965 onwards")
#     if draft_round < 1 or draft_round > 60:
#         raise ValueError("Draft round must be between 1 and 60")

#     try:
#         driver.get(BREF_DRAFT_URL.format(draft_year=year, draft_round=draft_round))
#         wait = WebDriverWait(driver, 10)
#         draft_table = wait.until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "#div_draft_stats"))
#         )
#     finally:
#         driver.quit()

#     soup = BeautifulSoup(draft_table.get_attribute("outerHTML"), "html.parser")
#     table = soup.find("table", id="draft_stats")

#     headers = [th["data-stat"] for th in table.thead.find_all("th")]

#     rows = []
#     for row in table.tbody.find_all("tr"):
#         if "class" in row.attrs and "thead" in row.attrs["class"]:
#             continue
#         cells = row.find_all(["th", "td"])

#         row_data = {}
#         for header, cell in zip(headers, cells):
#             row_data[header] = cell.get_text(strip=True)
#         rows.append(row_data)

#     df = pl.DataFrame(rows)
#     df = df.drop("draft_abb", "franch_round")
#     df = df.with_columns(
#         pl.all().replace("", "0"),
#     )
#     df = df.with_columns(
#         [
#             pl.col("player").str.replace(r"\(minors\)", ""),
#             pl.col(
#                 [
#                     "draft_round",
#                     "overall_pick",
#                     "round_pick",
#                     "G_bat",
#                     "AB",
#                     "HR",
#                     "G_pitch",
#                     "W",
#                     "L",
#                     "SV",
#                     "year_ID",
#                 ]
#             ).cast(pl.Int32),
#             pl.col(
#                 ["WAR", "batting_avg", "onbase_plus_slugging", "earned_run_avg", "whip"]
#             ).cast(pl.Float32),
#         ]
#     )
#     return df if not return_pandas else df.to_pandas()


# TEAM_YEAR_DRAFT_URL = "https://www.baseball-reference.com/draft/index.fcgi?team_ID={team}&year_ID={year}&draft_type=junreg&query_type=franch_year&from_type_hs=0&from_type_4y=0&from_type_unk=0&from_type_jc=0"


# def franchise_draft_order(
#     team: str, year: int, return_pandas: bool = False
# ) -> pl.DataFrame | pd.DataFrame:
#     if year < 1965:
#         raise ValueError("Draft data is only available from 1965 onwards")
#     if team not in [
#         "ANA",
#         "ARI",
#         "ATL",
#         "BAL",
#         "BOS",
#         "CHC",
#         "CHW",
#         "CIN",
#         "CLE",
#         "COL",
#         "DET",
#         "FLA",
#         "HOU",
#         "KCR",
#         "LAD",
#         "MIL",
#         "MIN",
#         "NYM",
#         "NYY",
#         "OAK",
#         "PHI",
#         "PIT",
#         "SDP",
#         "SEA",
#         "SFG",
#         "STL",
#         "TBD",
#         "TEX",
#         "TOR",
#         "WSN",
#     ]:
#         raise ValueError("Invalid team abbreviation")
#     try:
#         driver.get(TEAM_YEAR_DRAFT_URL.format(year=year, team=team))

#         wait = WebDriverWait(driver, 10)
#         draft_table = wait.until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "#div_draft_stats"))
#         )
#     finally:
#         driver.quit()

#     soup = BeautifulSoup(draft_table.get_attribute("outerHTML"), "html.parser")

#     table = soup.find("table", id="draft_stats")

#     headers = [th["data-stat"] for th in table.thead.find_all("th")]

#     rows = []

#     for row in table.tbody.find_all("tr"):
#         cells = row.find_all(["th", "td"])

#         row_data = {}
#         for header, cell in zip(headers, cells):
#             row_data[header] = cell.get_text(strip=True)
#         rows.append(row_data)

#     df = pl.DataFrame(rows)
#     df = df.drop("draft_abb")
#     df = df.with_columns(
#         pl.all().replace("", "0"),
#     )
#     df = df.with_columns(
#         [
#             pl.col("player").str.replace(r"\(minors\)", ""),
#             pl.col(
#                 [
#                     "draft_round",
#                     "overall_pick",
#                     "round_pick",
#                     "G_bat",
#                     "AB",
#                     "HR",
#                     "G_pitch",
#                     "year_ID",
#                     "W",
#                     "L",
#                     "SV",
#                 ]
#             ).cast(pl.Int32),
#             pl.col(
#                 ["WAR", "batting_avg", "onbase_plus_slugging", "earned_run_avg", "whip"]
#             ).cast(pl.Float32),
#         ]
#     )
#     return df if not return_pandas else df.to_pandas()
