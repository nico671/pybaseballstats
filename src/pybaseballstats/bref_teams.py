import polars as pl
from bs4 import BeautifulSoup

from pybaseballstats.consts.bref_consts import BREF_TEAMS_GENERAL_URL, BREFTeams
from pybaseballstats.utils.bref_utils import BREFSession, _extract_table

session = BREFSession.instance()  # type: ignore[attr-defined]


def team_franchise_history(team: BREFTeams) -> pl.DataFrame:
    """Returns year-by-year history of a franchise. Currently only supports current teams

    Args:
        team (BREFTeams): A BREFTeams enum value representing the team

    Returns:
        pl.DataFrame: A DataFrame containing the franchise history
    """
    assert isinstance(team, BREFTeams), "team must be a valid BREFTeams enum value"

    with session.get_page() as page:
        team_code = team.value
        url = BREF_TEAMS_GENERAL_URL.format(team_code=team_code)
        page.goto(url)
        page.wait_for_selector("#div_franchise_years", timeout=5000)
        html = page.locator("#div_franchise_years").inner_html()
        soup = BeautifulSoup(html, "html.parser")

    df = pl.DataFrame(_extract_table(soup.find("table")))
    df = df.with_columns(
        pl.col("games_back").str.replace("--", "0.0"),
        pl.col("playoffs").fill_null("Missed"),
    )
    df = df.with_columns(
        pl.col(
            [
                "year_ID",
                "G",
                "W",
                "L",
                "ties",
                "R",
                "RA",
                "batters_used",
                "pitchers_used",
            ]
        ).cast(pl.Int16),
        pl.col(
            [
                "win_loss_perc",
                "win_loss_perc_pythag",
                "games_back",
                "age_bat",
                "age_pit",
            ]
        ).cast(pl.Float32),
    )
    return df
