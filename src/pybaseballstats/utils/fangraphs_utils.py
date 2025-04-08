from datetime import datetime
from typing import List, Literal, Optional, Tuple, Union

from pybaseballstats.utils.fangraphs_consts import (
    FangraphsBattingPosTypes,
    FangraphsBattingStatType,
    FangraphsFieldingStatType,
    FangraphsPitchingStatType,
    FangraphsTeams,
)

FANGRAPHS_BATTING_API_URL = "https://www.fangraphs.com/api/leaders/major-league/data?age=&pos={pos}&stats=bat&lg={league}&qual={min_pa}&season={end_season}&season1={start_season}&startdate={start_date}&enddate={end_date}&month={month}&hand={batting_hand}&team={team}&pageitems=2000000000&pagenum=1&rost={active_roster_only}&players=0&postseason=&sort=21,d"


def fangraphs_validate_dates(
    start_date: str, end_date: str
) -> Tuple[datetime.date, datetime.date]:
    """Validate and convert date strings (YYYY-MM-DD) to datetime.date objects."""
    date_format = "%Y-%m-%d"

    try:
        start_dt = datetime.strptime(start_date, date_format).date()
        end_dt = datetime.strptime(end_date, date_format).date()
    except ValueError:
        raise ValueError(
            f"Dates must be in YYYY-MM-DD format. Got start_date='{start_date}', end_date='{end_date}'"
        )

    if start_dt > end_dt:
        raise ValueError(
            f"start_date ({start_dt}) cannot be after end_date ({end_dt})."
        )

    return start_dt, end_dt


def fangraphs_batting_input_val(
    start_date: Union[str, None] = None,
    end_date: Union[str, None] = None,
    start_season: Union[int, None] = None,
    end_season: Union[int, None] = None,
    min_pa: Union[str, int] = "y",
    stat_types: List[FangraphsBattingStatType] = None,
    fielding_position: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
    active_roster_only: bool = False,
    team: FangraphsTeams = FangraphsTeams.ALL,
    league: Literal["nl", "al", ""] = "",
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    batting_hand: Literal["R", "L", "S", ""] = "",
):
    # start_date, end_date, start_season, end_season validation
    # Ensure that either (start_date & end_date) OR (start_season & end_season) are provided
    if (start_date and end_date) and (start_season and end_season):
        raise ValueError(
            "Specify either (start_date, end_date) OR (start_season, end_season), but not both."
        )

    if not (start_date and end_date) and not (start_season and end_season):
        raise ValueError(
            "You must provide either (start_date, end_date) OR (start_season, end_season)."
        )

    # Validate and convert dates if provided
    if start_date and end_date:
        start_date, end_date = fangraphs_validate_dates(start_date, end_date)
        start_season = None
        end_season = None
        print(f"Using date range: {start_date} to {end_date}")

    # Validate seasons if provided
    if start_season and end_season:
        if start_season > end_season:
            raise ValueError(
                f"start_season ({start_season}) cannot be after end_season ({end_season})."
            )
        print(f"Using season range: {start_season} to {end_season}")
        start_date = None
        end_date = None

    # min_pa validation
    if isinstance(min_pa, str):
        if min_pa not in ["y"]:
            raise ValueError("If min_pa is a string, it must be 'y' (qualified).")
    elif isinstance(min_pa, int):
        if min_pa < 0:
            raise ValueError("min_pa must be a positive integer.")
    else:
        raise ValueError("min_pa must be a string or integer.")

    # fielding_position validation
    if not isinstance(fielding_position, FangraphsBattingPosTypes):
        raise ValueError(
            "fielding_position must be a valid FangraphsBattingPosTypes value"
        )

    # active_roster_only validation
    if not isinstance(active_roster_only, bool):
        raise ValueError("active_roster_only must be a boolean value.")
    if active_roster_only:
        print("Only active roster players will be included.")
        active_roster_only = 1
    else:
        print("All players will be included.")
        active_roster_only = 0

    # team validation
    if not isinstance(team, FangraphsTeams):
        raise ValueError("team must be a valid FangraphsTeams value")
    else:
        print(f"Filtering by team: {team}")
        team = team.value
    # league validation
    if league not in ["nl", "al", ""]:
        raise ValueError("league must be 'nl', 'al', or an empty string.")
    if league:
        print(f"Filtering by league: {league}")

    if (min_age is not None and max_age is None) or (
        min_age is None and max_age is not None
    ):
        raise ValueError("Both min_age and max_age must be provided or neither")
    if min_age is None:
        min_age = 14
    if max_age is None:
        max_age = 56
    if min_age > max_age:
        raise ValueError(
            f"min_age ({min_age}) cannot be greater than max_age ({max_age})"
        )
    if min_age < 14:
        raise ValueError("min_age must be at least 14")
    if max_age > 56:
        raise ValueError("max_age must be at most 56")

    # batting_hand validation
    if batting_hand not in ["R", "L", "S", ""]:
        raise ValueError("batting_hand must be 'R', 'L', 'S', or an empty string.")

    stat_cols = set()
    # stat_types validation
    if stat_types is None:
        for stat_type in FangraphsBattingStatType:
            for stat in stat_type.value:
                stat_cols.add(stat)
    else:
        for stat_type in stat_types:
            if not isinstance(stat_type, FangraphsBattingStatType):
                raise ValueError(
                    "stat_types must be a list of valid FangraphsBattingStatType values"
                )
            for stat in stat_type.value:
                stat_cols.add(stat)
    stat_types = list(stat_cols)
    return (
        start_date,
        end_date,
        start_season,
        end_season,
        min_pa,
        fielding_position,
        active_roster_only,
        team,
        league,
        min_age,
        max_age,
        batting_hand,
        stat_types,
    )


FANGRAPHS_FIELDING_API_URL = "https://www.fangraphs.com/api/leaders/major-league/data?age=&pos={fielding_position}&stats=fld&lg={league}&qual={min_inn}&season={end_year}&season1={start_year}&startdate=&enddate=&month=0&hand=&team={team}&pageitems=2000000000&pagenum=1&ind=0&rost={active_roster_only}&players=0&type=1&postseason=&sortdir=default&sortstat=Defense"


def fangraphs_fielding_input_val(
    start_year: Union[int, None] = None,
    end_year: Union[int, None] = None,
    min_inn: Union[str, int] = "y",
    stat_types: List[FangraphsFieldingStatType] = None,
    active_roster_only: bool = False,
    team: FangraphsTeams = FangraphsTeams.ALL,
    league: Literal["nl", "al", ""] = "",
    fielding_position: FangraphsBattingPosTypes = FangraphsBattingPosTypes.ALL,
):
    if not (start_year and end_year):
        raise ValueError("You must provide (start_year, end_year).")

    # Validate seasons if provided
    if start_year and end_year:
        if start_year > end_year:
            raise ValueError(
                f"start_year ({start_year}) cannot be after end_year ({end_year})."
            )
        print(f"Using season range: {start_year} to {end_year}")

    # min_pa validation
    if isinstance(min_inn, str):
        if min_inn not in ["y"]:
            raise ValueError("If min_inn is a string, it must be 'y' (qualified).")
    elif isinstance(min_inn, int):
        if min_inn < 0:
            raise ValueError("min_inn must be a positive integer.")
    else:
        raise ValueError("min_inn must be a string or integer.")

    # fielding_position validation
    if not isinstance(fielding_position, FangraphsBattingPosTypes):
        raise ValueError(
            "fielding_position must be a valid FangraphsBattingPosTypes value"
        )

    # active_roster_only validation
    if not isinstance(active_roster_only, bool):
        raise ValueError("active_roster_only must be a boolean value.")
    if active_roster_only:
        print("Only active roster players will be included.")
        active_roster_only = 1
    else:
        print("All players will be included.")
        active_roster_only = 0

    # team validation
    if not isinstance(team, FangraphsTeams):
        raise ValueError("team must be a valid FangraphsTeams value")
    else:
        print(f"Filtering by team: {team}")
        team = team.value
    # league validation
    if league not in ["nl", "al", ""]:
        raise ValueError("league must be 'nl', 'al', or an empty string.")
    if league:
        print(f"Filtering by league: {league}")

    stat_cols = set()
    # stat_types validation
    if stat_types is None:
        for stat_type in FangraphsFieldingStatType:
            for stat in stat_type.value:
                stat_cols.add(stat)
    else:
        for stat_type in stat_types:
            if not isinstance(stat_type, FangraphsFieldingStatType):
                raise ValueError(
                    "stat_types must be a list of valid FangraphsFieldingStatType values"
                )
            for stat in stat_type.value:
                stat_cols.add(stat)
    stat_types = list(stat_cols)
    return (
        start_year,
        end_year,
        min_inn,
        fielding_position,
        active_roster_only,
        team,
        league,
        stat_types,
    )


FANGRAPHS_PITCHING_API_URL = "https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&lg={league}&qual={min_ip}&season={end_year}&season1={start_year}&startdate={start_date}&enddate={end_date}&month={month}&hand={pitching_hand}&team={team}&pagenum=1&pageitems=2000000000&ind=0&rost={active_roster_only}&stats={starter_reliever}&players=0&type=0&postseason=&sortdir=default&sortstat=SO"


def fangraphs_pitching_range_input_val(
    start_date: Union[str, None] = None,
    end_date: Union[str, None] = None,
    start_year: Union[int, None] = None,
    end_year: Union[int, None] = None,
    min_ip: Union[str, int] = "y",
    stat_types: List[FangraphsPitchingStatType] = None,
    active_roster_only: bool = False,
    team: FangraphsTeams = FangraphsTeams.ALL,
    league: Literal["nl", "al", ""] = "",
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    pitching_hand: Literal["R", "L", "S", ""] = "",
    starter_reliever: Literal["sta", "rel", "pit"] = "pit",
):
    if (start_date and end_date) and (start_year and end_year):
        raise ValueError(
            "Specify either (start_date, end_date) OR (start_year, end_year), but not both."
        )

    if not (start_date and end_date) and not (start_year and end_year):
        raise ValueError(
            "You must provide either (start_date, end_date) OR (start_year, end_year)."
        )

    # Validate and convert dates if provided
    if start_date and end_date:
        start_date, end_date = fangraphs_validate_dates(start_date, end_date)
        start_year = None
        end_year = None
        print(f"Using date range: {start_date} to {end_date}")

    # Validate seasons if provided
    if start_year and end_year:
        if start_year > end_year:
            raise ValueError(
                f"start_season ({start_year}) cannot be after end_season ({end_year})."
            )
        print(f"Using season range: {start_year} to {end_year}")
        start_date = None
        end_date = None

    if isinstance(min_ip, str):
        if min_ip not in ["y"]:
            raise ValueError("If min_ip is a string, it must be 'y' (qualified).")
    elif isinstance(min_ip, int):
        if min_ip < 0:
            raise ValueError("min_ip must be a positive integer.")
    else:
        raise ValueError("min_ip must be a string or integer.")

    if stat_types is None:
        stat_types = [stat for stat in list(FangraphsPitchingStatType)]
    else:
        if not stat_types:
            raise ValueError("stat_types must not be an empty list.")
        for stat in stat_types:
            if stat not in list(FangraphsPitchingStatType):
                raise ValueError(f"Invalid stat type: {stat}")

    # active_roster_only validation
    if not isinstance(active_roster_only, bool):
        raise ValueError("active_roster_only must be a boolean value.")
    if active_roster_only:
        print("Only active roster players will be included.")
        active_roster_only = 1
    else:
        print("All players will be included.")
        active_roster_only = 0

    # team validation
    if not isinstance(team, FangraphsTeams):
        raise ValueError("team must be a valid FangraphsTeams value")
    else:
        print(f"Filtering by team: {team}")
        team = team.value
    # league validation
    if league not in ["nl", "al", ""]:
        raise ValueError("league must be 'nl', 'al', or an empty string.")
    if league:
        print(f"Filtering by league: {league}")

    if (min_age is not None and max_age is None) or (
        min_age is None and max_age is not None
    ):
        raise ValueError("Both min_age and max_age must be provided or neither")
    if min_age is None:
        min_age = 14
    if max_age is None:
        max_age = 56
    if min_age > max_age:
        raise ValueError(
            f"min_age ({min_age}) cannot be greater than max_age ({max_age})"
        )
    if min_age < 14:
        raise ValueError("min_age must be at least 14")
    if max_age > 56:
        raise ValueError("max_age must be at most 56")

    if pitching_hand not in ["R", "L", "S", ""]:
        raise ValueError("pitching_hand must be 'R', 'L', 'S', or an empty string.")

    if starter_reliever not in ["sta", "rel", "pit"]:
        raise ValueError("starter_reliever must be 'sta', 'rel', or 'pit'.")
    stat_cols = set()
    # stat_types validation
    if stat_types is None:
        for stat_type in FangraphsPitchingStatType:
            for stat in stat_type.value:
                stat_cols.add(stat)
    else:
        for stat_type in stat_types:
            if not isinstance(stat_type, FangraphsPitchingStatType):
                raise ValueError(
                    "stat_types must be a list of valid FangraphsPitchingStatType values"
                )
            for stat in stat_type.value:
                stat_cols.add(stat)
    stat_types = list(stat_cols)
    return (
        start_date,
        end_date,
        start_year,
        end_year,
        min_ip,
        stat_types,
        active_roster_only,
        team,
        league,
        min_age,
        max_age,
        pitching_hand,
        starter_reliever,
        stat_types,
    )
