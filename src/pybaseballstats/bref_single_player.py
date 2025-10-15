import polars as pl
from bs4 import BeautifulSoup

from pybaseballstats.consts.bref_consts import (
    BREF_SINGLE_PLAYER_SABERMETRIC_FIELDING_URL,
    BREF_SINGLE_PLAYER_URL,
)
from pybaseballstats.utils.bref_utils import (
    BREFSession,
    _extract_table,
)

session = BREFSession.instance()  # type: ignore[attr-defined]
__all__ = [
    "single_player_standard_batting",
    "single_player_value_batting",
    "single_player_advanced_batting",
    "single_player_standard_fielding",
    "single_player_sabermetric_fielding",
    "single_player_standard_pitching",
    "single_player_value_pitching",
    "single_player_advanced_pitching",
]


def single_player_standard_batting(player_code: str) -> pl.DataFrame:
    """Returns a DataFrame of a player's standard batting statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.

    Returns:
        pl.DataFrame: A Polars dataframe containing the player's standard batting statistics.
    """
    last_name_initial = player_code[0].lower()
    with session.get_page() as page:
        url = BREF_SINGLE_PLAYER_URL.format(
            initial=last_name_initial, player_code=player_code
        )
        page.goto(url, wait_until="domcontentloaded")
        # Wait for the specific div to be present
        page.wait_for_selector("#all_players_standard_batting", timeout=15000)

        # Get page content
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    standard_stats_table_div = soup.find("div", {"id": "all_players_standard_batting"})
    assert standard_stats_table_div is not None, (
        "Failed to retrieve standard stats table"
    )

    standard_stats_table_actual = standard_stats_table_div.find("table")
    standard_stats_df = pl.DataFrame(_extract_table(standard_stats_table_actual))
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
    return standard_stats_df


def single_player_value_batting(player_code: str) -> pl.DataFrame:
    """Returns a DataFrame of a player's value batting statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.


    Returns:
        pl.DataFrame: A Polars dataframe containing the player's value batting statistics.
    """
    last_name_initial = player_code[0].lower()
    with session.get_page() as page:
        url = BREF_SINGLE_PLAYER_URL.format(
            initial=last_name_initial, player_code=player_code
        )
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_selector("#all_players_value_batting", timeout=15000)

        # Get page content
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    value_batting_table = soup.find("div", {"id": "all_players_value_batting"})
    assert value_batting_table is not None, "Failed to retrieve value batting table"
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
    return value_batting_df


def single_player_advanced_batting(player_code: str) -> pl.DataFrame:
    """Returns a DataFrame of a player's advanced batting statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.

    Returns:
        pl.DataFrame: A Polars dataframe containing the player's advanced batting statistics.
    """
    last_name_initial = player_code[0].lower()
    with session.get_page() as page:
        url = BREF_SINGLE_PLAYER_URL.format(
            initial=last_name_initial, player_code=player_code
        )
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_selector("#all_players_advanced_batting", timeout=15000)

        # Get page content
        content = page.content()
    soup = BeautifulSoup(content, "html.parser")
    advanced_batting_table = soup.find("div", {"id": "all_players_advanced_batting"})
    assert advanced_batting_table is not None, (
        "Failed to retrieve advanced batting table"
    )
    advanced_batting_table = advanced_batting_table.find("table")
    advanced_batting_df = pl.DataFrame(_extract_table(advanced_batting_table))

    advanced_batting_df = advanced_batting_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("b_", ""))
    )

    advanced_batting_df = advanced_batting_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
    )
    advanced_batting_df = advanced_batting_df.with_columns(
        pl.col(["year_id", "age", "pa", "rbat_plus"]).cast(pl.Int32),
        pl.col(
            [
                "roba",
                "batting_avg_bip",
                "iso_slugging",
                "home_run_perc",
                "strikeout_perc",
                "base_on_balls_perc",
                "avg_exit_velo",
                "hard_hit_perc",
                "ld_perc",
                "pull_perc",
                "center_perc",
                "oppo_perc",
                "wpa_bat",
                "baseout_runs",
                "run_scoring_perc",
                "extra_bases_taken_perc",
            ]
        ).cast(pl.Float32),
        pl.col("gperc").cast(pl.Float64).alias("gb_perc"),
        pl.col("fperc").cast(pl.Float64).alias("fb_perc"),
        pl.col("gfratio").cast(pl.Float32).alias("gb_fb_ratio"),
        pl.col("cwpa_bat").str.replace("%", "").cast(pl.Float32),
    ).drop(["gperc", "fperc", "gfratio"])
    advanced_batting_df = advanced_batting_df.with_columns(
        pl.lit(player_code).alias("key_bbref")
    )
    return advanced_batting_df


def single_player_standard_fielding(player_code: str) -> pl.DataFrame:
    """Returns a DataFrame of a player's standard fielding statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.

    Returns:
        pl.DataFrame: A Polars dataframe containing the player's standard fielding statistics.
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
    standard_fielding_df = standard_fielding_df.with_columns(
        pl.col(
            [
                "age",
                "games",
                "games_started",
                "cg",
                "chances",
                "po",
                "assists",
                "errors",
                "dp",
                "tz_runs_total",
                "tz_runs_total_per_year",
                "drs_total",
                "drs_total_per_year",
            ]
        ).cast(pl.Int32),
        pl.col(
            [
                "fielding_perc",
                "innings",
                "fielding_perc_lg",
                "range_factor_per_nine",
                "range_factor_per_nine_lg",
                "range_factor_per_game",
                "range_factor_per_game_lg",
            ]
        ).cast(pl.Float32),
    )
    standard_fielding_df = standard_fielding_df.with_columns(
        pl.lit(player_code).alias("key_bbref")
    )
    return standard_fielding_df


def single_player_sabermetric_fielding(player_code: str) -> pl.DataFrame:
    """Returns a DataFrame of a player's advanced fielding statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.
    Returns:
        pl.DataFrame: A Polars dataframe containing the player's advanced fielding statistics.
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
    sabermetric_fielding_df = sabermetric_fielding_df.with_columns(
        pl.all().exclude(["team_ID", "pos", "lg_ID"]).cast(pl.Int32)
    )
    sabermetric_fielding_df = sabermetric_fielding_df.with_columns(
        pl.lit(player_code).alias("key_bbref")
    )
    return sabermetric_fielding_df


def single_player_standard_pitching(player_code: str) -> pl.DataFrame:
    """Returns a DataFrame of a player's standard pitching statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.

    Returns:
        pl.DataFrame: A Polars DataFrame containing the player's standard pitching statistics.
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
    print(standard_pitching_table.prettify())
    standard_pitching_df = pl.DataFrame(_extract_table(standard_pitching_table))
    standard_pitching_df = standard_pitching_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("p_", ""))
    )
    standard_pitching_df = standard_pitching_df.select(
        pl.all().name.map(lambda col_name: col_name.replace("_abbr", ""))
    )
    standard_pitching_df = standard_pitching_df.with_columns(
        pl.col(
            [
                "age",
                "w",
                "l",
                "g",
                "gs",
                "gf",
                "cg",
                "sho",
                "sv",
                "h",
                "r",
                "er",
                "hr",
                "bb",
                "ibb",
                "so",
                "hbp",
                "bk",
                "wp",
                "bfp",
                "earned_run_avg_plus",
            ]
        ).cast(pl.Int32),
        pl.col(
            [
                "war",
                "win_loss_perc",
                "earned_run_avg",
                "ip",
                "fip",
                "whip",
                "hits_per_nine",
                "hr_per_nine",
                "bb_per_nine",
                "so_per_nine",
                "strikeouts_per_base_on_balls",
            ]
        ).cast(pl.Float32),
    )
    return standard_pitching_df


def single_player_value_pitching(player_code: str) -> pl.DataFrame:
    """Returns a DataFrame of a player's value pitching statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.

    Returns:
        pl.DataFrame : A Polars DataFrame containing the player's value pitching statistics.
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
    value_pitching_df = value_pitching_df.with_columns(
        pl.col(["age", "g", "gs", "r", "ppf_custom", "raa", "rar"]).cast(pl.Int32),
        pl.col(
            [
                "ip",
                "ra9",
                "ra9_opp",
                "ra9_role",
                "ra9_extras",
                "ra9_avg_pitcher",
                "ra9_def",
                "waa",
                "waa_adj",
                "war",
                "waa_win_perc",
                "waa_win_perc_162",
            ]
        ).cast(pl.Float32),
    )
    return value_pitching_df


def single_player_advanced_pitching(player_code: str) -> pl.DataFrame:
    """Returns a DataFrame of a player's advanced pitching statistics.

    Args:
        player_code (str): The player's code from Baseball Reference. This can be found using the pybaseballstats.retrosheet.player_lookup function.

    Returns:
        pl.DataFrame: A polars DataFrame containing the player's advanced pitching statistics.
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
    # allow for float conversions in this column
    advanced_pitching_df = advanced_pitching_df.with_columns(
        pl.col(pl.String).str.replace("%", "")
    )
    advanced_pitching_df = advanced_pitching_df.with_columns(
        pl.col(
            [
                "age",
            ]
        ).cast(pl.Int32),
        pl.col(
            [
                "ip",
                "batting_avg",
                "onbase_perc",
                "slugging_perc",
                "onbase_plus_slugging",
                "batting_avg_bip",
                "home_run_perc",
                "strikeout_perc",
                "base_on_balls_perc",
                "avg_exit_velo",
                "hard_hit_perc",
                "ld_perc",
                "gb_perc",
                "fb_perc",
                "gb_fb_ratio",
                "wpa_def",
                "cwpa_def",
                "baseout_runs",
            ]
        ).cast(pl.Float32),
    )
    return advanced_pitching_df


if __name__ == "__main__":
    df = single_player_standard_pitching("imanash01")
    print(df.columns)
