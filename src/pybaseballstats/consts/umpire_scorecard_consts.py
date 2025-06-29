from enum import Enum


class UmpireScorecardTeams(Enum):
    ALL = "*"
    DIAMONDBACKS = "AZ"
    ATHLETICS = "ATH"
    BRAVES = "ATL"
    ORIOLES = "BAL"
    RED_SOX = "BOS"
    CUBS = "CHC"
    REDS = "CIN"
    WHITE_SOX = "CWS"
    GAURDIANS = "CLE"
    ROCKIES = "COL"
    ASTROS = "HOU"
    ROYALS = "KC"
    ANGELS = "LAA"
    DODGERS = "LAD"
    MARLINS = "MIA"
    BREWERS = "MIL"
    TWINS = "MIN"
    METS = "NYM"
    YANKEES = "NYY"
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

    @classmethod
    def show_options(cls):
        return "\n".join([f"{team.name}: {team.value}" for team in cls])


UMPIRE_SCORECARD_GAMES_URL = "https://umpscorecards.com/api/games?startDate={start_date}&endDate={end_date}&seasonType={game_type}&team={team}"
UMPIRE_SCORECARD_UMPIRES_URL = "https://umpscorecards.com/api/umpires?startDate={start_date}&endDate={end_date}&seasonType={game_type}&team={team}"
UMPIRE_SCORECARD_TEAMS_URL = "https://umpscorecards.com/api/teams?startDate={start_date}&endDate={end_date}&seasonType={game_type}"
