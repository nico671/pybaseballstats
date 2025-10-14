import polars as pl
from bs4 import BeautifulSoup

from pybaseballstats.consts.bref_consts import (
    BREF_MANAGER_TENDENCIES_URL,
    BREF_MANAGERS_GENERAL_URL,
)
from pybaseballstats.utils.bref_utils import (
    BREFSession,
    _extract_table,
)

session = BREFSession.instance()  # type: ignore[attr-defined]
__all__ = ["managers_basic_data", "managers_tendencies_data"]


def managers_basic_data(year: int) -> pl.DataFrame:
    """Returns a DataFrame of manager data for a given year. NOTE: This function uses Playwright to scrape the data, so it may be slow.

    Args:
        year (int): Which year to pull manager data from

    Raises:
        ValueError: If year is None
        ValueError: If year is less than 1871
        TypeError: If year is not an integer

    Returns:
        pl.DataFrame: A Polars DataFrame of manager data for the given year.
    """
    if not year:
        raise ValueError("Year must be provided")
    if not isinstance(year, int):
        raise TypeError("Year must be an integer")
    if year < 1871:
        raise ValueError("Year must be greater than 1871")

    with session.get_page() as page:
        url = BREF_MANAGERS_GENERAL_URL.format(year=year)
        page.goto(url, wait_until="domcontentloaded")

        # Wait for the table to be populated by JavaScript
        page.wait_for_function(
            """() => {
                const table = document.querySelector('#manager_record');
                return table && table.rows && table.rows.length > 1;
            }""",
            timeout=15000,
        )

        html = page.locator("#div_manager_record").inner_html()
        soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", {"id": "manager_record"})
    df = pl.DataFrame(_extract_table(table))
    df = df.select(pl.all().replace("", "0"))
    df = df.drop("ranker")
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
            pl.col("W_post").cast(pl.Int32).fill_null(0).alias("postseason_wins"),
            pl.col("L_post").cast(pl.Int32).fill_null(0).alias("postseason_losses"),
        ]
    ).drop(["W_post", "L_post"])
    print(df)
    return df


def managers_tendencies_data(year: int) -> pl.DataFrame:
    """Returns a DataFrame of manager tendencies data for a given year. NOTE: This function uses Playwright to scrape the data, so it may be slow.

    Args:
        year (int): Which year to pull manager tendencies data from

    Raises:
        ValueError: If year is None
        ValueError: If year is less than 1871
        TypeError: If year is not an integer


    Returns:
        pl.DataFrame: A DataFrame of manager tendencies data for the given year.
    """
    if not year:
        raise ValueError("Year must be provided")
    if not isinstance(year, int):
        raise TypeError("Year must be an integer")
    if year < 1871:
        raise ValueError("Year must be greater than 1871")

    resp = session.get(BREF_MANAGER_TENDENCIES_URL.format(year=year))
    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find("table", {"id": "manager_tendencies"})
    df = pl.DataFrame(_extract_table(table))
    df = df.select(pl.all().str.replace("", "0").str.replace("%", ""))
    df = df.drop("ranker")
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
    return df
