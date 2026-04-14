from typing import Literal

import polars as pl
from bs4 import BeautifulSoup

# TODO: same range of tables as bref_teams, but for this module
from pybaseballstats.consts.bref_consts import (
    BREF_SINGLE_PLAYER_BATTING_URL,
    BREF_SINGLE_PLAYER_SABERMETRIC_FIELDING_URL,
    BREF_SINGLE_PLAYER_URL,
)
from pybaseballstats.utils.bref_utils import (
    BREFSession,
    _extract_table,
)

session = BREFSession.instance()  # type: ignore[attr-defined]
__all__ = [
    "single_player_batting",
    "single_player_standard_fielding",
    "single_player_sabermetric_fielding",
    "single_player_standard_pitching",
    "single_player_value_pitching",
    "single_player_advanced_pitching",
]


def single_player_batting(
    player_code: str,
    metric_type: Literal[
        "standard",
        "value",
        "advanced",
        "sabermetric",
        "ratio",
        "win_probability",
        "baserunning",
        "situational",
        "pitches",
        "cumulative",
    ] = "standard",
) -> pl.DataFrame:
    if metric_type not in [
        "standard",
        "value",
        "advanced",
        "sabermetric",
        "ratio",
        "win_probability",
        "baserunning",
        "situational",
        "pitches",
        "cumulative",
    ]:
        raise ValueError(f"Invalid metric type: {metric_type}")
    last_name_initial = player_code[0].lower()
    with session.get_page() as page:
        url = BREF_SINGLE_PLAYER_BATTING_URL.format(
            initial=last_name_initial, player_code=player_code
        )
        page.goto(url, wait_until="networkidle")

        soup = BeautifulSoup(page.content(), "html.parser")
    table_id = ""
    if metric_type in ["standard", "value", "advanced"]:
        table_id = f"players_{metric_type}_batting"
    elif metric_type == "cumulative":
        table_id = "cumulative_batting"
    else:
        table_id = f"batting_{metric_type}"
    table = soup.find("table", id=table_id)
    if table is None:
        raise ValueError(f"Failed to find table with id {table_id}")
    df = pl.DataFrame(_extract_table(table))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    return df


# def single_player_standard_batting(player_code: str) -> pl.DataFrame:
#     """Return standard batting statistics for one player.

#     Args:
#         player_code (str): Baseball Reference player identifier (for example,
#             ``"troutmi01"``).

#     Returns:
#         pl.DataFrame: Standard batting statistics.
#     """
#     last_name_initial = player_code[0].lower()
#     with session.get_page() as page:
#         url = BREF_SINGLE_PLAYER_URL.format(
#             initial=last_name_initial, player_code=player_code
#         )
#         page.goto(url, wait_until="domcontentloaded")
#         # Wait for the specific div to be present
#         page.wait_for_selector("#all_players_standard_batting", timeout=15000)

#         # Get page content
#         content = page.content()
#         soup = BeautifulSoup(content, "html.parser")
#     standard_stats_table_div = soup.find("div", {"id": "all_players_standard_batting"})
#     assert standard_stats_table_div is not None, (
#         "Failed to retrieve standard stats table"
#     )

#     standard_stats_table_actual = standard_stats_table_div.find("table")
#     standard_stats_df = pl.DataFrame(_extract_table(standard_stats_table_actual))
#     standard_stats_df = standard_stats_df.select(
#         pl.all().name.map(lambda col_name: col_name.replace("b_", ""))
#     )
#     standard_stats_df = standard_stats_df.select(
#         pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
#     )
#     return standard_stats_df


# def single_player_value_batting(player_code: str) -> pl.DataFrame:
#     """Return value batting statistics for one player.

#     Args:
#         player_code (str): Baseball Reference player identifier.

#     Returns:
#         pl.DataFrame: Value batting statistics.
#     """
#     last_name_initial = player_code[0].lower()
#     with session.get_page() as page:
#         url = BREF_SINGLE_PLAYER_URL.format(
#             initial=last_name_initial, player_code=player_code
#         )
#         page.goto(url, wait_until="domcontentloaded")
#         page.wait_for_selector("#all_players_value_batting", timeout=15000)

#         # Get page content
#         content = page.content()
#         soup = BeautifulSoup(content, "html.parser")
#     value_batting_table = soup.find("div", {"id": "all_players_value_batting"})
#     assert value_batting_table is not None, "Failed to retrieve value batting table"
#     value_batting_table = value_batting_table.find("table")
#     value_batting_df = pl.DataFrame(_extract_table(value_batting_table))
#     value_batting_df = value_batting_df.select(
#         pl.all().name.map(lambda col_name: col_name.replace("b_", ""))
#     )
#     value_batting_df = value_batting_df.select(
#         pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
#     )
#     return value_batting_df


# def single_player_advanced_batting(player_code: str) -> pl.DataFrame:
#     """Return advanced batting statistics for one player.

#     Args:
#         player_code (str): Baseball Reference player identifier.

#     Returns:
#         pl.DataFrame: Advanced batting statistics.
#     """
#     last_name_initial = player_code[0].lower()
#     with session.get_page() as page:
#         url = BREF_SINGLE_PLAYER_URL.format(
#             initial=last_name_initial, player_code=player_code
#         )
#         page.goto(url, wait_until="domcontentloaded")
#         page.wait_for_selector("#all_players_advanced_batting", timeout=15000)

#         # Get page content
#         content = page.content()
#     soup = BeautifulSoup(content, "html.parser")
#     advanced_batting_table = soup.find("div", {"id": "all_players_advanced_batting"})
#     assert advanced_batting_table is not None, (
#         "Failed to retrieve advanced batting table"
#     )
#     advanced_batting_table = advanced_batting_table.find("table")
#     advanced_batting_df = pl.DataFrame(_extract_table(advanced_batting_table))

#     advanced_batting_df = advanced_batting_df.select(
#         pl.all().name.map(lambda col_name: col_name.replace("b_", ""))
#     )

#     advanced_batting_df = advanced_batting_df.select(
#         pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
#     )
#     advanced_batting_df = advanced_batting_df.with_columns(
#         pl.col("gperc").alias("gb_perc"),
#         pl.col("fperc").alias("fb_perc"),
#         pl.col("gfratio").alias("gb_fb_ratio"),
#     ).drop(["gperc", "fperc", "gfratio"])

#     return advanced_batting_df


def single_player_standard_fielding(player_code: str) -> pl.DataFrame:
    """Return standard fielding statistics for one player.

    Args:
        player_code (str): Baseball Reference player identifier.

    Returns:
        pl.DataFrame: Standard fielding statistics.
    """
    last_name_initial = player_code[0].lower()
    with session.get_page() as page:
        url = BREF_SINGLE_PLAYER_URL.format(
            initial=last_name_initial, player_code=player_code
        )
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_selector("#all_players_standard_fielding", timeout=15000)
        html = page.content()
        assert html is not None, "Failed to retrieve HTML content"
        soup = BeautifulSoup(html, "html.parser")
    table_wrapper = soup.find("div", {"id": "div_players_standard_fielding"})
    assert table_wrapper is not None, "Failed to retrieve standard fielding table"
    table = table_wrapper.find("table")
    standard_fielding_df = pl.DataFrame(_extract_table(table))
    standard_fielding_df = standard_fielding_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("f_", ""))
    )
    standard_fielding_df = standard_fielding_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
    )
    return standard_fielding_df


def single_player_sabermetric_fielding(player_code: str) -> pl.DataFrame:
    """Return sabermetric fielding statistics for one player.

    Args:
        player_code (str): Baseball Reference player identifier.

    Returns:
        pl.DataFrame: Sabermetric fielding statistics.
    """
    last_name_initial = player_code[0].lower()
    with session.get_page() as page:
        page.goto(
            BREF_SINGLE_PLAYER_SABERMETRIC_FIELDING_URL.format(
                initial=last_name_initial, player_code=player_code
            ),
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#div_advanced_fielding", timeout=15000)
        html = page.content()
        assert html is not None, "Failed to retrieve HTML content"
        soup = BeautifulSoup(html, "html.parser")
    sabermetric_fielding_table = soup.find("div", {"id": "div_advanced_fielding"})
    assert sabermetric_fielding_table is not None, (
        "Failed to retrieve sabermetric fielding table"
    )
    sabermetric_fielding_table = sabermetric_fielding_table.find("table")
    sabermetric_fielding_df = pl.DataFrame(_extract_table(sabermetric_fielding_table))
    sabermetric_fielding_df = sabermetric_fielding_df.fill_null(0)
    return sabermetric_fielding_df


def single_player_standard_pitching(player_code: str) -> pl.DataFrame:
    """Return standard pitching statistics for one player.

    Args:
        player_code (str): Baseball Reference player identifier.

    Returns:
        pl.DataFrame: Standard pitching statistics.
    """
    last_name_initial = player_code[0].lower()
    with session.get_page() as page:
        page.goto(
            BREF_SINGLE_PLAYER_URL.format(
                initial=last_name_initial, player_code=player_code
            ),
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#all_players_standard_pitching", timeout=15000)
        html = page.content()
        assert html is not None, "Failed to retrieve HTML content"
        soup = BeautifulSoup(html, "html.parser")
    standard_pitching_table_wrapper = soup.find(
        "div", {"id": "div_players_standard_pitching"}
    )
    assert standard_pitching_table_wrapper is not None, (
        "Failed to retrieve standard pitching table wrapper"
    )
    standard_pitching_table = standard_pitching_table_wrapper.find("table")
    assert standard_pitching_table is not None, (
        "Failed to retrieve standard pitching table"
    )
    standard_pitching_df = pl.DataFrame(_extract_table(standard_pitching_table))
    standard_pitching_df = standard_pitching_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("p_", ""))
    )
    standard_pitching_df = standard_pitching_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
    )
    return standard_pitching_df


def single_player_value_pitching(player_code: str) -> pl.DataFrame:
    """Return value pitching statistics for one player.

    Args:
        player_code (str): Baseball Reference player identifier.

    Returns:
        pl.DataFrame: Value pitching statistics.
    """
    last_name_initial = player_code[0].lower()
    with session.get_page() as page:
        page.goto(
            BREF_SINGLE_PLAYER_URL.format(
                initial=last_name_initial, player_code=player_code
            ),
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#div_players_value_pitching", timeout=15000)
        value_pitching_table_wrapper = page.query_selector(
            "#div_players_value_pitching"
        )
        html = value_pitching_table_wrapper.inner_html()
        assert html is not None, "Failed to retrieve HTML content"
        soup = BeautifulSoup(html, "html.parser")
    value_pitching_table = soup.find("table")
    value_pitching_df = pl.DataFrame(_extract_table(value_pitching_table))
    value_pitching_df = value_pitching_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("p_", ""))
    )
    value_pitching_df = value_pitching_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
    )
    return value_pitching_df


def single_player_advanced_pitching(player_code: str) -> pl.DataFrame:
    """Return advanced pitching statistics for one player.

    Args:
        player_code (str): Baseball Reference player identifier.

    Returns:
        pl.DataFrame: Advanced pitching statistics.
    """
    last_name_initial = player_code[0].lower()
    with session.get_page() as page:
        page.goto(
            BREF_SINGLE_PLAYER_URL.format(
                initial=last_name_initial, player_code=player_code
            ),
            wait_until="domcontentloaded",
        )
        page.wait_for_selector("#div_players_advanced_pitching", timeout=15000)
        advanced_pitching_table_wrapper = page.query_selector(
            "#div_players_advanced_pitching"
        )
        html = advanced_pitching_table_wrapper.inner_html()
        assert html is not None, "Failed to retrieve HTML content"
        soup = BeautifulSoup(html, "html.parser")
    advanced_pitching_table = soup.find("table")
    advanced_pitching_df = pl.DataFrame(_extract_table(advanced_pitching_table))

    advanced_pitching_df = advanced_pitching_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("p_", ""))
    )
    advanced_pitching_df = advanced_pitching_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
    )
    return advanced_pitching_df
