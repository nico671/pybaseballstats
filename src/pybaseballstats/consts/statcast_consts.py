from datetime import date, datetime
from enum import Enum

class StatcastTeams(Enum):
    DIAMONDBACKS = "AZ"
    BRAVES = "ATL"
    ORIOLES = "BAL"
    RED_SOX = "BOS"
    CUBS = "CHC"
    REDS = "CIN"
    GUARDIANS = "CLE"
    ROCKIES = "COL"
    WHITE_SOX = "CWS"
    TIGERS = "DET"
    ASTROS = "HOU"
    ROYALS = "KC"
    ANGELS = "LAA"
    DODGERS = "LAD"
    MARLINS = "MIA"
    BREWERS = "MIL"
    TWINS = "MIN"
    METS = "NYM"
    YANKEES = "NYY"
    ATHLETICS = "OAK"
    PHILLIES = "PHI"
    PIRATES = "PIT"
    PADRES = "SD"
    MARINERS = "SEA"
    GIANTS = "SF"
    CARDINALS = "STL"
    RAYS = "TB"
    RANGERS = "TEX"
    BLUE_JAYS = "TOR"
    NATIONALS = "WSH"

    # Would give results for any game with at least team in the specified league. Unusable currently. 
    # AMERICAN_LEAGUE = "AmericanL"
    # NATIONAL_LEAGUE = "NationalL"

    @classmethod
    def show_options(cls):
        return "\n".join(f"{team.name}: {team.value}" for team in cls)

STATCAST_SINGLE_GAME_URL = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&type=details&game_pk={game_pk}"
STATCAST_DATE_RANGE_URL = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&player_type=pitcher&game_date_gt={start_date}&game_date_lt={end_date}&sort_col=pitches&team={team}&player_event_sort=api_p_release_speed&sort_order=desc&type=details#results"
STATCAST_YEAR_RANGES = {
    2015: (date(2015, 4, 5), date(2015, 11, 1)),
    2016: (date(2016, 4, 3), date(2016, 11, 2)),
    2017: (date(2017, 4, 2), date(2017, 11, 1)),
    2018: (date(2018, 3, 29), date(2018, 10, 28)),
    2019: (date(2019, 3, 20), date(2019, 10, 30)),
    2020: (date(2020, 7, 23), date(2020, 10, 27)),
    2021: (date(2021, 3, 15), date(2021, 11, 2)),
    2022: (date(2022, 3, 17), date(2022, 11, 5)),
    2023: (date(2023, 3, 15), date(2023, 11, 1)),
    2024: (date(2024, 3, 15), date(2024, 10, 25)),
    2025: (date(2025, 3, 18), datetime.now().date()),
}
STATCAST_SINGLE_GAME_EV_PV_WP_URL = "https://baseballsavant.mlb.com/gamefeed?date={game_date}&gamePk={game_pk}&chartType=pitch&legendType=pitchName&playerType=pitcher&inning=&count=&pitchHand=&batSide=&descFilter=&ptFilter=&resultFilter=&hf={stat_type}&sportId=1&liveAb=#{game_pk}"
STATCAST_DATE_FORMAT = "%Y-%m-%d"