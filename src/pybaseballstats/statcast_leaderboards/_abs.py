import io
from typing import List, Literal

import polars as pl
import requests

from pybaseballstats.consts.statcast_leaderboard_consts import (
    ABS_CHALLENGES_LEADERBOARD_URL,
    StatcastLeaderboardsTeams,
)


def abs_challenges_leaderboard(
    season: int,
    challenge_type: Literal[
        "batter",
        "batting-team",
        "catcher",
        "pitcher",
        "catching-team",
        "team-summary",
        "league",
    ] = "batter",
    game_type: Literal["regular", "spring", "playoff"] = "regular",
    level: Literal["mlb", "aaa"] = "mlb",
    challenging_teams: List[StatcastLeaderboardsTeams] | None = None,
    opposing_teams: List[StatcastLeaderboardsTeams] | None = None,
    pitch_types: List[
        Literal["FF", "SI", "FC", "CH", "FS", "FO", "SC", "CU", "SL", "ST", "SV", "KN"]
    ]
    | None = None,
    attack_zone: List[Literal["11", "12", "13", "14", "16", "17", "18", "19"]]
    | None = None,
    in_zone: bool | None = None,
    min_challenges: int = 0,
    min_opp_challenges: int = 0,
) -> pl.DataFrame:
    """Return Baseball Savant ABS challenge leaderboard data.

    Args:
        season (int): Season year. Must be ``2025`` or later.
        challenge_type (Literal[...], optional): Leaderboard grouping. One of
            ``"batter"``, ``"batting-team"``, ``"catcher"``, ``"pitcher"``,
            ``"catching-team"``, ``"team-summary"``, or ``"league"``.
        game_type (Literal["regular", "spring", "playoff"], optional):
            Game-type filter.
        level (Literal["mlb", "aaa"], optional): Level filter.
        challenging_teams (List[StatcastLeaderboardsTeams], optional):
            Restrict to challenging organizations.
        opposing_teams (List[StatcastLeaderboardsTeams], optional):
            Restrict to opposing organizations.
        pitch_types (List[Literal[...]] | None, optional): Restrict to one or
            more pitch types from ``FF, SI, FC, CH, FS, FO, SC, CU, SL, ST, SV, KN``.
        attack_zone (List[Literal[...]] | None, optional): Restrict to one or
            more shadow-zone buckets from ``11, 12, 13, 14, 16, 17, 18, 19``.
        in_zone (bool | None, optional): If ``True``, include only in-zone
            challenges; if ``False``, out-of-zone only; if ``None``, no filter.
        min_challenges (int, optional): Minimum number of challenges.
        min_opp_challenges (int, optional): Minimum opponent challenge count.

    Raises:
        ValueError: If any parameter fails validation.

    Returns:
        pl.DataFrame: ABS challenges leaderboard data.
    """
    # Validate inputs

    # season must be greater than 2025
    if season < 2025:
        raise ValueError("Season must be 2025 or later")

    # level must be one of the specified options
    if level not in ["mlb", "aaa"]:
        raise ValueError("Invalid level. Must be one of 'mlb' or 'aaa'")

    # challenge_type must be one of the specified options
    if challenge_type not in [
        "batter",
        "batting-team",
        "catcher",
        "pitcher",
        "catching-team",
        "team-summary",
        "league",
    ]:
        raise ValueError(
            "Invalid challenge_type. Must be one of 'batter', 'batting-team', 'catcher', 'pitcher', 'catching-team', 'team-summary', or 'league'"
        )

    # game_type must be one of the specified options
    if game_type not in ["regular", "spring", "playoff"]:
        raise ValueError(
            "Invalid game_type. Must be one of 'regular', 'spring', or 'playoff'"
        )
    # challenging_teams and opposing_teams must be lists of StatcastLeaderboardsTeams enums or None
    if challenging_teams is not None:
        if not isinstance(challenging_teams, list) or not all(
            isinstance(team, StatcastLeaderboardsTeams) for team in challenging_teams
        ):
            raise ValueError(
                "challenging_teams must be a list of StatcastLeaderboardsTeams enums or None"
            )
        else:
            challenging_teams_param_str = "|".join(
                str(team.value) for team in challenging_teams
            )
    else:
        challenging_teams_param_str = ""
    if opposing_teams is not None:
        if not isinstance(opposing_teams, list) or not all(
            isinstance(team, StatcastLeaderboardsTeams) for team in opposing_teams
        ):
            raise ValueError(
                "opposing_teams must be a list of StatcastLeaderboardsTeams enums or None"
            )
        else:
            opposing_teams_param_str = "|".join(
                str(team.value) for team in opposing_teams
            )
    else:
        opposing_teams_param_str = ""
    # pitch_types must be a list of the specified options or None
    if pitch_types is not None:
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
        if not isinstance(pitch_types, list) or not all(
            pitch in valid_pitch_types for pitch in pitch_types
        ):
            raise ValueError(
                f"pitch_types must be a list of the following options or None: {valid_pitch_types}"
            )
        else:
            pitch_types_param_str = "|".join(pitch_types)
    else:
        pitch_types_param_str = ""

    # attack_zone must be a list of the specified options or None
    if attack_zone is not None:
        valid_attack_zones = ["11", "12", "13", "14", "16", "17", "18", "19"]
        if not isinstance(attack_zone, list) or not all(
            zone in valid_attack_zones for zone in attack_zone
        ):
            raise ValueError(
                f"attack_zone must be a list of the following options or None: {valid_attack_zones}"
            )
        else:
            attack_zone_param_str = "|".join(attack_zone)
    else:
        attack_zone_param_str = ""
    # in_zone must be a boolean or None
    if in_zone is not None and not isinstance(in_zone, bool):
        raise ValueError("in_zone must be a boolean or None")
    if in_zone is True:
        in_zone_param_str = "in"
    elif in_zone is False:
        in_zone_param_str = "out"
    else:
        in_zone_param_str = ""

    # min_challenges and min_opp_challenges must be non-negative integers
    if not isinstance(min_challenges, int) or min_challenges < 0:
        raise ValueError("min_challenges must be a non-negative integer")
    if not isinstance(min_opp_challenges, int) or min_opp_challenges < 0:
        raise ValueError("min_opp_challenges must be a non-negative integer")

    url = ABS_CHALLENGES_LEADERBOARD_URL.format(
        in_zone=in_zone_param_str,
        challenging_teams=challenging_teams_param_str,
        game_type=game_type,
        level=level,
        opposing_teams=opposing_teams_param_str,
        pitch_types=pitch_types_param_str,
        attack_zone=attack_zone_param_str,
        season=season,
        challenge_type=challenge_type,
        min_challenges=min_challenges,
        min_opp_challenges=min_opp_challenges,
    )
    df = pl.read_csv(io.StringIO(requests.get(url).text))
    return df
