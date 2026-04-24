from datetime import datetime
from typing import Literal, Tuple, Union

from pybaseballstats.consts.fangraphs_consts import (
    FangraphsBattingPosTypes,
    FangraphsLeaderboardTeams,
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


def validate_hand_param(handedness: Literal["L", "R", "S", ""]) -> str:
    if handedness not in ["L", "R", "S", ""]:
        raise ValueError("handedness must be one of ['L', 'R', 'S', '']")

    return handedness


def validate_age_params(min_age: int, max_age: int) -> None:
    if not (14 <= min_age <= 56):
        raise ValueError("min_age must be between 14 and 56")
    if not (14 <= max_age <= 56):
        raise ValueError("max_age must be between 14 and 56")
    if min_age > max_age:
        raise ValueError("min_age cannot be greater than max_age")
    return


def validate_ind_param(split_seasons: bool) -> str:
    if not isinstance(split_seasons, bool):
        raise ValueError("split_seasons must be a boolean value")
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
        raise ValueError("start_season cannot be greater than end_season")
    return str(start_season), str(end_season)


def validate_league_param(league: Literal["", "al", "nl"]) -> str:
    if league not in ["", "al", "nl"]:
        raise ValueError("league must be one of '', 'al', or 'nl'")
    return league


def validate_team_stat_split_param(
    team: FangraphsLeaderboardTeams, stat_split: str
) -> str:
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
        assert isinstance(team, FangraphsLeaderboardTeams)
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
    assert isinstance(active_roster_only, bool), (
        "active_roster_only must be a boolean value"
    )
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
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    assert start_dt is not None, (
        "Could not parse start_date, ensure it is in 'YYYY-MM-DD' format"
    )
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    assert end_dt is not None, (
        "Could not parse end_date, ensure it is in 'YYYY-MM-DD' format"
    )
    if start_dt > end_dt:
        raise ValueError("start_date must be before end_date")
    # ensure year range is valid
    if start_dt.year < 1871:
        raise ValueError("start_date year must be 1871 or later")
    current_year = datetime.now().year
    if start_dt.year > current_year:
        raise ValueError(f"end_date year cannot be later than {current_year}")
    if end_dt.year < 1871:
        raise ValueError("end_date year must be 1871 or later")
    if end_dt.year > current_year:
        raise ValueError(f"end_date year cannot be later than {current_year}")
    return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d")


def validate_seasons_and_dates_together(
    start_season: int | None,
    end_season: int | None,
    start_date: str | None,
    end_date: str | None,
) -> bool:
    if (start_season is not None) and (start_date is not None):
        raise ValueError(
            "Specify either seasons (start_season, end_season) OR dates (start_date, end_date), but not both."
        )
    if (start_season is None) and (start_date is None):
        raise ValueError(
            "You must provide either a start or end season (start_season, end_season) OR a start date (start_date, end_date)."
        )
    if start_season:
        # using seasons
        return True
    else:
        # using dates
        return False
