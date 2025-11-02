from datetime import datetime
from typing import Literal, Tuple, Union

import dateparser

from pybaseballstats.consts.fangraphs_consts import (
    FangraphsBattingPosTypes,
    FangraphsTeams,
)


def validate_min_pa_param(min_pa: Union[int, str]) -> str:
    if isinstance(min_pa, int):
        if min_pa < 0:
            raise ValueError("min_pa must be a non-negative integer or 'y'")
        return str(min_pa)
    elif isinstance(min_pa, str):
        if min_pa.lower() != "y":
            raise ValueError("min_pa string value must be 'y'")
        return "y"
    else:
        raise ValueError("min_pa must be either a non-negative integer or 'y'")


def validate_pos_param(pos: FangraphsBattingPosTypes) -> str:
    if type(pos) is not FangraphsBattingPosTypes:
        raise ValueError("pos must be a FangraphsBattingPosTypes enum value")
    elif pos is None:
        return FangraphsBattingPosTypes.ALL.value
    else:
        return pos.value


def validate_hand_param(handedness: Literal["L", "R", "S", None]) -> str:
    if handedness not in ["L", "R", "S", None]:
        raise ValueError("handedness must be one of ['L', 'R', 'S', None]")
    elif handedness is None:
        return ""
    else:
        return handedness


def validate_age_params(min_age: int, max_age: int) -> str:
    if not (14 <= min_age <= 56):
        raise ValueError("min_age must be between 14 and 56")
    if not (14 <= max_age <= 56):
        raise ValueError("max_age must be between 14 and 56")
    if min_age > max_age:
        raise ValueError("min_age cannot be greater than max_age")
    return f"{min_age},{max_age}"


def validate_ind_param(split_seasons: bool) -> str:
    if split_seasons:
        return "1"
    else:
        return "0"


def validate_seasons_param(
    start_season: int | None, end_season: int | None
) -> Tuple[str, str]:
    current_year = datetime.now().year

    # Check if only one parameter is provided for single season
    if start_season is not None and end_season is None:
        assert start_season is not None  # for mypy
        if start_season < 1871 or start_season > current_year:
            raise ValueError(f"start_season must be between 1871 and {current_year}")
        print(
            "End season not provided, doing a single year search using the start season param."
        )
        return str(start_season), str(start_season)
    elif start_season is None and end_season is not None:
        assert end_season is not None  # for mypy
        if end_season < 1871 or end_season > current_year:
            raise ValueError(f"end_season must be between 1871 and {current_year}")
        print(
            "Start season not provided, doing a single year search using the end season param."
        )
        return str(end_season), str(end_season)
    elif start_season is None and end_season is None:
        raise ValueError("At least one season must be provided")
    assert start_season is not None and end_season is not None  # for mypy
    # Both parameters provided - validate range
    if start_season < 1871 or start_season > current_year:
        raise ValueError(f"start_season must be between 1871 and {current_year}")
    if end_season < 1871 or end_season > current_year:
        raise ValueError(f"end_season must be between 1871 and {current_year}")
    if start_season > end_season:
        print("start_season is greater than end_season, switching them")
        start_season, end_season = end_season, start_season
    return str(start_season), str(end_season)


def validate_team_stat_split_param(team: FangraphsTeams, stat_split: str) -> str:
    # handle team and stat_split together
    if stat_split and stat_split not in ["player", "team", "league"]:
        raise ValueError("stat_split must be one of 'player', 'team', or 'league'")
    if stat_split == "player":
        stat_split = ""
    elif stat_split is None:
        print("No stat_split provided, defaulting to player stats")
        stat_split = ""
    elif stat_split == "team":
        stat_split = "ts"
    elif stat_split == "league":
        stat_split = "ss"
    if team:
        team_value = str(team.value)
    else:
        team_value = ""
    team_together = ""
    if stat_split == "":
        team_together = team_value
    else:
        team_together = f"{team_value},{stat_split}"
    return team_together


def validate_active_roster_param(active_roster_only: bool) -> str:
    if active_roster_only:
        return "1"
    return "0"


def validate_season_type(season_type: str) -> str:
    if not season_type:
        print("No season_type provided, defaulting to regular season stats")
        return ""
    if season_type not in [
        "regular",
        "all_postseason",
        "world_series",
        "championship_series",
        "division_series",
        "wild_card",
    ]:
        raise ValueError("Invalid season_type")

    match season_type:
        case "regular":
            return ""
        case "all_postseason":
            return "Y"
        case "world_series":
            return "W"
        case "championship_series":
            return "L"
        case "division_series":
            return "D"
        case "wild_card":
            return "F"
    raise Exception("Unreachable code reached in validate_season_type")


def validate_dates(start_date: str | None, end_date: str | None) -> Tuple[str, str]:
    if not start_date:
        raise ValueError("start_date must be provided")
    if not end_date:
        print("No end date provided, defaulting to today's date")
        end_date = datetime.today().strftime("%Y-%m-%d")
    start_dt, end_dt = (
        dateparser.parse(start_date),
        dateparser.parse(end_date),
    )
    assert start_dt is not None, "Could not parse start_date"
    assert end_dt is not None, "Could not parse end_date"
    if start_dt > end_dt:
        raise ValueError("start_date must be before end_date")
    return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")


# def fangraphs_fielding_input_val(
#     start_year: Union[int, None] = None,
#     end_year: Union[int, None] = None,
#     min_inn: Union[str, int] = "y",
#     stat_types: List[FangraphsFieldingStatType] = None,
#     active_roster_only: bool = False,
#     team: FangraphsTeams = FangraphsTeams.ALL,
#     league: Literal["nl", "al", ""] = "",
#     fielding_position: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
# ):
#     if not (start_year and end_year):
#         raise ValueError("You must provide (start_year, end_year).")

#     # Validate seasons if provided
#     if start_year and end_year:
#         if start_year > end_year:
#             raise ValueError(
#                 f"start_year ({start_year}) cannot be after end_year ({end_year})."
#             )
#         print(f"Using season range: {start_year} to {end_year}")

#     # min_pa validation
#     if isinstance(min_inn, str):
#         if min_inn not in ["y"]:
#             raise ValueError("If min_inn is a string, it must be 'y' (qualified).")
#     elif isinstance(min_inn, int):
#         if min_inn < 0:
#             raise ValueError("min_inn must be a positive integer.")
#     else:
#         raise ValueError("min_inn must be a string or integer.")

#     # fielding_position validation
#     if not isinstance(fielding_position, FangraphsBattingPosTypes):
#         raise ValueError(
#             "fielding_position must be a valid FangraphsBattingPosTypes value"
#         )

#     # active_roster_only validation
#     if not isinstance(active_roster_only, bool):
#         raise ValueError("active_roster_only must be a boolean value.")
#     if active_roster_only:
#         print("Only active roster players will be included.")
#         active_roster_only = 1
#     else:
#         print("All players will be included.")
#         active_roster_only = 0

#     # team validation
#     if not isinstance(team, FangraphsTeams):
#         raise ValueError("team must be a valid FangraphsTeams value")
#     else:
#         print(f"Filtering by team: {team}")
#         team = team.value
#     # league validation
#     if league not in ["nl", "al", ""]:
#         raise ValueError("league must be 'nl', 'al', or an empty string.")
#     if league:
#         print(f"Filtering by league: {league}")

#     stat_cols = set()
#     # stat_types validation
#     if stat_types is None:
#         for stat_type in FangraphsFieldingStatType:
#             for stat in stat_type.value:
#                 stat_cols.add(stat)
#     else:
#         for stat_type in stat_types:
#             if not isinstance(stat_type, FangraphsFieldingStatType):
#                 raise ValueError(
#                     "stat_types must be a list of valid FangraphsFieldingStatType values"
#                 )
#             for stat in stat_type.value:
#                 stat_cols.add(stat)
#     stat_types = list(stat_cols)
#     return (
#         start_year,
#         end_year,
#         min_inn,
#         fielding_position,
#         active_roster_only,
#         team,
#         league,
#         stat_types,
#     )


# def fangraphs_pitching_range_input_val(
#     start_date: Union[str, None] = None,
#     end_date: Union[str, None] = None,
#     start_year: Union[int, None] = None,
#     end_year: Union[int, None] = None,
#     min_ip: Union[str, int] = "y",
#     stat_types: List[FangraphsPitchingStatType] = None,
#     active_roster_only: bool = False,
#     team: FangraphsTeams = FangraphsTeams.ALL,
#     league: Literal["nl", "al", ""] = "",
#     min_age: Optional[int] = None,
#     max_age: Optional[int] = None,
#     pitching_hand: Literal["R", "L", "S", ""] = "",
#     starter_reliever: Literal["sta", "rel", "pit"] = "pit",
#     split_seasons: bool = False,
# ):
#     if (start_date and end_date) and (start_year and end_year):
#         raise ValueError(
#             "Specify either (start_date, end_date) OR (start_year, end_year), but not both."
#         )

#     if not (start_date and end_date) and not (start_year and end_year):
#         raise ValueError(
#             "You must provide either (start_date, end_date) OR (start_year, end_year)."
#         )

#     # Validate and convert dates if provided
#     if start_date and end_date:
#         start_date, end_date = fangraphs_validate_dates(start_date, end_date)
#         start_year = None
#         end_year = None
#         print(f"Using date range: {start_date} to {end_date}")

#     # Validate seasons if provided
#     if start_year and end_year:
#         if start_year > end_year:
#             raise ValueError(
#                 f"start_season ({start_year}) cannot be after end_season ({end_year})."
#             )
#         print(f"Using season range: {start_year} to {end_year}")
#         start_date = None
#         end_date = None

#     if isinstance(min_ip, str):
#         if min_ip not in ["y"]:
#             raise ValueError("If min_ip is a string, it must be 'y' (qualified).")
#     elif isinstance(min_ip, int):
#         if min_ip < 0:
#             raise ValueError("min_ip must be a positive integer.")
#     else:
#         raise ValueError("min_ip must be a string or integer.")

#     if stat_types is None:
#         stat_types = [stat for stat in list(FangraphsPitchingStatType)]
#     else:
#         if not stat_types:
#             raise ValueError("stat_types must not be an empty list.")
#         for stat in stat_types:
#             if stat not in list(FangraphsPitchingStatType):
#                 raise ValueError(f"Invalid stat type: {stat}")

#     # active_roster_only validation
#     if not isinstance(active_roster_only, bool):
#         raise ValueError("active_roster_only must be a boolean value.")
#     if active_roster_only:
#         print("Only active roster players will be included.")
#         active_roster_only = 1
#     else:
#         print("All players will be included.")
#         active_roster_only = 0

#     # team validation
#     if not isinstance(team, FangraphsTeams):
#         raise ValueError("team must be a valid FangraphsTeams value")
#     else:
#         print(f"Filtering by team: {team}")
#         team = team.value
#     # league validation
#     if league not in ["nl", "al", ""]:
#         raise ValueError("league must be 'nl', 'al', or an empty string.")
#     if league:
#         print(f"Filtering by league: {league}")

#     if (min_age is not None and max_age is None) or (
#         min_age is None and max_age is not None
#     ):
#         raise ValueError("Both min_age and max_age must be provided or neither")
#     if min_age is None:
#         min_age = 14
#     if max_age is None:
#         max_age = 56
#     if min_age > max_age:
#         raise ValueError(
#             f"min_age ({min_age}) cannot be greater than max_age ({max_age})"
#         )
#     if min_age < 14:
#         raise ValueError("min_age must be at least 14")
#     if max_age > 56:
#         raise ValueError("max_age must be at most 56")

#     if pitching_hand not in ["R", "L", "S", ""]:
#         raise ValueError("pitching_hand must be 'R', 'L', 'S', or an empty string.")

#     if starter_reliever not in ["sta", "rel", "pit"]:
#         raise ValueError("starter_reliever must be 'sta', 'rel', or 'pit'.")
#     stat_cols = set()
#     # stat_types validation
#     if stat_types is None:
#         for stat_type in FangraphsPitchingStatType:
#             for stat in stat_type.value:
#                 stat_cols.add(stat)
#     else:
#         for stat_type in stat_types:
#             if not isinstance(stat_type, FangraphsPitchingStatType):
#                 raise ValueError(
#                     "stat_types must be a list of valid FangraphsPitchingStatType values"
#                 )
#             for stat in stat_type.value:
#                 stat_cols.add(stat)
#     stat_types = list(stat_cols)
#     assert isinstance(split_seasons, bool)
#     if split_seasons:
#         split_seasons = 1
#     else:
#         split_seasons = 0
#     return (
#         start_date,
#         end_date,
#         start_year,
#         end_year,
#         min_ip,
#         stat_types,
#         active_roster_only,
#         team,
#         league,
#         min_age,
#         max_age,
#         pitching_hand,
#         starter_reliever,
#         stat_types,
#         split_seasons,
#     )
