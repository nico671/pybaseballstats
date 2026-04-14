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


# Historical Baseball Reference franchise codes by year, generated from
# notebooks/bref_code_switches_progress.json.
# Mapping key is the stable public enum code, and each tuple is
# (start_year, end_year, baseball_reference_team_code).
BREF_TEAM_CODE_SWITCHES: dict[str, tuple[tuple[int, int, str], ...]] = {
    "ANA": (
        (1961, 1964, "LAA"),
        (1965, 1996, "CAL"),
        (1997, 2004, "ANA"),
        (2005, 2026, "LAA"),
    ),
    "ARI": ((1998, 2026, "ARI"),),
    "ATL": ((1876, 1952, "BSN"), (1953, 1965, "MLN"), (1966, 2026, "ATL")),
    "BAL": ((1901, 1901, "MLA"), (1902, 1953, "SLB"), (1954, 2026, "BAL")),
    "BOS": ((1901, 2026, "BOS"),),
    "CHC": ((1876, 2026, "CHC"),),
    "CHW": ((1901, 2026, "CHW"),),
    "CIN": ((1882, 2026, "CIN"),),
    "CLE": ((1901, 2026, "CLE"),),
    "COL": ((1993, 2026, "COL"),),
    "DET": ((1901, 2026, "DET"),),
    "FLA": ((1993, 2011, "FLA"), (2012, 2026, "MIA")),
    "HOU": ((1962, 2026, "HOU"),),
    "KCR": ((1969, 2026, "KCR"),),
    "LAD": ((1884, 1957, "BRO"), (1958, 2026, "LAD")),
    "MIL": ((1969, 1969, "SEP"), (1970, 2026, "MIL")),
    "MIN": ((1901, 1960, "WSH"), (1961, 2026, "MIN")),
    "NYM": ((1962, 2026, "NYM"),),
    "NYY": ((1903, 2026, "NYY"),),
    "OAK": (
        (1901, 1954, "PHA"),
        (1955, 1967, "KCA"),
        (1968, 2024, "OAK"),
        (2025, 2026, "ATH"),
    ),
    "PHI": ((1883, 2026, "PHI"),),
    "PIT": ((1882, 2026, "PIT"),),
    "SDP": ((1969, 2026, "SDP"),),
    "SEA": ((1977, 2026, "SEA"),),
    "SFG": ((1883, 1957, "NYG"), (1958, 2026, "SFG")),
    "STL": ((1882, 2026, "STL"),),
    "TBD": ((1998, 2007, "TBD"), (2008, 2026, "TBR")),
    "TEX": ((1961, 1971, "WSA"), (1972, 2026, "TEX")),
    "TOR": ((1977, 2026, "TOR"),),
    "WSN": ((1969, 2004, "MON"), (2005, 2026, "WSN")),
}


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

BREF_TEAMS_SCHEDULE_RESULTS_URL = (
    "https://www.baseball-reference.com/teams/{team_code}/{year}-schedule-scores.shtml"
)
BREF_TEAMS_ROSTER_URL = "https://www.baseball-reference.com/teams/{team_code}/{year}-roster.shtml#all_appearances"

BREF_TEAMS_BATTING_BASE_URL = (
    "https://www.baseball-reference.com/teams/{team_code}/{year}-batting.shtml"
)
BREF_TEAMS_PITCHING_BASE_URL = (
    "https://www.baseball-reference.com/teams/{team_code}/{year}-pitching.shtml"
)
BREF_TEAMS_FIELDING_BASE_URL = (
    "https://www.baseball-reference.com/teams/{team_code}/{year}-fielding.shtml"
)
BREF_SINGLE_PLAYER_BATTING_URL = (
    "https://www.baseball-reference.com/players/{initial}/{player_code}-bat.shtml"
)
