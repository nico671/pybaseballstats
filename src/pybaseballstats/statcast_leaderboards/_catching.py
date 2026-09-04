import io
from datetime import datetime
from typing import List, Literal

import polars as pl
import requests

from pybaseballstats.consts.statcast_leaderboard_consts import (
    CATCHER_BLOCKING_LEADERBOARD_URL,
    CATCHER_FRAMING_LEADERBOARD_URL,
    CATCHER_STANCE_LEADERBOARD_URL,
    CATCHER_THROWING_LEADERBOARD_URL,
    POPTIME_LEADERBOARD_URL,
    StatcastLeaderboardsTeams,
)


def catcher_blocking_leaderboard(
    start_season: int,
    end_season: int,
    game_type: Literal["Regular", "Playoff", "All"] = "Regular",
    group_by: Literal["Cat", "Pit", "Catching Team", "League"] = "Cat",
    min_pitches: int | str = "q",
    team: StatcastLeaderboardsTeams | str = "All",
    split_years: bool = False,
) -> pl.DataFrame:
    """Return Baseball Savant catcher-blocking leaderboard data.

    Args:
        start_season (int): First season to include. Must be 2018 or later.
        end_season (int): Last season to include. Must not precede ``start_season``.
        game_type (Literal["Regular", "Playoff", "All"], optional): Game-type filter.
        group_by (Literal["Cat", "Pit", "Catching Team", "League"], optional):
            Leaderboard grouping. ``"Cat"`` returns catchers, ``"Pit"`` returns
            pitchers, ``"Catching Team"`` returns catching-team aggregates, and
            ``"League"`` returns league aggregates.
        min_pitches (int | str, optional): Minimum pitch count threshold, or
            ``"q"`` for Baseball Savant's qualifying threshold. Defaults to ``"q"``.
        team (StatcastLeaderboardsTeams | str, optional): Team filter. Use a team
            enum, ``"All"`` for all teams, or ``"All-Split"`` for separate team
            stints. Defaults to ``"All"``.
        split_years (bool, optional): If ``True``, return one row per season.
            Otherwise, aggregate across the requested season range.

    Raises:
        ValueError: If a season, filter, threshold, or team value is invalid.

    Returns:
        pl.DataFrame: Catcher-blocking leaderboard data.

    Notes:
        - Catcher-blocking data is available from 2018 onwards.
        - The website's ``Difficulty`` and ``Pitches`` controls filter only the
          selected catcher's visualization; they are not table CSV filters.
        - The website disables team and minimum-pitch filters for ``"Catching Team"``
          grouping, so this function follows that behavior.
    """
    current_year = datetime.now().year
    if not isinstance(start_season, int) or not 2018 <= start_season <= current_year:
        raise ValueError(f"start_season must be between 2018 and {current_year}")
    if (
        not isinstance(end_season, int)
        or not start_season <= end_season <= current_year
    ):
        raise ValueError(f"end_season must be between start_season and {current_year}")
    if game_type not in ["Regular", "Playoff", "All"]:
        raise ValueError("game_type must be 'Regular', 'Playoff', or 'All'")
    if group_by not in ["Cat", "Pit", "Catching Team", "League"]:
        raise ValueError("group_by must be 'Cat', 'Pit', 'Catching Team', or 'League'")

    if isinstance(min_pitches, int):
        if min_pitches < 1:
            raise ValueError("min_pitches must be at least 1")
        min_pitches_param = str(min_pitches)
    elif isinstance(min_pitches, str) and min_pitches == "q":
        min_pitches_param = min_pitches
    else:
        raise ValueError("min_pitches must be a positive integer or 'q'")

    if isinstance(team, StatcastLeaderboardsTeams):
        team_param = str(team.value)
    elif team == "All":
        team_param = ""
    elif team == "All-Split":
        team_param = "split"
    else:
        raise ValueError(
            "team must be a StatcastLeaderboardsTeams enum, 'All', or 'All-Split'"
        )

    if not isinstance(split_years, bool):
        raise ValueError("split_years must be a boolean")
    split_years_param = "yes" if split_years else "no"

    if group_by == "Catching Team":
        group_by_param = "Pitching+Team"
        team_param = ""
        min_pitches_param = ""
    else:
        group_by_param = group_by

    url = CATCHER_BLOCKING_LEADERBOARD_URL.format(
        game_type=game_type,
        min_pitches=min_pitches_param,
        end_season=end_season,
        start_season=start_season,
        split_years=split_years_param,
        team=team_param,
        group_by=group_by_param,
    )
    resp = requests.get(url)
    return pl.read_csv(io.StringIO(resp.text))


def catcher_framing_leaderboard(
    start_season: int,
    end_season: int,
    group_by: Literal[
        "catcher", "catching-team", "batter", "batting-team", "pitcher", "league"
    ] = "catcher",
    game_type: Literal["Any", "Regular", "Playoff"] = "Regular",
    min_pitches: int | str = "q",
    teams: List[StatcastLeaderboardsTeams] | None = None,
    batter_handedness: Literal["L", "R", "ALL"] = "ALL",
    pitcher_handedness: Literal["L", "R", "ALL"] = "ALL",
    in_zone: bool | None = None,
    min_results: int = 1,
) -> pl.DataFrame:
    """Return Baseball Savant catcher-framing leaderboard data.

    Args:
        start_season (int): First season to include. Must be 2018 or later.
        end_season (int): Last season to include. Must not precede ``start_season``.
        group_by (Literal[...], optional): Leaderboard entity. Options are
            ``"catcher"``, ``"catching-team"``, ``"batter"``, ``"batting-team"``,
            ``"pitcher"``, and ``"league"``.
        game_type (Literal["Any", "Regular", "Playoff"], optional): Game-type filter.
        min_pitches (int | str, optional): Minimum shadow-pitch threshold, or
            ``"q"`` for Baseball Savant's qualifying threshold. Defaults to ``"q"``.
        teams (List[StatcastLeaderboardsTeams] | None, optional): Organizations to
            include. ``None`` includes all teams.
        batter_handedness (Literal["L", "R", "ALL"], optional): Batter-side filter.
        pitcher_handedness (Literal["L", "R", "ALL"], optional): Pitcher-hand filter.
        in_zone (bool | None, optional): ``True`` for in-zone pitches, ``False`` for
            out-of-zone pitches, or ``None`` for both.
        min_results (int, optional): Minimum result count. Must be at least 1.

    Raises:
        ValueError: If a season, filter, team, or threshold value is invalid.

    Returns:
        pl.DataFrame: Catcher-framing leaderboard data. Player groupings use
            ``player_id`` and ``player_name``; team groupings use ``team_id`` and
            ``team_name``; league groupings use ``league_id`` and ``league_name``.

    Notes:
        Catcher-framing data is available from 2018 onwards.
    """
    current_year = datetime.now().year
    if not isinstance(start_season, int) or not 2018 <= start_season <= current_year:
        raise ValueError(f"start_season must be between 2018 and {current_year}")
    if (
        not isinstance(end_season, int)
        or not start_season <= end_season <= current_year
    ):
        raise ValueError(f"end_season must be between start_season and {current_year}")
    if group_by not in [
        "catcher",
        "catching-team",
        "batter",
        "batting-team",
        "pitcher",
        "league",
    ]:
        raise ValueError(
            "group_by must be 'catcher', 'catching-team', 'batter', "
            "'batting-team', 'pitcher', or 'league'"
        )
    if game_type not in ["Any", "Regular", "Playoff"]:
        raise ValueError("game_type must be 'Any', 'Regular', or 'Playoff'")

    if isinstance(min_pitches, int):
        if min_pitches < 1:
            raise ValueError("min_pitches must be at least 1")
        min_pitches_param = str(min_pitches)
    elif isinstance(min_pitches, str) and min_pitches == "q":
        min_pitches_param = min_pitches
    else:
        raise ValueError("min_pitches must be a positive integer or 'q'")

    if teams is not None:
        if not isinstance(teams, list) or not all(
            isinstance(team, StatcastLeaderboardsTeams) for team in teams
        ):
            raise ValueError(
                "teams must be a list of StatcastLeaderboardsTeams enums or None"
            )
        teams_param = "|".join(str(team.value) for team in teams)
    else:
        teams_param = ""

    if batter_handedness not in ["L", "R", "ALL"]:
        raise ValueError("batter_handedness must be 'L', 'R', or 'ALL'")
    bat_side_param = batter_handedness if batter_handedness != "ALL" else ""
    if pitcher_handedness not in ["L", "R", "ALL"]:
        raise ValueError("pitcher_handedness must be 'L', 'R', or 'ALL'")
    pitch_hand_param = pitcher_handedness if pitcher_handedness != "ALL" else ""

    if in_zone is not None and not isinstance(in_zone, bool):
        raise ValueError("in_zone must be a boolean or None")
    if in_zone is True:
        ball_strike_param = "in"
    elif in_zone is False:
        ball_strike_param = "out"
    else:
        ball_strike_param = ""

    if not isinstance(min_results, int) or min_results < 1:
        raise ValueError("min_results must be at least 1")

    url = CATCHER_FRAMING_LEADERBOARD_URL.format(
        game_type=game_type,
        start_season=start_season,
        end_season=end_season,
        teams=teams_param,
        group_by=group_by,
        min_pitches=min_pitches_param,
        min_results=min_results,
        bat_side=bat_side_param,
        pitch_hand=pitch_hand_param,
        ball_strike=ball_strike_param,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    if group_by in ["catcher", "batter", "pitcher"]:
        return df.rename({"id": "player_id", "name": "player_name"})
    if group_by in ["catching-team", "batting-team"]:
        return df.rename({"id": "team_id", "name": "team_name"})
    return df.rename({"id": "league_id", "name": "league_name"})


def catcher_pop_time_leaderboard(
    season: int = 2026,
    team: StatcastLeaderboardsTeams | None = None,
    min_2b_attempts: int = 5,
    min_3b_attempts: int = 0,
) -> pl.DataFrame:
    """Return Baseball Savant catcher Pop Time leaderboard data.

    Args:
        season (int, optional): Season year. Pop Time data is available from 2015
            through the current year.
        team (StatcastLeaderboardsTeams | None, optional): Optional team filter.
        min_2b_attempts (int, optional): Minimum second-base attempts.
        min_3b_attempts (int, optional): Minimum third-base attempts.

    Raises:
        ValueError: If a season, team, or attempt threshold is invalid.

    Returns:
        pl.DataFrame: Catcher Pop Time leaderboard data with catcher, team, and
            throwing metrics.
    """
    current_year = datetime.now().year
    if not isinstance(season, int) or not 2015 <= season <= current_year:
        raise ValueError(f"season must be between 2015 and {current_year}")
    if team is not None and not isinstance(team, StatcastLeaderboardsTeams):
        raise ValueError(
            "team must be an instance of StatcastLeaderboardsTeams or None"
        )
    if not isinstance(min_2b_attempts, int) or isinstance(min_2b_attempts, bool):
        raise ValueError("min_2b_attempts must be an integer")
    if not isinstance(min_3b_attempts, int) or isinstance(min_3b_attempts, bool):
        raise ValueError("min_3b_attempts must be an integer")

    team_param = str(team.value) if team is not None else ""
    url = POPTIME_LEADERBOARD_URL.format(
        season=season,
        team=team_param,
        min_2b_attempts=min_2b_attempts,
        min_3b_attempts=min_3b_attempts,
    )
    resp = requests.get(url)
    return pl.read_csv(io.StringIO(resp.text))


def catcher_stance_leaderboard(
    start_season: int,
    end_season: int,
    group_by: Literal[
        "catcher", "catching-team", "batter", "batting-team", "pitcher", "league"
    ] = "catcher",
    game_type: Literal["Any", "Regular", "Playoff"] = "Regular",
    min_pitches: int | str = "q",
    teams: List[StatcastLeaderboardsTeams] | None = None,
    batter_handedness: Literal["L", "R", "ALL"] = "ALL",
    pitcher_handedness: Literal["L", "R", "ALL"] = "ALL",
    knee_position: Literal[
        "ALL", "Knee(s) Down", "Both Up", "Both Down", "R Up, L Down", "L Up, R Down"
    ] = "ALL",
    min_results: int = 1,
    start_date: str | None = None,
    end_date: str | None = None,
) -> pl.DataFrame:
    """Return Baseball Savant catcher-stance leaderboard data.

    Args:
        start_season (int): First season to include. Must be 2020 or later.
        end_season (int): Last season to include. Must not precede ``start_season``.
        group_by (Literal[...], optional): Leaderboard entity. Options are
            ``"catcher"``, ``"catching-team"``, ``"batter"``, ``"batting-team"``,
            ``"pitcher"``, and ``"league"``.
        game_type (Literal["Any", "Regular", "Playoff"], optional): Game-type filter.
        min_pitches (int | str, optional): Minimum pitch threshold, or ``"q"`` for
            Baseball Savant's qualifying threshold. Defaults to ``"q"``.
        teams (List[StatcastLeaderboardsTeams] | None, optional): Organizations to
            include. ``None`` includes all teams.
        batter_handedness (Literal["L", "R", "ALL"], optional): Batter-side filter.
        pitcher_handedness (Literal["L", "R", "ALL"], optional): Pitcher-hand filter.
        knee_position (Literal[...], optional): Catcher stance filter. Options are
            ``"ALL"``, ``"Knee(s) Down"``, ``"Both Up"``, ``"Both Down"``,
            ``"R Up, L Down"``, and ``"L Up, R Down"``.
        min_results (int, optional): Minimum result count. Must be at least 1.
        start_date (str | None, optional): Optional start date in ``YYYY-MM-DD``
            format. The earliest available date is ``2020-07-23``.
        end_date (str | None, optional): Optional end date in ``YYYY-MM-DD`` format.

    Raises:
        ValueError: If a season, date, filter, team, or threshold value is invalid.

    Returns:
        pl.DataFrame: Catcher-stance leaderboard data. Player groupings use
            ``player_id`` and ``player_name``; team groupings use ``team_id`` and
            ``team_name``; league groupings use ``league_id`` and ``league_name``.
    """
    current_year = datetime.now().year
    if not isinstance(start_season, int) or not 2020 <= start_season <= current_year:
        raise ValueError(f"start_season must be between 2020 and {current_year}")
    if (
        not isinstance(end_season, int)
        or not start_season <= end_season <= current_year
    ):
        raise ValueError(f"end_season must be between start_season and {current_year}")
    if group_by not in [
        "catcher",
        "catching-team",
        "batter",
        "batting-team",
        "pitcher",
        "league",
    ]:
        raise ValueError(
            "group_by must be 'catcher', 'catching-team', 'batter', "
            "'batting-team', 'pitcher', or 'league'"
        )
    if game_type not in ["Any", "Regular", "Playoff"]:
        raise ValueError("game_type must be 'Any', 'Regular', or 'Playoff'")

    if isinstance(min_pitches, int):
        if min_pitches < 1:
            raise ValueError("min_pitches must be at least 1")
        min_pitches_param = str(min_pitches)
    elif isinstance(min_pitches, str) and min_pitches == "q":
        min_pitches_param = min_pitches
    else:
        raise ValueError("min_pitches must be a positive integer or 'q'")

    if teams is not None:
        if not isinstance(teams, list) or not all(
            isinstance(team, StatcastLeaderboardsTeams) for team in teams
        ):
            raise ValueError(
                "teams must be a list of StatcastLeaderboardsTeams enums or None"
            )
        teams_param = "|".join(str(team.value) for team in teams)
    else:
        teams_param = ""

    if batter_handedness not in ["L", "R", "ALL"]:
        raise ValueError("batter_handedness must be 'L', 'R', or 'ALL'")
    bat_side_param = batter_handedness if batter_handedness != "ALL" else ""
    if pitcher_handedness not in ["L", "R", "ALL"]:
        raise ValueError("pitcher_handedness must be 'L', 'R', or 'ALL'")
    pitch_hand_param = pitcher_handedness if pitcher_handedness != "ALL" else ""

    knee_position_codes = {
        "ALL": "",
        "Knee(s) Down": "9999",
        "Both Up": "4",
        "Both Down": "1",
        "R Up, L Down": "2",
        "L Up, R Down": "3",
    }
    if knee_position not in knee_position_codes:
        raise ValueError(
            "knee_position must be 'ALL', 'Knee(s) Down', 'Both Up', 'Both Down', "
            "'R Up, L Down', or 'L Up, R Down'"
        )
    knee_code_param = knee_position_codes[knee_position]

    if not isinstance(min_results, int) or min_results < 1:
        raise ValueError("min_results must be at least 1")

    earliest_date = datetime(2020, 7, 23).date()
    latest_date = datetime.today().date()
    date_params = {}
    for name, value in [("start_date", start_date), ("end_date", end_date)]:
        if value is None:
            date_params[name] = ""
            continue
        try:
            date_value = datetime.strptime(value, "%Y-%m-%d").date()
        except (TypeError, ValueError):
            raise ValueError(f"{name} must be in YYYY-MM-DD format")
        if date_value < earliest_date:
            raise ValueError(f"{name} must be on or after 2020-07-23")
        if date_value > latest_date:
            raise ValueError(f"{name} cannot be in the future")
        date_params[name] = value

    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValueError("end_date must be on or after start_date")

    url = CATCHER_STANCE_LEADERBOARD_URL.format(
        game_type=game_type,
        start_season=start_season,
        end_season=end_season,
        teams=teams_param,
        group_by=group_by,
        min_pitches=min_pitches_param,
        min_results=min_results,
        bat_side=bat_side_param,
        pitch_hand=pitch_hand_param,
        knee_code=knee_code_param,
        start_date=date_params["start_date"],
        end_date=date_params["end_date"],
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    if group_by in ["catcher", "batter", "pitcher"]:
        return df.rename({"id": "player_id", "name": "player_name"})
    if group_by in ["catching-team", "batting-team"]:
        return df.rename({"id": "team_id", "name": "team_name"})
    return df.rename({"id": "league_id", "name": "league_name"})


def catcher_throwing_leaderboard(
    start_season: int,
    end_season: int,
    game_type: Literal["Regular", "Playoff", "All"] = "Regular",
    group_by: Literal["Cat", "Pitching Team", "League"] = "Cat",
    min_sb_attempts: int | str = "q",
    target_base: Literal["2B", "3B", "All"] = "All",
    team: StatcastLeaderboardsTeams | str = "All",
    split_years: bool = False,
    with_team_only: bool = True,
) -> pl.DataFrame:
    """Return Baseball Savant catcher-throwing leaderboard data.

    Args:
        start_season (int): First season to include. Must be 2016 or later.
        end_season (int): Last season to include. Must not precede start_season.
        game_type (Literal[Regular, Playoff, All], optional): Game-type filter.
        group_by (Literal[Cat, Pitching Team, League], optional): Leaderboard
            grouping. Cat returns catchers, Pitching Team returns catching-team
            aggregates, and League returns league aggregates.
        min_sb_attempts (int | str, optional): Minimum stolen-base attempt threshold,
            or q for Baseball Savant's qualifying threshold. Defaults to q.
        target_base (Literal[2B, 3B, All], optional): Base targeted by the throw.
        team (StatcastLeaderboardsTeams | str, optional): Team filter. Use a team
            enum, All for all teams, or All-Split for separate team stints.
        split_years (bool, optional): If True, return one row per season.
        with_team_only (bool, optional): If True, include only rows with a team.

    Raises:
        ValueError: If a season, filter, threshold, team, or boolean value is invalid.

    Returns:
        pl.DataFrame: Catcher-throwing leaderboard data.
    """
    current_year = datetime.now().year
    if not isinstance(start_season, int) or not 2016 <= start_season <= current_year:
        raise ValueError(f"start_season must be between 2016 and {current_year}")
    if (
        not isinstance(end_season, int)
        or not start_season <= end_season <= current_year
    ):
        raise ValueError(f"end_season must be between start_season and {current_year}")
    if game_type not in ["Regular", "Playoff", "All"]:
        raise ValueError("game_type must be 'Regular', 'Playoff', or 'All'")
    if group_by not in ["Cat", "Pitching Team", "League"]:
        raise ValueError("group_by must be 'Cat', 'Pitching Team', or 'League'")

    if isinstance(min_sb_attempts, int):
        if min_sb_attempts < 1:
            raise ValueError("min_sb_attempts must be at least 1")
        min_sb_attempts_param = str(min_sb_attempts)
    elif isinstance(min_sb_attempts, str) and min_sb_attempts == "q":
        min_sb_attempts_param = min_sb_attempts
    else:
        raise ValueError("min_sb_attempts must be a positive integer or 'q'")

    if target_base not in ["2B", "3B", "All"]:
        raise ValueError("target_base must be '2B', '3B', or 'All'")
    if isinstance(team, StatcastLeaderboardsTeams):
        team_param = str(team.value)
    elif team == "All":
        team_param = ""
    elif team == "All-Split":
        team_param = "split"
    else:
        raise ValueError(
            "team must be a StatcastLeaderboardsTeams enum, 'All', or 'All-Split'"
        )
    if not isinstance(split_years, bool):
        raise ValueError("split_years must be a boolean")
    if not isinstance(with_team_only, bool):
        raise ValueError("with_team_only must be a boolean")

    url = CATCHER_THROWING_LEADERBOARD_URL.format(
        game_type=game_type,
        min_sb_attempts=min_sb_attempts_param,
        end_season=end_season,
        start_season=start_season,
        split_years="yes" if split_years else "no",
        team=team_param,
        group_by=group_by,
        with_team_only="1" if with_team_only else "0",
        target_base=target_base,
    )
    resp = requests.get(url)
    return pl.read_csv(io.StringIO(resp.text))


# endregion
