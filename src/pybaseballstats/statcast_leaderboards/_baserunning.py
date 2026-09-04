import io
from datetime import datetime
from typing import Literal

import polars as pl
import requests

from pybaseballstats._consts.statcast_leaderboard_consts import (
    BASERUNNING_RUN_VALUE_LEADERBOARD_URL,
    BASESTEALING_RUN_VALUE_LEADERBOARD_URL,
    EXTRA_BASES_TAKEN_RUN_VALUE_LEADERBOARD_URL,
    RUNNING_SPLITS_LEADERBOARD_URL,
    SPRINT_SPEED_PLAYER_LEADERBOARD_URL,
    SPRINT_SPEED_TEAM_LEADERBOARD_URL,
    StatcastLeaderboardsTeams,
)


def baserunning_run_value_leaderboard(
    start_season: int,
    end_season: int,
    game_type: Literal["Regular", "Playoff", "All"] = "Regular",
    group_by: Literal["Runners", "Running Team", "Pitching Team", "League"] = "Runners",
    min_opportunities: int | str = "q",
    team: StatcastLeaderboardsTeams | str = "All",
    split_years: bool = False,
) -> pl.DataFrame:
    """Return Baseball Savant baserunning run-value leaderboard data.

    Args:
        start_season (int): First season to include. Must be 2016 or later.
        end_season (int): Last season to include. Must not precede ``start_season``.
        game_type (Literal["Regular", "Playoff", "All"], optional): Game-type
            filter. Defaults to ``"Regular"``.
        group_by (Literal["Runners", "Running Team", "Pitching Team", "League"], optional):
            Leaderboard grouping. Defaults to ``"Runners"``.
        min_opportunities (int | str, optional): Minimum baserunning opportunities,
            or ``"q"`` for Baseball Savant's qualifying threshold. Defaults to
            ``"q"``.
        team (StatcastLeaderboardsTeams | str, optional): Team filter. Use a team
            enum, ``"All"`` for all teams, or ``"All-Split"`` for separate team
            stints. Defaults to ``"All"``.
        split_years (bool, optional): If ``True``, return one row per season.
            Otherwise, aggregate across the requested season range. Defaults to
            ``False``.

    Raises:
        ValueError: If a season, filter, threshold, team, or boolean value is invalid.

    Returns:
        pl.DataFrame: Baserunning run-value leaderboard data. Runner groupings use
            ``player_id`` and ``player_name``; team groupings use ``team_id``,
            ``team_name``, and ``team_abbr``; league groupings use ``league_id``
            and ``league_name``.

    Notes:
        Baserunning run-value data is available from 2016 onwards.
    """
    current_year = datetime.now().year
    if (
        not isinstance(start_season, int)
        or isinstance(start_season, bool)
        or not 2016 <= start_season <= current_year
    ):
        raise ValueError(f"start_season must be between 2016 and {current_year}")
    if (
        not isinstance(end_season, int)
        or isinstance(end_season, bool)
        or not start_season <= end_season <= current_year
    ):
        raise ValueError(f"end_season must be between start_season and {current_year}")
    if game_type not in ["Regular", "Playoff", "All"]:
        raise ValueError("game_type must be 'Regular', 'Playoff', or 'All'")
    if group_by not in ["Runners", "Running Team", "Pitching Team", "League"]:
        raise ValueError(
            "group_by must be 'Runners', 'Running Team', 'Pitching Team', or 'League'"
        )
    group_by_params = {
        "Runners": "Run",
        "Running Team": "Batting+Team",
        "Pitching Team": "Pitching+Team",
        "League": "League",
    }

    if isinstance(min_opportunities, int) and not isinstance(min_opportunities, bool):
        if min_opportunities < 1:
            raise ValueError("min_opportunities must be at least 1")
        min_opportunities_param = str(min_opportunities)
    elif isinstance(min_opportunities, str) and min_opportunities == "q":
        min_opportunities_param = min_opportunities
    else:
        raise ValueError("min_opportunities must be a positive integer or 'q'")

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

    url = BASERUNNING_RUN_VALUE_LEADERBOARD_URL.format(
        game_type=game_type,
        start_season=start_season,
        end_season=end_season,
        split_years="yes" if split_years else "no",
        min_opportunities=min_opportunities_param,
        team=team_param,
        group_by=group_by_params[group_by],
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    if group_by == "Runners":
        return df.rename({"entity_name": "player_name"})
    if group_by in ["Running Team", "Pitching Team"]:
        return df.rename(
            {
                "player_id": "team_id",
                "entity_name": "team_name",
                "team_name": "team_abbr",
            }
        )
    return df.rename({"player_id": "league_id", "entity_name": "league_name"})


def basestealing_run_value_leaderboard(
    start_season: int,
    end_season: int,
    game_type: Literal["Regular", "Playoff", "All"] = "Regular",
    group_by: Literal["Runners", "Running Team", "League"] = "Runners",
    pitcher_handedness: Literal["R", "L", "ALL"] = "ALL",
    runner_movement: Literal["All", "Advance", "Out", "Hold"] = "All",
    target_base: Literal["All", "2B", "3B"] = "All",
    num_prior_disengagements: Literal["All", "0", "1", "2", "3+"] = "All",
    min_sb_opportunities: int | str = "q",
    team: StatcastLeaderboardsTeams | str = "All",
    split_years: bool = False,
) -> pl.DataFrame:
    """Return Baseball Savant basestealing run-value leaderboard data.

    Args:
        start_season (int): First season to include. Must be 2016 or later.
        end_season (int): Last season to include. Must not precede ``start_season``.
        game_type (Literal["Regular", "Playoff", "All"], optional): Game-type
            filter. Defaults to ``"Regular"``.
        group_by (Literal["Runners", "Running Team", "League"], optional):
            Leaderboard grouping. Defaults to ``"Runners"``.
        pitcher_handedness (Literal["R", "L", "ALL"], optional): Pitcher-hand
            filter. Defaults to ``"ALL"``.
        runner_movement (Literal["All", "Advance", "Out", "Hold"], optional):
            Runner-outcome filter. Defaults to ``"All"``.
        target_base (Literal["All", "2B", "3B"], optional): Target-base filter.
            Defaults to ``"All"``.
        num_prior_disengagements (Literal["All", "0", "1", "2", "3+"], optional):
            Number of prior pitcher disengagements. Defaults to ``"All"``.
        min_sb_opportunities (int | str, optional): Minimum stolen-base opportunity
            count, or ``"q"`` for Baseball Savant's qualifying threshold.
            Defaults to ``"q"``.
        team (StatcastLeaderboardsTeams | str, optional): Team filter. Use a team
            enum, ``"All"`` for all teams, or ``"All-Split"`` for separate team
            stints. Defaults to ``"All"``.
        split_years (bool, optional): If ``True``, return one row per season.
            Otherwise, aggregate across the requested season range. Defaults to
            ``False``.

    Raises:
        ValueError: If a season, filter, threshold, team, or boolean value is invalid.

    Returns:
        pl.DataFrame: Basestealing run-value leaderboard data with ``player_id``,
            ``player_name``, and ``team_name`` identifier columns.

    Notes:
        Basestealing run-value data is available from 2016 onwards. The website's
        column-expansion control changes presentation only and is not a table-data
        filter, so it is not exposed here.
    """
    current_year = datetime.now().year
    if (
        not isinstance(start_season, int)
        or isinstance(start_season, bool)
        or not 2016 <= start_season <= current_year
    ):
        raise ValueError(f"start_season must be between 2016 and {current_year}")
    if (
        not isinstance(end_season, int)
        or isinstance(end_season, bool)
        or not start_season <= end_season <= current_year
    ):
        raise ValueError(f"end_season must be between start_season and {current_year}")
    if game_type not in ["Regular", "Playoff", "All"]:
        raise ValueError("game_type must be 'Regular', 'Playoff', or 'All'")
    if group_by not in ["Runners", "Running Team", "League"]:
        raise ValueError("group_by must be 'Runners', 'Running Team', or 'League'")
    group_by_params = {
        "Runners": "Bat",
        "Running Team": "Batting+Team",
        "League": "League",
    }
    if pitcher_handedness not in ["R", "L", "ALL"]:
        raise ValueError("pitcher_handedness must be 'R', 'L', or 'ALL'")
    pitcher_handedness_param = (
        pitcher_handedness if pitcher_handedness != "ALL" else "all"
    )
    if runner_movement not in ["All", "Advance", "Out", "Hold"]:
        raise ValueError("runner_movement must be 'All', 'Advance', 'Out', or 'Hold'")
    if target_base not in ["All", "2B", "3B"]:
        raise ValueError("target_base must be 'All', '2B', or '3B'")
    if num_prior_disengagements not in ["All", "0", "1", "2", "3+"]:
        raise ValueError(
            "num_prior_disengagements must be 'All', '0', '1', '2', or '3+'"
        )
    num_prior_disengagements_param = (
        num_prior_disengagements if num_prior_disengagements != "3+" else "3"
    )

    if isinstance(min_sb_opportunities, int) and not isinstance(
        min_sb_opportunities, bool
    ):
        if min_sb_opportunities < 1:
            raise ValueError("min_sb_opportunities must be at least 1")
        min_sb_opportunities_param = str(min_sb_opportunities)
    elif isinstance(min_sb_opportunities, str) and min_sb_opportunities == "q":
        min_sb_opportunities_param = min_sb_opportunities
    else:
        raise ValueError("min_sb_opportunities must be a positive integer or 'q'")

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

    url = BASESTEALING_RUN_VALUE_LEADERBOARD_URL.format(
        game_type=game_type,
        min_sb_opportunities=min_sb_opportunities_param,
        pitcher_handedness=pitcher_handedness_param,
        runner_movement=runner_movement,
        target_base=target_base,
        num_prior_disengagements=num_prior_disengagements_param,
        end_season=end_season,
        start_season=start_season,
        split_years="yes" if split_years else "no",
        team=team_param,
        group_by=group_by_params[group_by],
    )
    resp = requests.get(url)
    return pl.read_csv(io.StringIO(resp.text))


def extra_bases_taken_run_value_leaderboard(
    start_season: int,
    end_season: int,
    game_type: Literal["Regular", "Playoff", "All"] = "Regular",
    group_by: Literal[
        "Runners",
        "Fielders",
        "Pitchers",
        "Batting Team",
        "Fielding Team",
        "League",
    ] = "Runners",
    situation: Literal[
        "all",
        "batter_1b_to_2b",
        "batter_2b_to_3b",
        "runner_1b_to_3b_lt_2_outs",
        "runner_1b_to_3b_2_outs",
        "runner_1b_to_home_lt_2_outs",
        "runner_1b_to_home_2_outs",
        "runner_2b_to_home_lt_2_outs",
        "runner_2b_to_home_2_outs",
        "runner_3b_to_home_first_out",
        "runner_3b_to_home_second_out",
    ] = "all",
    min_opportunities: int | str = "q",
    team: StatcastLeaderboardsTeams | str = "All",
    split_years: bool = False,
) -> pl.DataFrame:
    """Return Baseball Savant Extra Bases Taken run-value leaderboard data.

    Args:
        start_season (int): First season to include. Must be 2016 or later.
        end_season (int): Last season to include. Must not precede ``start_season``.
        game_type (Literal["Regular", "Playoff", "All"], optional): Game-type
            filter. Defaults to ``"Regular"``.
        group_by (Literal[...], optional): Leaderboard grouping. Options are
            ``"Runners"``, ``"Fielders"``, ``"Pitchers"``, ``"Batting Team"``,
            ``"Fielding Team"``, and ``"League"``. Defaults to ``"Runners"``.
        situation (Literal[...], optional): Short base/out situation key. Supported
            keys are ``"all"``, ``"batter_1b_to_2b"``, ``"batter_2b_to_3b"``,
            ``"runner_1b_to_3b_lt_2_outs"``, ``"runner_1b_to_3b_2_outs"``,
            ``"runner_1b_to_home_lt_2_outs"``, ``"runner_1b_to_home_2_outs"``,
            ``"runner_2b_to_home_lt_2_outs"``, ``"runner_2b_to_home_2_outs"``,
            ``"runner_3b_to_home_first_out"``, and
            ``"runner_3b_to_home_second_out"``. Defaults to ``"all"``.
        min_opportunities (int | str, optional): Minimum advance opportunities, or
            ``"q"`` for Baseball Savant's qualifying threshold. Defaults to ``"q"``.
        team (StatcastLeaderboardsTeams | str, optional): Team filter. Use a team
            enum, ``"All"`` for all teams, or ``"All-Split"`` for separate team
            stints. Defaults to ``"All"``.
        split_years (bool, optional): If ``True``, return one row per season.
            Otherwise, aggregate across the requested season range. Defaults to
            ``False``.

    Raises:
        ValueError: If a season, filter, threshold, team, or boolean value is invalid.

    Returns:
        pl.DataFrame: Extra Bases Taken run-value leaderboard data. Player groupings
            use ``player_id`` and ``player_name``; team groupings use ``team_id``,
            ``team_name``, and ``team_abbr``; league groupings use ``league_id``
            and ``league_name``.

    Notes:
        Extra Bases Taken data is available from 2016 onwards. The website's
        presentation controls are not exposed because they do not change the CSV
        table request.
    """
    current_year = datetime.now().year
    if (
        not isinstance(start_season, int)
        or isinstance(start_season, bool)
        or not 2016 <= start_season <= current_year
    ):
        raise ValueError(f"start_season must be between 2016 and {current_year}")
    if (
        not isinstance(end_season, int)
        or isinstance(end_season, bool)
        or not start_season <= end_season <= current_year
    ):
        raise ValueError(f"end_season must be between start_season and {current_year}")
    if game_type not in ["Regular", "Playoff", "All"]:
        raise ValueError("game_type must be 'Regular', 'Playoff', or 'All'")

    situation_params = {
        "all": "All",
        "batter_1b_to_2b": "r10_to_2b_210",
        "batter_2b_to_3b": "r10_to_3b_210",
        "runner_1b_to_3b_lt_2_outs": "r11_to_3b_10",
        "runner_1b_to_3b_2_outs": "r11_to_3b_2",
        "runner_1b_to_home_lt_2_outs": "r11_to_hp_10",
        "runner_1b_to_home_2_outs": "r11_to_hp_2",
        "runner_2b_to_home_lt_2_outs": "r12_to_hp_10",
        "runner_2b_to_home_2_outs": "r12_to_hp_2",
        "runner_3b_to_home_first_out": "r13_to_hp_0",
        "runner_3b_to_home_second_out": "r13_to_hp_1",
    }
    if not isinstance(situation, str) or situation not in situation_params:
        raise ValueError("situation must be one of the documented situation keys")

    group_by_params = {
        "Runners": "Run",
        "Fielders": "Fld",
        "Pitchers": "Pit",
        "Batting Team": "Batting+Team",
        "Fielding Team": "Pitching+Team",
        "League": "League",
    }
    if group_by not in [
        "Runners",
        "Fielders",
        "Pitchers",
        "Batting Team",
        "Fielding Team",
        "League",
    ]:
        raise ValueError(
            "group_by must be 'Runners', 'Fielders', 'Pitchers', 'Batting Team', "
            "'Fielding Team', or 'League'"
        )

    if isinstance(min_opportunities, int) and not isinstance(min_opportunities, bool):
        if min_opportunities < 1:
            raise ValueError("min_opportunities must be at least 1")
        min_opportunities_param = str(min_opportunities)
    elif isinstance(min_opportunities, str) and min_opportunities == "q":
        min_opportunities_param = "top"
    else:
        raise ValueError("min_opportunities must be a positive integer or 'q'")

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

    url = EXTRA_BASES_TAKEN_RUN_VALUE_LEADERBOARD_URL.format(
        game_type=game_type,
        min_opportunities=min_opportunities_param,
        situation=situation_params[situation],
        end_season=end_season,
        start_season=start_season,
        split_years="yes" if split_years else "no",
        team=team_param,
        group_by=group_by_params[group_by],
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    if group_by in ["Runners", "Fielders", "Pitchers"]:
        return df.rename({"entity_id": "player_id", "entity_name": "player_name"})
    if group_by in ["Batting Team", "Fielding Team"]:
        return df.rename(
            {
                "entity_id": "team_id",
                "entity_name": "team_name",
                "team_name": "team_abbr",
            }
        )
    return df.rename({"entity_id": "league_id", "entity_name": "league_name"})


def sprint_speed_leaderboard(
    start_season: int,
    end_season: int,
    group_by: Literal["Player", "Team"] = "Player",
    position: Literal[
        "Position Players",
        "All",
        "C",
        "1B",
        "2B",
        "SS",
        "3B",
        "LF",
        "CF",
        "RF",
        "DH",
        "P",
    ] = "Position Players",
    min_opportunities: int = 10,
    team: StatcastLeaderboardsTeams | str = "All",
    split_years: bool = False,
) -> pl.DataFrame:
    """Return Baseball Savant Sprint Speed leaderboard data.

    Args:
        start_season (int): First season to include. Must be 2015 or later.
        end_season (int): Last season to include. Must not precede ``start_season``.
        group_by (Literal["Player", "Team"], optional): Leaderboard row type.
            ``"Player"`` supports a season range; ``"Team"`` supports one season
            or Baseball Savant's split-years view. Defaults to ``"Player"``.
        position (Literal[...], optional): Player-position filter. Defaults to
            ``"Position Players"``. Use ``"All"`` to include pitchers. This filter
            is used only for player results.
        min_opportunities (int, optional): Minimum competitive-run count. The
            endpoint accepts zero or any non-negative integer. Defaults to ``10``.
        team (StatcastLeaderboardsTeams | str, optional): Team filter. Use a team
            enum or ``"All"``. Defaults to ``"All"``.
        split_years (bool, optional): For team results, use Baseball Savant's
            ``"All - Split Years"`` option when ``True``. For player results, this
            parameter has no effect. Defaults to ``False``.

    Raises:
        ValueError: If a season, grouping, position, threshold, team, or boolean
            value is invalid, or if team results request a season range without
            ``split_years=True``.

    Returns:
        pl.DataFrame: Sprint Speed leaderboard data. Player results use
            ``player_id``, ``player_name``, and ``team_abbr``. Team results use
            ``team_id`` and ``team_name``.

    Notes:
        Sprint Speed data is available from 2015 onwards. Baseball Savant's team
        split-years view returns all available team seasons, so the requested
        season bounds are not applied in that mode.
    """
    current_year = datetime.now().year
    if (
        not isinstance(start_season, int)
        or isinstance(start_season, bool)
        or not 2015 <= start_season <= current_year
    ):
        raise ValueError(f"start_season must be between 2015 and {current_year}")
    if (
        not isinstance(end_season, int)
        or isinstance(end_season, bool)
        or not start_season <= end_season <= current_year
    ):
        raise ValueError(f"end_season must be between start_season and {current_year}")
    if group_by not in ["Player", "Team"]:
        raise ValueError("group_by must be 'Player' or 'Team'")

    position_params = {
        "Position Players": "",
        "All": "all",
        "C": "2",
        "1B": "3",
        "2B": "4",
        "SS": "6",
        "3B": "5",
        "LF": "7",
        "CF": "8",
        "RF": "9",
        "DH": "10",
        "P": "1",
    }
    if not isinstance(position, str) or position not in position_params:
        raise ValueError("position must be one of the documented position values")
    if (
        not isinstance(min_opportunities, int)
        or isinstance(min_opportunities, bool)
        or min_opportunities < 0
    ):
        raise ValueError("min_opportunities must be a non-negative integer")

    if isinstance(team, StatcastLeaderboardsTeams):
        team_param = str(team.value)
    elif team == "All":
        team_param = ""
    else:
        raise ValueError("team must be a StatcastLeaderboardsTeams enum or 'All'")
    if not isinstance(split_years, bool):
        raise ValueError("split_years must be a boolean")

    if group_by == "Player":
        url = SPRINT_SPEED_PLAYER_LEADERBOARD_URL.format(
            start_season=start_season,
            end_season=end_season,
            position=position_params[position],
            team=team_param,
            min_opportunities=min_opportunities,
        )
    else:
        if not split_years and start_season != end_season:
            raise ValueError(
                "Team results require matching seasons unless split_years is True"
            )
        url = SPRINT_SPEED_TEAM_LEADERBOARD_URL.format(
            season="all" if split_years else start_season,
            team=team_param,
        )

    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    if group_by == "Player":
        return df.rename(
            {
                "last_name, first_name": "player_name",
                "team": "team_abbr",
            }
        )
    return df.rename({"team": "team_name", "home_to_first": "hp_to_1b"})


def running_splits_leaderboard(
    season: int,
    position: Literal[
        "All",
        "C",
        "1B",
        "2B",
        "SS",
        "3B",
        "LF",
        "CF",
        "RF",
        "DH",
    ] = "All",
    team: StatcastLeaderboardsTeams | str = "All",
    bat_side: Literal["All", "Right", "Left"] = "All",
    min_opportunities: int = 5,
    split_type: Literal["raw_times", "percentile"] = "raw_times",
) -> pl.DataFrame:
    """Return Baseball Savant 90ft Running Splits leaderboard data.

    Args:
        season (int): Season year. Must be 2015 or later.
        position (Literal[...], optional): Position filter. Defaults to ``"All"``.
        team (StatcastLeaderboardsTeams | str, optional): Team filter. Use a team
            enum or ``"All"``. Defaults to ``"All"``.
        bat_side (Literal["All", "Right", "Left"], optional): Batter-side filter.
            Defaults to ``"All"``.
        min_opportunities (int, optional): Minimum running-split opportunities.
            The endpoint accepts any positive integer. Defaults to ``5``.
        split_type (Literal["raw_times", "percentile"], optional):
            Return raw_times or percentile. Defaults to
            ``"raw_times"``.

    Raises:
        ValueError: If a season, position, team, batter side, threshold, or split
            type is invalid.

    Returns:
        pl.DataFrame: Running Splits leaderboard data with ``player_id``,
            ``player_name``, ``team_abbr``, and ``position`` identifier columns.

    Notes:
        Running Splits data is available from 2015 onwards. The page's four player
        comparison selectors are visualization controls and are not table filters,
        so they are not exposed here.
    """
    current_year = datetime.now().year
    if (
        not isinstance(season, int)
        or isinstance(season, bool)
        or not 2015 <= season <= current_year
    ):
        raise ValueError(f"season must be between 2015 and {current_year}")

    position_params = {
        "All": "",
        "C": "2",
        "1B": "3",
        "2B": "4",
        "SS": "6",
        "3B": "5",
        "LF": "7",
        "CF": "8",
        "RF": "9",
        "DH": "10",
    }
    if not isinstance(position, str) or position not in position_params:
        raise ValueError("position must be one of the documented position values")

    bat_side_params = {"All": "", "Right": "R", "Left": "L"}
    if not isinstance(bat_side, str) or bat_side not in bat_side_params:
        raise ValueError("bat_side must be 'All', 'Right', or 'Left'")

    split_type_params = {
        "raw_times": "raw",
        "percentile": "percent",
    }
    if not isinstance(split_type, str) or split_type not in split_type_params:
        raise ValueError("split_type must be 'raw_times' or 'percentile'")

    if (
        not isinstance(min_opportunities, int)
        or isinstance(min_opportunities, bool)
        or min_opportunities < 1
    ):
        raise ValueError("min_opportunities must be a positive integer")

    if isinstance(team, StatcastLeaderboardsTeams):
        team_param = str(team.value)
    elif team == "All":
        team_param = ""
    else:
        raise ValueError("team must be a StatcastLeaderboardsTeams enum or 'All'")

    url = RUNNING_SPLITS_LEADERBOARD_URL.format(
        split_type=split_type_params[split_type],
        bat_side=bat_side_params[bat_side],
        season=season,
        position=position_params[position],
        team=team_param,
        min_opportunities=min_opportunities,
    )
    resp = requests.get(url)
    df = pl.read_csv(io.StringIO(resp.text))
    return df.rename(
        {
            "last_name, first_name": "player_name",
            "name_abbrev": "team_abbr",
            "position_name": "position",
        }
    )
