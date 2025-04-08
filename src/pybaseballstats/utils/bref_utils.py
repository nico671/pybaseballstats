from enum import Enum

BREF_SINGLE_PLAYER_BATTING_URL = (
    "https://www.baseball-reference.com/players/{initial}/{player_code}.shtml"
)
BREF_SINGLE_PLAYER_FIELDING_URL = (
    "https://www.baseball-reference.com/players/{initial}/{player_code}-field.shtml"
)


def _extract_table(table):
    trs = table.tbody.find_all("tr")
    row_data = {}
    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) == 0:
            continue
        for td in tds:
            data_stat = td.attrs["data-stat"]
            if data_stat not in row_data:
                row_data[data_stat] = []
            row_data[data_stat].append(td.string)
    return row_data


BREF_DRAFT_URL = "https://www.baseball-reference.com/draft/index.fcgi?year_ID={draft_year}&draft_round={draft_round}&draft_type=junreg&query_type=year_round&from_type_hs=0&from_type_jc=0&from_type_4y=0&from_type_unk=0"


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


MANAGERS_URL = "https://www.baseball-reference.com/leagues/majors/{year}-managers.shtml#manager_record"

MANAGER_TENDENCY_URL = "https://www.baseball-reference.com/leagues/majors/{year}-managers.shtml#manager_tendencies"
