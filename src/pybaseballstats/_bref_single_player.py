from typing import Literal

import polars as pl

# TODO: same range of tables as bref_teams, but for this module
from pybaseballstats._consts.bref_consts import (
    BREF_SINGLE_PLAYER_BATTING_URL,
    BREF_SINGLE_PLAYER_FIELDING_URL,
    BREF_SINGLE_PLAYER_PITCHING_URL,
)
from pybaseballstats._utils.bref_utils import (
    _required_table,
    _source_schema_errors,
)
from pybaseballstats._utils.session_utils import BREF_SESSION as session

__all__ = [
    "single_player_batting",
    "single_player_pitching",
    "single_player_fielding",
]


@_source_schema_errors
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
    verbose: bool = False,
) -> pl.DataFrame:
    """Return single-player batting statistics for one metric family.

    Args:
        player_code (str): Baseball Reference player identifier
            (for example ``"troutmi01"``).
        metric_type (Literal[...], optional): Batting table family to fetch.
            Supported metric families are ``"standard"``, ``"value"``, ``"advanced"``,
            ``"sabermetric"``, ``"ratio"``, ``"win_probability"``, ``"baserunning"``,
            ``"situational"``, ``"pitches"``, and ``"cumulative"``.
        verbose (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.

    Raises:
        ValueError: If ``metric_type`` is not supported.
        RuntimeError: If the requested batting table is not found.

    Returns:
        pl.DataFrame: Requested batting table with normalized column names.
    """
    if not isinstance(player_code, str):
        raise TypeError("player_code must be a string")
    if not player_code:
        raise ValueError("player_code must not be empty")
    if not isinstance(metric_type, str):
        raise TypeError("metric_type must be a string")
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
    resp = session.get(
        BREF_SINGLE_PLAYER_BATTING_URL.format(
            initial=last_name_initial, player_code=player_code
        ),
        verbose=verbose,
    )
    if metric_type in ["standard", "value", "advanced"]:
        table_id = f"players_{metric_type}_batting"
    elif metric_type == "cumulative":
        table_id = "cumulative_batting"
    else:
        table_id = f"batting_{metric_type}"
    df = _required_table(resp.text, table_id, "single_player_batting")
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("b_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    return df


@_source_schema_errors
def single_player_pitching(
    player_code: str,
    metric_type: Literal[
        "standard",
        "value",
        "advanced",
        "ratio",
        "win_probability",
        "basesituation",
        "batting_against",
        "pitches",
        "cumulative",
    ] = "standard",
    verbose: bool = False,
) -> pl.DataFrame:
    """Return single-player pitching statistics for one metric family.

    Supported metric families are ``"standard"``, ``"value"``, ``"advanced"``,
    ``"ratio"``, ``"win_probability"``, ``"basesituation"``,
    ``"batting_against"``, ``"pitches"``, and ``"cumulative"``.

    Args:
        player_code (str): Baseball Reference player identifier
            (for example ``"troutmi01"``).
        metric_type (Literal[...], optional): Pitching table family to fetch.
        verbose (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.
    Raises:
        ValueError: If ``metric_type`` is not supported.
        RuntimeError: If the requested pitching table is not found.

    Returns:
        pl.DataFrame: Requested pitching table with normalized column names.
    """
    if not isinstance(player_code, str):
        raise TypeError("player_code must be a string")
    if not player_code:
        raise ValueError("player_code must not be empty")
    if not isinstance(metric_type, str):
        raise TypeError("metric_type must be a string")
    if metric_type not in [
        "standard",
        "value",
        "advanced",
        "ratio",
        "win_probability",
        "basesituation",
        "batting_against",
        "pitches",
        "cumulative",
    ]:
        raise ValueError(f"Invalid metric type: {metric_type}")
    last_name_initial = player_code[0].lower()
    resp = session.get(
        BREF_SINGLE_PLAYER_PITCHING_URL.format(
            initial=last_name_initial, player_code=player_code
        ),
        verbose=verbose,
    )
    if metric_type in ["standard", "value", "advanced"]:
        table_id = f"players_{metric_type}_pitching"
    elif metric_type == "cumulative":
        table_id = "cumulative_pitching"
    elif metric_type == "batting_against":
        table_id = "pitching_batting"
    else:
        table_id = f"pitching_{metric_type}"
    df = _required_table(resp.text, table_id, "single_player_pitching")

    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("p_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    return df


@_source_schema_errors
def single_player_fielding(
    player_code: str,
    metric_type: Literal[
        "standard", "sabermetric", "advanced_at_position", "appearances"
    ],
    position: Literal[
        "3b", "ss", "2b", "1b", "c", "c_baserunning", "lf", "rf", "cf", "p"
    ]
    | None = None,
    verbose: bool = False,
) -> pl.DataFrame:
    """Return single-player fielding statistics for one metric family.

    Args:
        player_code (str): Baseball Reference player identifier
            (for example ``"sheldsc01"``).
        metric_type (Literal[...]): Fielding table family to fetch.
            - ``"standard"``
            - ``"appearances"``
            - ``"sabermetric"``
            - ``"advanced_at_position"``
        position (Literal[...] | None, optional): Position selector used only
            when ``metric_type="advanced_at_position"``.
            Valid values are ``"3b"``, ``"ss"``, ``"2b"``, ``"1b"``, ``"c"``,
            ``"c_baserunning"``, ``"lf"``, ``"rf"``, ``"cf"``, and ``"p"``.
        verbose (bool, optional): If True, print debug information during the request process. Defaults to False. Useful for troubleshooting Cloudflare blocks.
    Raises:
        ValueError: If ``metric_type`` is not supported.
        ValueError: If ``position`` is missing for
            ``metric_type="advanced_at_position"``.
        ValueError: If ``position`` is provided when ``metric_type`` is not
            ``"advanced_at_position"``.
        ValueError: If ``position`` is invalid.
        RuntimeError: If the requested fielding table is not found.

    Returns:
        pl.DataFrame: Requested fielding table with normalized column names.

    Notes:
        - Sabermetric fielding tables are only available for players with
          non-pitcher defensive appearances.
        - Not every player has data for every advanced-at-position table.
    """

    if not isinstance(player_code, str):
        raise TypeError("player_code must be a string")
    if not player_code:
        raise ValueError("player_code must not be empty")
    if not isinstance(metric_type, str):
        raise TypeError("metric_type must be a string")
    if position is not None and not isinstance(position, str):
        raise TypeError("position must be a string or None")
    if metric_type not in [
        "standard",
        "sabermetric",
        "advanced_at_position",
        "appearances",
    ]:
        raise ValueError(f"Invalid metric type: {metric_type}")
    if metric_type == "advanced_at_position" and position is None:
        raise ValueError(
            "Position must be specified when metric_type is advanced_at_position"
        )
    if metric_type != "advanced_at_position" and position is not None:
        raise ValueError(
            "Position should not be specified when metric_type is not advanced_at_position"
        )
    if position is not None:
        if position not in [
            "3b",
            "ss",
            "2b",
            "1b",
            "c",
            "c_baserunning",
            "lf",
            "rf",
            "cf",
            "p",
        ]:
            raise ValueError(f"Invalid position: {position}")
    table_id = ""
    if metric_type == "standard":
        table_id = "players_standard_fielding"
    elif metric_type == "sabermetric":
        table_id = "advanced_fielding"
    elif metric_type == "appearances":
        table_id = metric_type
    else:
        table_id = f"advanced_fielding_{position}"
    last_name_initial = player_code[0].lower()
    resp = session.get(
        BREF_SINGLE_PLAYER_FIELDING_URL.format(
            initial=last_name_initial, player_code=player_code
        ),
        verbose=verbose,
    )
    df = _required_table(resp.text, table_id, "single_player_fielding")
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("f_", "")))
    df = df.select(pl.all().name.map(lambda col_name: col_name.replace("_abbr", "")))
    return df
