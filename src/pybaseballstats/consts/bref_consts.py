from enum import Enum


# team enum
class BREFTeams(Enum):
    ANGELS = "ANA"
    DIAMONDBACKS = "ARI"
    BRAVES = "ATL"
    ORIOLES = "BAL"
    RED_SOX = "BOS"
    CUBS = "CHC"
    WHITE_SOX = "CHW"
    REDS = "CIN"
    GUARDIANS = "CLE"
    ROCKIES = "COL"
    TIGERS = "DET"
    MARLINS = "FLA"
    ASTROS = "HOU"
    ROYALS = "KCR"
    DODGERS = "LAD"
    BREWERS = "MIL"
    TWINS = "MIN"
    METS = "NYM"
    YANKEES = "NYY"
    ATHLETICS = "OAK"
    PHILLIES = "PHI"
    PIRATES = "PIT"
    PADRES = "SDP"
    MARINERS = "SEA"
    GIANTS = "SFG"
    CARDINALS = "STL"
    RAYS = "TBD"
    RANGERS = "TEX"
    BLUE_JAYS = "TOR"
    NATIONALS = "WSN"

    @classmethod
    def show_options(cls):
        return "\n".join([f"{team.name}: {team.value}" for team in cls])


# urls
# bref_draft URLS
BREF_DRAFT_YEAR_ROUND_URL = "https://www.baseball-reference.com/draft/index.fcgi?year_ID={year}&draft_round={round}&draft_type=junreg&query_type=year_round&from_type_4y=0&from_type_jc=0&from_type_hs=0&from_type_unk=0"
TEAM_YEAR_DRAFT_URL = "https://www.baseball-reference.com/draft/index.fcgi?team_ID={team}&year_ID={year}&draft_type=junreg&query_type=franch_year&from_type_hs=0&from_type_4y=0&from_type_unk=0&from_type_jc=0"

# bref_manager URLS
BREF_MANAGERS_GENERAL_URL = (
    "https://www.baseball-reference.com/leagues/majors/{year}-managers.shtml"
)
BREF_MANAGER_TENDENCIES_URL = "https://www.baseball-reference.com/leagues/majors/{year}-managers.shtml#manager_tendencies"

# bref_single_player URLS
BREF_SINGLE_PLAYER_URL = (
    "https://www.baseball-reference.com/players/{initial}/{player_code}.shtml"
)
BREF_SINGLE_PLAYER_SABERMETRIC_FIELDING_URL = (
    "https://www.baseball-reference.com/players/{initial}/{player_code}-field.shtml"
)

# bref_teams URLS

BREF_TEAMS_GENERAL_URL = "https://www.baseball-reference.com/teams/{team_code}/"
