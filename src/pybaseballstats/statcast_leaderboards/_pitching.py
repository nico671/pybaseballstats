import io
from datetime import datetime
from typing import List, Literal

import polars as pl
import requests

from pybaseballstats._consts.statcast_leaderboard_consts import (
    ACTIVE_SPIN_LEADERBOARD_URL,
    ARM_ANGLE_LEADERBOARD_URL,
    PITCH_ARSENALS_LEADERBOARD_URL,
    PITCH_MOVEMENT_LEADERBOARD_URL,
    PITCHER_RUNNING_GAME_LEADERBOARD_URL,
    SPIN_DIRECTION_LEADERBOARD_URL,
    StatcastLeaderboardsTeams,
)


def spin_direction_leaderboard(
    season: int | str = "ALL",
    team: StatcastLeaderboardsTeams | None = None,
    pitch_type: Literal[
        "FF", "CH", "CU", "FC", "FO", "KN", "SC", "SI", "SL", "SV", "FS", "ST", "ALL"
    ] = "ALL",
    pitcher_handedness: Literal["R", "L", "ALL"] = "ALL",
    min_pitches: int | str = "q",
) -> pl.DataFrame:
    """Return Baseball Savant spin direction leaderboard data.

    Retrieve pitcher spin direction data from Baseball Savant, which provides insight
    into how pitchers impart spin axis direction on their pitches.

    Args:
        season (int | str): Season year between 2020 and current year, or ``"ALL"`` for all available years.
        team (StatcastLeaderboardsTeams | None, optional): Optional team filter. Defaults to ``None``.
        pitch_type (Literal[...]): Pitch type filter. Options: ``FF`` (Four-Seam Fastball),
            ``SI`` (Sinker), ``FC`` (Cut Fastball), ``CH`` (Changeup), ``FS`` (Splitter),
            ``FO`` (Forkball), ``SC`` (Screwball), ``CU`` (Curveball), ``SL`` (Slider),
            ``ST`` (Sweeper), ``SV`` (Slurve), ``KN`` (Knuckleball), or ``"ALL"`` for all pitch types.
            Defaults to ``"ALL"``.
        pitcher_handedness (Literal["R", "L", "ALL"], optional): ``"R"`` for right-handed,
            ``"L"`` for left-handed, ``"ALL"`` for both. Defaults to ``"ALL"``.
        min_pitches (int | str, optional): Minimum pitch count threshold. Can be a positive integer
            or ``"q"`` for Baseball Savant's qualifying threshold. Defaults to ``"q"``.

    Returns:
        pl.DataFrame: Spin direction leaderboard data with columns including player name,
            spin direction metrics, and pitch-specific statistics.

    Raises:
        ValueError: If ``season`` is not an integer between 2020 and current year or ``"ALL"``.
        ValueError: If ``pitch_type`` is not a valid pitch type.
        ValueError: If ``pitcher_handedness`` is not ``"R"``, ``"L"``, or ``"ALL"``.
        ValueError: If ``min_pitches`` is not a positive integer or ``"q"``.
        ValueError: If ``team`` is not ``None`` or ``StatcastLeaderboardsTeams``.

    Notes:
        - Data is sourced directly from Baseball Savant via CSV endpoint.
        - Spin direction data has been available since 2020.
        - Column names are standardized with ``last_name, first_name`` renamed to ``player_name``.
    """
    # validate season input, can either be int from 2020 to current year, or "ALL"
    if isinstance(season, int):
        if season < 2020 or season > datetime.now().year:
            raise ValueError(f"season must be between 2020 and {datetime.now().year}")
    elif isinstance(season, str):
        if season != "ALL":
            raise ValueError("season must be an integer or 'ALL'")
    else:
        raise ValueError("season must be an integer or 'ALL'")

    # validate team input, must be an instance of StatcastLeaderboardsTeams or None
    if team is not None and not isinstance(team, StatcastLeaderboardsTeams):
        raise ValueError(
            "team must be an instance of StatcastLeaderboardsTeams or None"
        )
    team_id_param = str(team.value) if team is not None else ""

    # validate pitch_type input, must be one of the specified options
    if pitch_type not in [
        "FF",
        "CH",
        "CU",
        "FC",
        "FO",
        "KN",
        "SC",
        "SI",
        "SL",
        "SV",
        "FS",
        "ST",
        "ALL",
    ]:
        raise ValueError(
            "pitch_type must be one of 'FF', 'CH', 'CU', 'FC', 'FO', 'KN', 'SC', 'SI', 'SL', 'SV', 'FS', 'ST', or 'ALL'"
        )

    # validate pitcher_handedness input, must be one of the specified options
    if pitcher_handedness not in ["R", "L", "ALL"]:
        raise ValueError("pitcher_handedness must be 'R', 'L', or 'ALL'")
    throws_param = pitcher_handedness if pitcher_handedness != "ALL" else ""

    # validate min_pitches input, must be a positive integer or "q"
    if isinstance(min_pitches, int):
        if min_pitches < 1:
            raise ValueError("min_pitches must be a positive integer")
    elif isinstance(min_pitches, str):
        if min_pitches != "q":
            raise ValueError("min_pitches must be a positive integer or 'q'")
    else:
        raise ValueError("min_pitches must be a positive integer or 'q'")
    min_pitches_param = str(min_pitches)

    url = SPIN_DIRECTION_LEADERBOARD_URL.format(
        season=season,
        min_pitches=min_pitches_param,
        pitch_type=pitch_type,
        team_id=team_id_param,
        throws=throws_param,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    df = df.rename({"last_name, first_name": "player_name"})
    return df


def active_spin_leaderboard(
    season: int,
    min_pitches: int = 100,
    stat_method: Literal["spin-based", "observed"] = "spin-based",
    pitcher_handedness: Literal["R", "L", "ALL"] = "ALL",
) -> pl.DataFrame:
    """Return Baseball Savant active spin leaderboard data.

    Retrieve pitcher active spin statistics, which measures the amount of spin imparted
    on a pitch that contributes to actual movement. See the Baseball Savant writeup for details:
    https://baseballsavant.mlb.com/leaderboard/active-spin

    Args:
        season (int): Season year between 2017 and current year.
        min_pitches (int, optional): Minimum pitch count threshold. Must be at least 1.
            Defaults to ``100``.
        stat_method (Literal["spin-based", "observed"], optional): Calculation method for active spin.
            ``"spin-based"`` uses advanced spin modeling (available from 2020 onwards),
            ``"observed"`` uses direct measurement (available from 2017 onwards).
            Defaults to ``"spin-based"``.
        pitcher_handedness (Literal["R", "L", "ALL"], optional): ``"R"`` for right-handed,
            ``"L"`` for left-handed, ``"ALL"`` for both. Defaults to ``"ALL"``.

    Returns:
        pl.DataFrame: Active spin leaderboard data with pitcher statistics and spin measurements.
            Columns include ``player_name`` and ``player_id`` (renamed from ``entity_name`` and ``entity_id``).

    Raises:
        ValueError: If ``season`` is not between 2017 and current year.
        ValueError: If ``min_pitches`` is less than 1.
        ValueError: If ``stat_method`` is not ``"spin-based"`` or ``"observed"``.
        ValueError: If ``stat_method`` is ``"spin-based"`` but ``season`` is before 2020.
        ValueError: If ``pitcher_handedness`` is not ``"R"``, ``"L"``, or ``"ALL"``.

    Notes:
        - Spin-based calculations are only available from 2020 onwards.
        - Observed spin measurements are available from 2017 onwards.
        - Column names are standardized with ``entity_name`` to ``player_name`` and ``entity_id`` to ``player_id``.
    """
    # validate season input
    if season < 2017 or season > datetime.now().year:
        raise ValueError(f"season must be between 2017 and {datetime.now().year}")
    # validate min_pitches input
    if min_pitches < 1:
        raise ValueError("min_pitches must be at least 1")
    # validate stat_method input
    if stat_method not in ["spin-based", "observed"]:
        raise ValueError("stat_method must be 'spin-based' or 'observed'")
    if stat_method == "spin-based" and season < 2020:
        raise ValueError("spin-based stat_method is only available from 2020 onwards")
    # validate pitcher_handedness input
    if pitcher_handedness not in ["R", "L", "ALL"]:
        raise ValueError("pitcher_handedness must be 'R', 'L', or 'ALL'")

    throws_param = pitcher_handedness if pitcher_handedness != "ALL" else ""
    url = ACTIVE_SPIN_LEADERBOARD_URL.format(
        season=season,
        stat_method=stat_method,
        min_pitches=min_pitches,
        pitcher_handedness=throws_param,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    df = df.rename({"entity_name": "player_name", "entity_id": "player_id"})
    return df


def arm_angle_leaderboard(
    start_date: str = "2020-01-01",
    end_date: str = datetime.today().strftime("%Y-%m-%d"),
    teams: List[StatcastLeaderboardsTeams] | None = None,
    season_type: List[Literal["R", "WC", "DS", "CS", "WS"]] | None = None,
    pitcher_handedness: Literal["R", "L", "ALL"] = "ALL",
    batter_handedness: Literal["R", "L", "ALL"] = "ALL",
    pitch_types: List[
        Literal["FF", "SI", "FC", "CH", "FS", "FO", "SC", "CU", "SL", "ST", "SV", "KN"]
    ]
    | None = None,
    min_pitches: int | str = "q",
    group_by: List[
        Literal[
            "season", "month", "pitch_type", "game_type", "bat_side", "fielding_team"
        ]
    ]
    | None = None,
    min_group_size: int = 1,
) -> pl.DataFrame:
    """Return Baseball Savant arm angle leaderboard data.

    Retrieve pitcher arm angle statistics over a date range with optional filtering
    and grouping. Arm angle affects pitch movement and deception.

    Args:
        start_date (str, optional): Start date in ``YYYY-MM-DD`` format. The earliest possible
            date is ``2020-01-01``. Defaults to ``"2020-01-01"``.
        end_date (str, optional): End date in ``YYYY-MM-DD`` format. Must be after ``start_date``
            and cannot be in the future. Defaults to today's date.
        teams (List[StatcastLeaderboardsTeams] | None, optional): Optional list of teams to filter.
            Defaults to ``None`` (all teams).
        season_type (List[Literal[...]] | None, optional): Season type(s) to include.
            ``R`` = Regular season, ``WC`` = Wild Card, ``DS`` = Divisional Series,
            ``CS`` = Championship Series, ``WS`` = World Series. Defaults to ``None`` (all types).
        pitcher_handedness (Literal["R", "L", "ALL"], optional): ``"R"`` for right-handed,
            ``"L"`` for left-handed, ``"ALL"`` for both. Defaults to ``"ALL"``.
        batter_handedness (Literal["R", "L", "ALL"], optional): ``"R"`` for right-handed batters,
            ``"L"`` for left-handed batters, ``"ALL"`` for both. Defaults to ``"ALL"``.
        pitch_types (List[...] | None, optional): Optional list of pitch types to filter.
            Valid options: ``FF``, ``SI``, ``FC``, ``CH``, ``FS``, ``FO``, ``SC``, ``CU``, ``SL``,
            ``ST``, ``SV``, ``KN``. Defaults to ``None`` (all pitch types).
        min_pitches (int | str, optional): Minimum pitch count threshold. Can be a positive integer
            or ``"q"`` for Baseball Savant's qualifying threshold. Defaults to ``"q"``.
        group_by (List[...] | None, optional): Grouping dimensions (max 4). Options:
            ``"season"``, ``"month"``, ``"pitch_type"``, ``"game_type"``, ``"bat_side"``,
            ``"fielding_team"``. Defaults to ``None`` (no grouping).
        min_group_size (int, optional): Minimum group size threshold. Groups smaller than this
            are filtered out. Must be at least 1. Defaults to ``1``.

    Returns:
        pl.DataFrame: Arm angle leaderboard data with standardized column names.
            Pitch type column (if present) is renamed to ``pitch_type``.
            Month-related columns (if present) are renamed to ``month`` and ``month_num``.

    Raises:
        ValueError: If ``start_date`` or ``end_date`` is not in ``YYYY-MM-DD`` format.
        ValueError: If ``end_date`` is before ``start_date``.
        ValueError: If ``end_date`` is in the future.
        ValueError: If ``teams`` is not a list of ``StatcastLeaderboardsTeams`` or ``None``.
        ValueError: If ``season_type`` is not a valid season type list or ``None``.
        ValueError: If ``pitcher_handedness`` is not ``"R"``, ``"L"``, or ``"ALL"``.
        ValueError: If ``batter_handedness`` is not ``"R"``, ``"L"``, or ``"ALL"``.
        ValueError: If ``pitch_types`` contains invalid pitch type(s).
        ValueError: If ``min_pitches`` is not a positive integer or ``"q"``.
        ValueError: If ``group_by`` contains invalid dimensions or more than 4 items.
        ValueError: If ``min_group_size`` is less than 1.

    Notes:
        - Date range must span from 2020-01-01 onwards (earliest available data).
        - Seasons are automatically inferred from the date range.
        - Data is aggregated across all inferred seasons unless ``group_by`` includes ``"season"``.
    """
    # validate date inputs
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("start_date must be in YYYY-MM-DD format")
    try:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("end_date must be in YYYY-MM-DD format")
    if end_date_obj < start_date_obj:
        raise ValueError("end_date must be after start_date")
    if end_date_obj > datetime.today():
        raise ValueError("end_date cannot be in the future")
    # construct season string as all years included in the date range, separated by |, e.g. 2020|2021|2022
    seasons_inferred = "|".join(
        str(year) for year in range(start_date_obj.year, end_date_obj.year + 1)
    )
    # validate team input
    if teams is not None:
        if not isinstance(teams, list) or not all(
            isinstance(t, StatcastLeaderboardsTeams) for t in teams
        ):
            raise ValueError(
                "teams must be a list of StatcastLeaderboardsTeams enums or None"
            )
        teams_param = "|".join(str(t.value) for t in teams)
    else:
        teams_param = ""

    # validate season_type input
    season_type_mapping = {
        "R": "R",
        "WC": "F",
        "DS": "D",
        "CS": "L",
        "WS": "W",
    }
    if season_type is not None:
        if not isinstance(season_type, list) or not all(
            st in season_type_mapping for st in season_type
        ):
            raise ValueError(
                f"season_type must be a list of the following options or None: {list(season_type_mapping.keys())}"
            )
        season_type_param = "|".join(season_type_mapping[st] for st in season_type)
    else:
        season_type_param = ""

    # validate pitcher_handedness input
    if pitcher_handedness not in ["R", "L", "ALL"]:
        raise ValueError("pitcher_handedness must be 'R', 'L', or 'ALL'")
    throws_param = pitcher_handedness if pitcher_handedness != "ALL" else ""

    # validate batter_handedness input
    if batter_handedness not in ["R", "L", "ALL"]:
        raise ValueError("batter_handedness must be 'R', 'L', or 'ALL'")
    bat_side_param = batter_handedness if batter_handedness != "ALL" else ""
    # validate pitch_type input
    valid_pitch_types = [
        "FF",
        "SI",
        "FC",
        "CH",
        "FS",
        "FO",
        "SC",
        "CU",
        "SL",
        "ST",
        "SV",
        "KN",
    ]
    if pitch_types is not None:
        if not isinstance(pitch_types, list) or not all(
            pt in valid_pitch_types for pt in pitch_types
        ):
            raise ValueError(
                f"pitch_types must be a list of the following options or None: {valid_pitch_types}"
            )
        pitch_types_param = "|".join(pitch_types)
    else:
        pitch_types_param = ""

    # validate min_pitches input
    if isinstance(min_pitches, int):
        if min_pitches < 1:
            raise ValueError("min_pitches must be at least 1")
        min_pitches_param = str(min_pitches)
    elif isinstance(min_pitches, str):
        if min_pitches != "q":
            raise ValueError("min_pitches must be a positive integer or 'q'")
        min_pitches_param = min_pitches
    else:
        raise ValueError("min_pitches must be a positive integer or 'q'")

    # validate group_by input
    group_by_mapping = {
        "season": "year",
        "month": "api_game_date_month_text",
        "pitch_type": "api_pitch_type_group03",
        "game_type": "game_type",
        "bat_side": "bat_side",
        "fielding_team": "fld_team_id",
    }
    if group_by is not None:
        if not isinstance(group_by, list) or not all(
            gb in group_by_mapping for gb in group_by
        ):
            raise ValueError(
                f"group_by must be a list of the following options or None: {list(group_by_mapping.keys())}"
            )
        if len(group_by) > 4:
            raise ValueError("group_by cannot have more than 4 options")
        group_by_param = "|".join(group_by_mapping[gb] for gb in group_by)
    else:
        group_by_param = ""

    # validate min_group_size input
    if min_group_size < 1:
        raise ValueError("min_group_size must be at least 1")

    url = ARM_ANGLE_LEADERBOARD_URL.format(
        bat_side=bat_side_param,
        start_date=start_date,
        end_date=end_date,
        game_type=season_type_param,
        group_by=group_by_param,
        min_total_pitches=min_pitches_param,
        min_group_size=min_group_size,
        pitch_hand=throws_param,
        pitch_type=pitch_types_param,
        team=teams_param,
        seasons_inferred=seasons_inferred,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    if "api_pitch_type_group03" in df.columns:
        df = df.rename({"api_pitch_type_group03": "pitch_type"})
    if "api_game_date_month_text" in df.columns:
        df = df.rename(
            {"api_game_date_month_text": "month", "api_game_date_month_mm": "month_num"}
        )
    return df


def pitch_arsenals_leaderboard(
    season: int = 2026,
    metric_type: Literal["avg_speed", "usage_percentage", "avg_spin"] = "avg_speed",
    pitcher_handedness: Literal["R", "L", "ALL"] = "ALL",
    min_pitches: int | str = "q",
) -> pl.DataFrame:
    """Return Baseball Savant pitch arsenal leaderboard data.

    Retrieve pitcher arsenal statistics including pitch velocities, usage percentages,
    or spin rates across different pitch types.

    Args:
        season (int, optional): Season year between 2008 and current year. Defaults to ``2026``.
        metric_type (Literal["avg_speed", "usage_percentage", "avg_spin"], optional):
            Metric to retrieve: ``"avg_speed"`` for average velocity, ``"usage_percentage"``
            for pitch type usage distribution, ``"avg_spin"`` for average spin rate.
            Defaults to ``"avg_speed"``.
        pitcher_handedness (Literal["R", "L", "ALL"], optional): ``"R"`` for right-handed,
            ``"L"`` for left-handed, ``"ALL"`` for both. Defaults to ``"ALL"``.
        min_pitches (int | str, optional): Minimum pitch count threshold. Can be a positive integer
            or ``"q"`` for Baseball Savant's qualifying threshold. Defaults to ``"q"``.

    Returns:
        pl.DataFrame: Pitch arsenal leaderboard data. Column names are standardized with
            ``last_name, first_name`` renamed to ``player_name`` and ``pitcher`` renamed to ``player_id``.
            When ``metric_type`` is ``"usage_percentage"``, pitch type columns are converted to percentage columns.

    Raises:
        ValueError: If ``season`` is not between 2008 and current year.
        ValueError: If ``metric_type`` is not one of the valid options.
        ValueError: If ``pitcher_handedness`` is not ``"R"``, ``"L"``, or ``"ALL"``.
        ValueError: If ``min_pitches`` is not a positive integer or ``"q"``.

    Notes:
        - Data availability starts from 2008 for all metric types.
        - Usage percentage metrics are calculated as percentages across all pitch types thrown.
        - Column names are automatically standardized after retrieval.
    """
    # validate season input
    if season < 2008 or season > datetime.now().year:
        raise ValueError(f"season must be between 2008 and {datetime.now().year}")
    # validate metric_type input
    if metric_type not in ["avg_speed", "usage_percentage", "avg_spin"]:
        raise ValueError(
            "metric_type must be 'avg_speed', 'usage_percentage', or 'avg_spin'"
        )
    # validate pitcher_handedness input
    if pitcher_handedness not in ["R", "L", "ALL"]:
        raise ValueError("pitcher_handedness must be 'R', 'L', or 'ALL'")
    throws_param = pitcher_handedness if pitcher_handedness != "ALL" else ""
    # validate min_pitches input
    if isinstance(min_pitches, int):
        if min_pitches < 1:
            raise ValueError("min_pitches must be at least 1")
        min_pitches_param = str(min_pitches)
    elif isinstance(min_pitches, str):
        if min_pitches != "q":
            raise ValueError("min_pitches must be a positive integer or 'q'")
        min_pitches_param = min_pitches
    else:
        raise ValueError("min_pitches must be a positive integer or 'q'")

    url = PITCH_ARSENALS_LEADERBOARD_URL.format(
        year=season,
        metric_type=metric_type if metric_type != "usage_percentage" else "n_",
        pitcher_handedness=throws_param,
        min_pitches=min_pitches_param,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    df = df.rename({"last_name, first_name": "player_name", "pitcher": "player_id"})
    if metric_type == "usage_percentage":
        for col in df.columns:
            if col.startswith("n_"):
                new_col_name = col[2:] + "_usage_percentage"
                df = df.rename({col: new_col_name})
                df = df.with_columns(
                    pl.col(new_col_name).str.replace("", "0").cast(pl.Float64)
                )
    return df


def pitch_movement_leaderboard(
    season: int = 2026,
    pitch_type: Literal[
        "FF", "CH", "CU", "FC", "FO", "KN", "SC", "SI", "SL", "SV", "FS", "ST", "ALL"
    ] = "ALL",
    pitcher_handedness: Literal["R", "L", "ALL"] = "ALL",
    min_pitches: int | str = "q",
) -> pl.DataFrame:
    """Return Baseball Savant pitch movement leaderboard data.

    Retrieve pitcher pitch movement statistics, which measure vertical and horizontal
    break induced by spin and other factors.

    Args:
        season (int, optional): Season year between 2017 and current year. Defaults to ``2026``.
        pitch_type (Literal[...]): Pitch type filter. Options: ``FF`` (Four-Seam Fastball),
            ``SI`` (Sinker), ``FC`` (Cut Fastball), ``CH`` (Changeup), ``FS`` (Splitter),
            ``FO`` (Forkball), ``SC`` (Screwball), ``CU`` (Curveball), ``SL`` (Slider),
            ``ST`` (Sweeper), ``SV`` (Slurve), ``KN`` (Knuckleball), or ``"ALL"`` for all pitch types.
            Defaults to ``"ALL"``.
        pitcher_handedness (Literal["R", "L", "ALL"], optional): ``"R"`` for right-handed,
            ``"L"`` for left-handed, ``"ALL"`` for both. Defaults to ``"ALL"``.
        min_pitches (int | str, optional): Minimum pitch count threshold. Can be a positive integer
            or ``"q"`` for Baseball Savant's qualifying threshold. Defaults to ``"q"``.

    Returns:
        pl.DataFrame: Pitch movement leaderboard data with pitcher statistics and movement metrics.
            Column names are standardized with ``last_name, first_name`` renamed to ``player_name``.

    Raises:
        ValueError: If ``season`` is not between 2017 and current year.
        ValueError: If ``pitch_type`` is not a valid pitch type or ``"ALL"``.
        ValueError: If ``pitcher_handedness`` is not ``"R"``, ``"L"``, or ``"ALL"``.
        ValueError: If ``min_pitches`` is not a positive integer or ``"q"``.

    Notes:
        - Pitch movement data has been available since 2017.
        - Movement metrics typically include induced vertical break (IVB) and horizontal break (HB).
        - Column names are standardized with ``last_name, first_name`` renamed to ``player_name``.
    """
    # validate season input
    if season < 2017 or season > datetime.now().year:
        raise ValueError(f"season must be between 2017 and {datetime.now().year}")
    # validate pitch_type input
    valid_pitch_types = [
        "FF",
        "SI",
        "FC",
        "CH",
        "FS",
        "FO",
        "SC",
        "CU",
        "SL",
        "ST",
        "SV",
        "KN",
        "ALL",
    ]
    if pitch_type not in valid_pitch_types:
        raise ValueError(
            f"pitch_type must be one of the following options: {valid_pitch_types}"
        )
    # validate pitcher_handedness input
    if pitcher_handedness not in ["R", "L", "ALL"]:
        raise ValueError("pitcher_handedness must be 'R', 'L', or 'ALL'")
    throws_param = pitcher_handedness if pitcher_handedness != "ALL" else ""
    # validate min_pitches input
    if isinstance(min_pitches, int):
        if min_pitches < 1:
            raise ValueError("min_pitches must be at least 1")
        min_pitches_param = str(min_pitches)
    elif isinstance(min_pitches, str):
        if min_pitches != "q":
            raise ValueError("min_pitches must be a positive integer or 'q'")
        min_pitches_param = min_pitches
    else:
        raise ValueError("min_pitches must be a positive integer or 'q'")

    url = PITCH_MOVEMENT_LEADERBOARD_URL.format(
        season=season,
        pitch_type=pitch_type,
        pitcher_handedness=throws_param,
        min_pitches=min_pitches_param,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    df = df.rename({"last_name, first_name": "player_name"})
    return df


def pitcher_running_game_leaderboard(
    start_season: int,
    end_season: int,
    game_type: Literal["Regular", "Playoff", "All"] = "All",
    group_by: Literal["Pit", "Pitching Team", "League"] = "Pit",
    pitcher_handedness: Literal["R", "L", "ALL"] = "ALL",
    runner_movement: Literal["All", "Advance", "Out", "Hold"] = "All",
    target_base: Literal["All", "2B", "3B"] = "All",
    num_prior_disengagements: Literal["All", "0", "1", "2", "3+"] = "All",
    min_sb_opportunities: int | str = "q",
    team: StatcastLeaderboardsTeams | str = "All",
    split_years: bool = False,
) -> pl.DataFrame:
    """Return Baseball Savant pitcher running game leaderboard data.

    Retrieve pitcher statistics related to runner movement, stolen base prevention,
    and pitcher engagement with baserunners.

    Args:
        start_season (int): Starting season year (2016 or later).
        end_season (int): Ending season year (must be >= ``start_season``).
        game_type (Literal["Regular", "Playoff", "All"], optional): Game type filter.
            ``"Regular"`` = regular season, ``"Playoff"`` = playoff games, ``"All"`` = both.
            Defaults to ``"All"``.
        group_by (Literal["Pit", "Pitching Team", "League"], optional): Aggregation level.
            ``"Pit"`` = individual pitcher, ``"Pitching Team"`` = aggregate by pitching team,
            ``"League"`` = aggregate by league. Defaults to ``"Pit"``.
        pitcher_handedness (Literal["R", "L", "ALL"], optional): ``"R"`` for right-handed,
            ``"L"`` for left-handed, ``"ALL"`` for both. Defaults to ``"ALL"``.
        runner_movement (Literal["All", "Advance", "Out", "Hold"], optional): Filter by runner outcome.
            ``"All"`` = all outcomes, ``"Advance"`` = runners advanced,
            ``"Out"`` = runners thrown out, ``"Hold"`` = runners held. Defaults to ``"All"``.
        target_base (Literal["All", "2B", "3B"], optional): Base being targeted.
            ``"All"`` = both 2nd and 3rd base attempts, ``"2B"`` = 2nd base only,
            ``"3B"`` = 3rd base only. Defaults to ``"All"``.
        num_prior_disengagements (Literal["All", "0", "1", "2", "3+"], optional):
            Number of prior pitcher disengagements (pickoff attempts/throws to base).
            Defaults to ``"All"``.
        min_sb_opportunities (int | str, optional): Minimum stolen base opportunity count.
            Can be a positive integer or ``"q"`` for qualifying threshold. Defaults to ``"q"``.
        team (StatcastLeaderboardsTeams | str, optional): Team filter. Can be a ``StatcastLeaderboardsTeams``
            enum, ``"All"`` for all teams, or ``"All-Split"`` to aggregate by each team a player played for.
            Defaults to ``"All"``.
        split_years (bool, optional): If ``True``, splits results by individual season.
            If ``False``, aggregates across the entire date range. Defaults to ``False``.

    Returns:
        pl.DataFrame: Pitcher running game leaderboard data with runner movement and
            stolen base statistics.

    Raises:
        ValueError: If ``start_season`` is before 2016 or after current year.
        ValueError: If ``end_season`` is before ``start_season`` or after current year.
        ValueError: If ``game_type`` is not one of the valid options.
        ValueError: If ``group_by`` is not ``"Pit"``, ``"Pitching Team"``, or ``"League"``.
        ValueError: If ``pitcher_handedness`` is not ``"R"``, ``"L"``, or ``"ALL"``.
        ValueError: If ``runner_movement`` is not a valid option.
        ValueError: If ``target_base`` is not a valid option.
        ValueError: If ``num_prior_disengagements`` is not a valid option.
        ValueError: If ``min_sb_opportunities`` is not a positive integer or ``"q"``.
        ValueError: If ``team`` is not a valid ``StatcastLeaderboardsTeams``, ``"All"``, or ``"All-Split"``.

    Notes:
        - Data is available from 2016 onwards.
        - The ``"All-Split"`` team option is useful for tracking pitchers who played for multiple teams.
        - Results can be aggregated across years or split by individual season using ``split_years``.
    """
    # validate season inputs
    if start_season < 2016 or start_season > datetime.now().year:
        raise ValueError(f"start_season must be between 2016 and {datetime.now().year}")
    if end_season < start_season or end_season > datetime.now().year:
        raise ValueError(
            f"end_season must be between start_season and {datetime.now().year}"
        )

    # validate game_type input
    if game_type not in ["Regular", "Playoff", "All"]:
        raise ValueError("game_type must be 'Regular', 'Playoff', or 'All'")

    # validate group_by input
    if group_by not in ["Pit", "Pitching Team", "League"]:
        raise ValueError("group_by must be 'Pit', 'Pitching Team', or 'League'")
    group_by_param = ""
    if group_by == "Pitching Team":
        group_by_param = "Pitching+Team"
    else:
        group_by_param = group_by
    # validate pitcher_handedness input
    if pitcher_handedness not in ["R", "L", "ALL"]:
        raise ValueError("pitcher_handedness must be 'R', 'L', or 'ALL'")
    throws_param = pitcher_handedness if pitcher_handedness != "ALL" else "all"

    # validate runner_movement input
    if runner_movement not in ["All", "Advance", "Out", "Hold"]:
        raise ValueError("runner_movement must be 'All', 'Advance', 'Out', or 'Hold'")

    # validate target_base input
    if target_base not in ["All", "2B", "3B"]:
        raise ValueError("target_base must be 'All', '2B', or '3B'")

    # validate num_prior_disengagements input
    if num_prior_disengagements not in ["All", "0", "1", "2", "3+"]:
        raise ValueError(
            "num_prior_disengagements must be 'All', '0', '1', '2', or '3+'"
        )
    num_prior_disengagements_param = (
        num_prior_disengagements if num_prior_disengagements != "3+" else "3"
    )
    min_sb_opportunities_param = ""
    # validate min_sb_opportunities input
    if isinstance(min_sb_opportunities, int):
        if min_sb_opportunities < 1:
            raise ValueError("min_sb_opportunities must be at least 1")
        min_sb_opportunities_param = str(min_sb_opportunities)
    elif isinstance(min_sb_opportunities, str):
        if min_sb_opportunities != "q":
            raise ValueError("min_sb_opportunities must be a positive integer or 'q'")
        min_sb_opportunities_param = min_sb_opportunities
    else:
        raise ValueError("min_sb_opportunities must be a positive integer or 'q'")
    team_param = ""
    if isinstance(team, StatcastLeaderboardsTeams):
        team_param = str(team.value)
    elif isinstance(team, str):
        if team not in ["All", "All-Split"]:
            raise ValueError(
                "team must be an instance of StatcastLeaderboardsTeams or 'All' (all teams) or 'All-Split' (all teams with separate rows for each team a player played for)"
            )
        if team == "All":
            team_param = ""
        elif team == "All-Split":
            team_param = "split"
    else:
        raise ValueError(
            "team must be an instance of StatcastLeaderboardsTeams or 'All' (all teams) or 'All-Split' (all teams with separate rows for each team a player played for)"
        )
    split_years_param = "yes" if split_years else "no"

    url = PITCHER_RUNNING_GAME_LEADERBOARD_URL.format(
        game_type=game_type,
        min_sb_opportunities=min_sb_opportunities_param,
        pitcher_handedness=throws_param,
        runner_movement=runner_movement,
        target_base=target_base,
        num_prior_disengagements=num_prior_disengagements_param,
        end_season=end_season,
        start_season=start_season,
        split_years=split_years_param,
        team=team_param,
        group_by=group_by_param,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    return df
