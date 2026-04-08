import polars as pl
from bs4 import BeautifulSoup

from pybaseballstats.consts.bref_consts import (
    BREF_TEAMS_BATTING_BASE_URL,
    BREF_TEAMS_ROSTER_URL,
    BREF_TEAMS_SCHEDULE_RESULTS_URL,
    BREFTeams,
)
from pybaseballstats.utils.bref_utils import (
    BREFSession,
    _extract_table,
    resolve_bref_team_code,
)

session = BREFSession.instance()  # type: ignore[attr-defined]

__all__ = [
    "BREFTeams",
    "game_by_game_schedule_results",
    "roster_and_appearances",
    "standard_batting",
    "value_batting",
    "advanced_batting",
    "sabermetric_batting",
    "ratio_batting",
    "win_probability_batting",
    "baserunning_batting",
    "situational_batting",
    "pitches_batting",
    "career_cumulative_batting",
]


# region random functions
# TODO: return results with converted dtypes and cleaned columns (e.g., opponent team code, home/away status, etc.)
def game_by_game_schedule_results(team: BREFTeams, year: int) -> pl.DataFrame:
    """Return game-by-game schedule/results for a team season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the page request fails.
        ValueError: If the schedule/results table is not found.

    Returns:
        pl.DataFrame: Team schedule and results rows from Baseball Reference.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    team_code = resolve_bref_team_code(team=team, year=year)
    url = BREF_TEAMS_SCHEDULE_RESULTS_URL.format(team_code=team_code, year=year)
    resp = session.get(url)
    if resp is None:
        print(url)
        raise ValueError(f"Failed to fetch data for {team.name} in {year}.")

    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find("table", id="team_schedule")
    if table is None:
        raise ValueError(f"No schedule/results table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop(
        "boxscore"
    )  # drop boxscore column since it just has a link to the boxscore page which isn't useful for our purposes
    return df


# TODO: return results with converted dtypes and cleaned columns (e.g., position, games played/started as int, etc.)
def roster_and_appearances(team: BREFTeams, year: int) -> pl.DataFrame:
    """Return roster and appearances data for a team season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        AssertionError: If the roster/appearances table is not found.

    Returns:
        pl.DataFrame: Team roster and appearances rows from Baseball Reference.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    team_code = resolve_bref_team_code(team=team, year=year)
    with session.get_page() as page:
        page.goto(
            BREF_TEAMS_ROSTER_URL.format(team_code=team_code, year=year),
        )
        # page.wait_for_selector("#appearances > tbody")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    print(
        BREF_TEAMS_ROSTER_URL.format(team_code=team_code, year=year),
    )
    table = soup.find("table", id="appearances")
    assert table is not None, (
        f"No roster/appearances table found for {team.name} in {year}."
    )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")
    return df


# endregion


# region batting functions
def standard_batting(team: BREFTeams, year: int):
    """Return standard team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the page request fails.
        ValueError: If the standard batting table is not found.

    Returns:
        pl.DataFrame: Standard batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    resp = session.get(url)
    if resp is None:
        raise ValueError(f"Failed to fetch data for {team.name} in {year}.")
    soup = BeautifulSoup(resp.content, "html.parser")
    table = soup.find("table", id="players_standard_batting")
    if table is None:
        raise ValueError(f"No standard batting table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")  # drop index column
    df = df.with_columns(
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
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    return df


def value_batting(team: BREFTeams, year: int):
    """Return value team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the value batting table is not found.

    Returns:
        pl.DataFrame: Value batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
    soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_value_batting")
    if table is None:
        raise ValueError(f"No value batting table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")  # drop index column
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.with_columns(
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
    return df


def advanced_batting(team: BREFTeams, year: int):
    """Return advanced team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the advanced batting table is not found.

    Returns:
        pl.DataFrame: Advanced batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_advanced_batting")
    if table is None:
        raise ValueError(f"No advanced batting table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.drop("ranker")  # drop index column
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))

    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.with_columns(
        pl.col(["age", "pa", "rbat_plus"]).cast(pl.Int32),
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
    df = df.filter(pl.col("name_display") != "League Average")
    return df


def sabermetric_batting(team: BREFTeams, year: int):
    """Return sabermetric team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the sabermetric batting table is not found.

    Returns:
        pl.DataFrame: Sabermetric batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_sabermetric_batting")
    if table is None:
        raise ValueError(
            f"No sabermetric batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    int_cols = [
        "age",
        "PA",
        "outs_made",
        "RC",
        "batter_air",
        "onbase_plus_slugging_plus",
    ]
    float_cols = [
        "RCpG",
        "batting_avg_bip",
        "batting_avg",
        "batting_avg_lg",
        "onbase_perc",
        "onbase_perc_lg",
        "slugging_perc",
        "slugging_perc_lg",
        "onbase_plus_slugging",
        "onbase_plus_slugging_lg",
        "offensive_winning_perc",
        "abRuns",
        "abWins",
        "total_avg",
        "secondary_avg",
        "isolated_slugging_perc",
        "power_speed_number",
    ]
    df = df.with_columns(
        pl.col(int_cols).cast(pl.Int32),
        pl.col(float_cols).cast(pl.Float32),
    )
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    return df


def ratio_batting(team: BREFTeams, year: int):
    """Return ratio team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the ratio batting table is not found.

    Returns:
        pl.DataFrame: Ratio batting table with typed numeric and percent columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_ratio_batting")
    if table is None:
        raise ValueError(f"No ratio batting table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    int_cols = ["age", "PA"]
    float_cols = [
        "strikeouts_per_base_on_balls",
        "at_bats_per_strikeout",
        "at_bats_per_home_run",
        "at_bats_per_rbi",
        "gfratio",
        "go_ao_ratio",
    ]
    df = df.with_columns(
        pl.col(int_cols).cast(pl.Int32),
        pl.col(float_cols).cast(pl.Float32),
    )
    perc_cols = [col for col in df.columns if "perc" in col or "percentage" in col]
    df = df.with_columns(pl.col(perc_cols).str.replace("%", "").cast(pl.Float32))
    df = df.filter(pl.col("player") != "League Average")
    return df


def win_probability_batting(team: BREFTeams, year: int):
    """Return win-probability team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the win probability batting table is not found.

    Returns:
        pl.DataFrame: Win probability batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_win_probability_batting")
    if table is None:
        raise ValueError(
            f"No win probability batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    df = df.filter(pl.col("player") != "League Average")
    int_cols = ["age", "PA", "wpa_plays", "PH_ab"]
    float_cols = [
        "abRuns",
        "abWins",
        "wpa_bat",
        "wpa_bat_pos",
        "wpa_bat_neg",
        "leverage_index_avg",
        "wpa_li_bat",
        "wpa_clutch",
        "cli_avg",
        "re24_bat",
        "rew_bat",
        "bo_leverage_index_avg",
        "re24_boli",
        "PH_leverage",
    ]
    df = df.with_columns(
        pl.col(int_cols).cast(pl.Int32),
        pl.col(float_cols).cast(pl.Float32),
    )
    perc_cols = ["cwpa_bat_neg", "cwpa_bat_pos", "cwpa_clutch", "cwpa_bat"]
    df = df.with_columns(pl.col(perc_cols).str.replace("%", "").cast(pl.Float32))
    return df


def baserunning_batting(team: BREFTeams, year: int):
    """Return baserunning team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the baserunning batting table is not found.

    Returns:
        pl.DataFrame: Baserunning batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_baserunning_batting")
    if table is None:
        raise ValueError(
            f"No baserunning batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    # df = df.drop("ranker")  # drop index column
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    int_cols = [
        "age",
        "PA",
        "ROE",
        "XI",
        "SB_opp",
        "SB",
        "CS",
        "SB_2",
        "CS_2",
        "SB_3",
        "CS_3",
        "SB_H",
        "CS_H",
        "pickoffs",
        "POCS",
        "outs_on_base",
        "outs_on_base_1",
        "outs_on_base_2",
        "outs_on_base_3",
        "outs_on_base_h",
        "bases_taken",
        "on_first_single",
        "on_first_single_12",
        "on_first_single_13",
        "on_first_double",
        "on_first_double_13",
        "on_first_double_1H",
        "on_second_single",
        "on_second_single_23",
        "on_second_single_2H",
    ]

    perc_cols = ["runs_scored_perc", "stolen_base_perc", "extra_bases_taken_perc"]
    df = df.with_columns(
        pl.col(int_cols).cast(pl.Int32),
        pl.col(perc_cols).str.replace("%", "").cast(pl.Float32),
    )
    df = df.filter(pl.col("player") != "League Average")
    return df


def situational_batting(team: BREFTeams, year: int):
    """Return situational team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the situational batting table is not found.

    Returns:
        pl.DataFrame: Situational batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_situational_batting")
    if table is None:
        raise ValueError(
            f"No situational batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    int_cols = [
        "age",
        "PA_pbp",
        "H_all",
        "H_inf",
        "H_bunt",
        "PH_ab",
        "PH_h",
        "PH_hr",
        "PH_rbi",
        "HR_all",
        "HR_gs",
        "HR_gs_opp",
        "HR_vrh",
        "HR_vlh",
        "HR_hm",
        "HR_rd",
        "HR_iphr",
        "SH_att",
        "SH_suc",
        "GIDP_opp",
        "GIDP_suc",
        "productive_outs_opp",
        "productive_outs",
        "baserunners_tot",
        "drove_in_tot",
        "lt_2_out_on_third_opp",
        "lt_2_out_on_third_scored",
        "no_out_on_second_opp",
        "no_out_on_second_adv",
        "PA_unknown",
    ]
    float_cols = ["PH_leverage"]
    perc_cols = [
        "GIDP_perc",
        "lt_2_out_on_third_perc",
        "baserunners_scored_perc",
        "PA_with_platoon_adv_perc",
        "SH_perc",
        "productive_outs_perc",
        "no_out_on_second_perc",
    ]
    df = df.with_columns(
        pl.col(int_cols).cast(pl.Int32),
        pl.col(float_cols).cast(pl.Float32),
        pl.col(perc_cols).str.replace("%", "").cast(pl.Float32),
    )
    df = df.filter(pl.col("player") != "League Average")
    return df


def pitches_batting(team: BREFTeams, year: int):
    """Return pitches/plate-discipline team batting statistics for one season.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the pitches batting table is not found.

    Returns:
        pl.DataFrame: Pitches batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_pitches_batting")
    if table is None:
        raise ValueError(f"No pitches batting table found for {team.name} in {year}.")
    data = _extract_table(table)
    df = pl.DataFrame(data)
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    int_cols = [
        "age",
        "PA_pitch",
        "pitches",
        "strikes_total",
        "30_pitches",
        "30_swings",
        "20_pitches",
        "20_swings",
        "31_pitches",
        "31_swings",
        "SO_looking",
        "SO_swinging",
        "PA_unknown",
        "pitches_unknown",
        "strikes_unknown",
    ]
    float_cols = ["pitches_per_pa"]
    perc_cols = [
        "strike_foul_perc",
        "first_pitch_swings_perc",
        "strike_inplay_perc",
        "30_pitches_perc",
        "strike_swinging_perc",
        "strike_looking_perc",
        "contact_perc",
        "31_pitches_perc",
        "strike_perc",
        "20_pitches_perc",
        "all_strikes_swinging_perc",
        "SO_looking_perc",
        "ball_intent_perc",
        "pitches_swinging_perc",
    ]
    df = df.filter(pl.col("player") != "League Average")
    df = df.with_columns(
        pl.col(int_cols).cast(pl.Int32),
        pl.col(float_cols).cast(pl.Float32),
        pl.col(perc_cols).str.replace("%", "").cast(pl.Float32),
    )
    return df


def career_cumulative_batting(team: BREFTeams, year: int):
    """Return cumulative career batting summaries for the team roster.

    Args:
        team (BREFTeams): Team enum value.
        year (int): MLB season year.

    Raises:
        ValueError: If ``team`` is not a ``BREFTeams`` value.
        ValueError: If the cumulative batting table is not found.

    Returns:
        pl.DataFrame: Cumulative batting table with typed numeric columns.
    """
    if not isinstance(team, BREFTeams):
        raise ValueError("Team must be a member of the BREFTeams enum")
    url = BREF_TEAMS_BATTING_BASE_URL.format(
        team_code=resolve_bref_team_code(team, year=year), year=year
    )
    with session.get_page() as page:
        page.goto(url, wait_until="networkidle")
        content = page.content()
        soup = BeautifulSoup(content, "html.parser")
    table = soup.find("table", id="players_cumulative_batting")
    if table is None:
        raise ValueError(
            f"No cumulative batting table found for {team.name} in {year}."
        )
    data = _extract_table(table)
    df = pl.DataFrame(data)
    int_cols = [
        "age",
        "seasons",
        "G",
        "PA",
        "AB",
        "R",
        "H",
        "2B",
        "3B",
        "HR",
        "RBI",
        "SB",
        "CS",
        "BB",
        "SO",
        "onbase_plus_slugging_plus",
        "TB",
        "GIDP",
        "HBP",
        "SH",
        "SF",
        "IBB",
    ]
    float_cols = ["batting_avg", "onbase_perc", "slugging_perc", "onbase_plus_slugging"]
    df = df.with_columns(
        pl.col(int_cols).cast(pl.Int32),
        pl.col(float_cols).cast(pl.Float32),
    )
    return df


# TODO: pitching, fielding, def lineups, batting orders,
