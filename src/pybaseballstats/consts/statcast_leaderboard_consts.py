from enum import Enum

PARK_FACTOR_DIMENSIONS_URL = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=dimensions&year={season}&batSide=&stat=index_wOBA&condition=All&rolling=3&parks=mlb&fenceStatType={metric_type}"
PARK_FACTOR_YEARLY_URL = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year={season}&batSide={bat_side}&stat=index_wOBA&condition={condition}&rolling={rolling_years}&parks=mlb"
PARK_FACTOR_DISTANCE_URL = "http://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=distance&year={season}&parks=mlb"
TIMER_INFRACTIONS_LEADERBOARD_URL = "https://baseballsavant.mlb.com/leaderboard/pitch-timer-infractions?type={perspective}&season={season}&min_pitches={min_pitches}&include_zeroes=0&sortColumn=N_pitches&sortDirection=asc&csv=true"
ARM_STRENGTH_LEADERBOARD_URL = "https://baseballsavant.mlb.com/leaderboard/arm-strength?type={stat_type}&year={year}&minThrows={min_throws}&pos={pos}&team={team}&csv=true"


class StatcastLeaderboardsTeams(Enum):
    ANGELS = 108
    ASTROS = 117
    ATHLETICS = 133
    BLUE_JAYS = 141
    BRAVES = 144
    BREWERS = 158
    CARDINALS = 138
    CUBS = 112
    D_BACKS = 109
    DODGERS = 119
    GIANTS = 137
    GUARDIANS = 114
    MARINERS = 136
    MARLINS = 146
    METS = 121
    NATIONALS = 120
    ORIOLES = 110
    PADRES = 135
    PHILLIES = 143
    PIRATES = 134
    RANGERS = 140
    RAYS = 139
    REDS = 113
    RED_SOX = 111
    ROCKIES = 115
    ROYALS = 118
    TIGERS = 116
    TWINS = 142
    WHITE_SOX = 145
    YANKEES = 147

    # Would give results for any game with at least team in the specified league. Unusable currently.
    # AMERICAN_LEAGUE = "AmericanL"
    # NATIONAL_LEAGUE = "NationalL"

    @classmethod
    def show_options(cls):
        return "\n".join(f"{team.name}: {team.value}" for team in cls)


ARM_STRENGTH_POS_INPUT_MAP = {
    "All": "",
    "2b_ss_3b": "arm_inf",
    "outfield": "arm_of",
    "1b": "arm_1b",
    "2b": "arm_2b",
    "3b": "arm_3b",
    "shortstop": "arm_ss",
    "lf": "arm_lf",
    "cf": "arm_cf",
    "rf": "arm_rf",
}
