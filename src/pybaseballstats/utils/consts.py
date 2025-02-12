from enum import Enum


class FangraphsFieldingStatType(Enum):
    STANDARD = 0
    ADVANCED = 1
    STATCAST = 24


class FangraphsPitchingStatType(Enum):
    DASHBOARD = 8
    STANDARD = 0
    ADVANCED = 1
    BATTED_BALL = 2
    WIN_PROBABILITY = 3
    VALUE = 6
    PLUS_STATS = 23
    STATCAST = 24
    VIOLATIONS = 48
    SPORTS_INFO_PITCH_TYPE = 4
    SPORTS_INFO_PITCH_VALUE = 7
    SPORTS_INFO_PLATE_DISCIPLINE = 5
    STATCAST_PITCH_TYPE = 9
    STATCAST_VELO = 10
    STATCAST_H_MOVEMENT = 11
    STATCAST_V_MOVEMENT = 12
    STATCAST_PITCH_TYPE_VALUE = 13
    STATCAST_PITCH_TYPE_VALUE_PER_100 = 14
    STATCAST_PLATE_DISCIPLINE = 15
    PITCH_INFO_PITCH_TYPE = 16
    PITCH_INFO_PITCH_VELOCITY = 17
    PITCH_INFO_H_MOVEMENT = 18
    PITCH_INFO_V_MOVEMENT = 19
    PITCH_INFO_PITCH_TYPE_VALUE = 20
    PITCH_INFO_PITCH_TYPE_VALUE_PER_100 = 21
    PITCH_INFO_PLATE_DISCIPLINE = 22
    PITCHING_BOT_STUFF = 26
    PITCHING_BOT_COMMAND = 27
    PITCHING_BOT_OVR = 25
    STUFF_PLUS = 36
    LOCATION_PLUS = 37
    PITCHING_PLUS = 38


class FangraphsTeams(Enum):
    ALL = 0
    ANGELS = 1
    ASTROS = 17
    ATHLETICS = 10
    BLUE_JAYS = 14
    BRAVES = 16
    BREWERS = 23
    CARDINALS = 28
    CUBS = 17
    DIAMONDBACKS = 15
    DODGERS = 22
    GIANTS = 30
    GUARDIANS = 5
    MARINERS = 11
    MARLINS = 20
    METS = 25
    NATIONALS = 24
    ORIOLES = 2
    PADRES = 29
    PHILLIES = 26
    PIRATES = 27
    RANGERS = 13
    RAYS = 12
    RED_SOX = 3
    REDS = 18
    ROCKIES = 19
    ROYALS = 7
    TIGERS = 6
    TWINS = 8
    WHITE_SOX = 4
    YANKEES = 9


class FangraphsStatSplitTypes(Enum):
    PLAYER = ""
    TEAM = "ts"
    LEAGUE = "ss"


class FangraphsBattingStatType(Enum):
    DASHBOARD = 8
    STANDARD = 0
    ADVANCED = 1
    BATTED_BALL = 2
    WIN_PROBABILITY = 3
    VALUE = 6
    PLUS_STATS = 23
    STATCAST = 24
    VIOLATIONS = 48
    SPORTS_INFO_PITCH_TYPE = 4
    SPORTS_INFO_PITCH_VALUE = 7
    SPORTS_INFO_PLATE_DISCIPLINE = 5
    STATCAST_PITCH_TYPE = 9
    STATCAST_VELO = 10
    STATCAST_H_MOVEMENT = 11
    STATCAST_V_MOVEMENT = 12
    STATCAST_PITCH_TYPE_VALUE = 13
    STATCAST_PITCH_TYPE_VALUE_PER_100 = 14
    STATCAST_PLATE_DISCIPLINE = 15
    PITCH_INFO_PITCH_TYPE = 16
    PITCH_INFO_PITCH_VELOCITY = 17
    PITCH_INFO_H_MOVEMENT = 18
    PITCH_INFO_V_MOVEMENT = 19
    PITCH_INFO_PITCH_TYPE_VALUE = 20
    PITCH_INFO_PITCH_TYPE_VALUE_PER_100 = 21
    PITCH_INFO_PLATE_DISCIPLINE = 22


class FangraphsBattingPosTypes(Enum):
    CATCHER = "c"
    FIRST_BASE = "1b"
    SECOND_BASE = "2b"
    THIRD_BASE = "3b"
    SHORTSTOP = "ss"
    LEFT_FIELD = "lf"
    CENTER_FIELD = "cf"
    RIGHT_FIELD = "rf"
    DESIGNATED_HITTER = "dh"
    OUTFIELD = "of"
    PITCHER = "p"
    NON_PITCHER = "np"
    ALL = "all"

    def __str__(self):
        return self.value


class FangraphsLeagueTypes(Enum):
    ALL = ""
    NATIONAL_LEAGUE = "nl"
    AMERICAN_LEAGUE = "al"

    def __str__(self):
        return self.value


FANGRAPHS_BATTING_URL = (
    "https://www.fangraphs.com/leaders/major-league?"
    "pos={pos}&stats=bat&lg={league}&qual={qual}&type={stat_type}"
    "&season={end_season}&season1={start_season}"
    "&startdate={start_date}&enddate={end_date}&hand={handedness}"
    "&rost={rost}&team={team}&pagenum=1&pageitems=2000000000"
)
# "https://www.fangraphs.com/leaders/major-league?pos={pos}&lg=&qual=y&type=8&season=&season1=&startdate=2021-04-01&enddate=2021-04-30&rost=0&pageitems=2000000000&month=0&team=0&stats={starter_reliever}"
FANGRAPHS_PITCHING_URL = (
    "https://www.fangraphs.com/leaders/major-league?"
    "pos={pos}&lg={league}&qual={qual}&type={stat_type}"
    "&season={end_season}&season1={start_season}&stats={starter_reliever}"
    "&startdate={start_date}&enddate={end_date}&hand={handedness}"
    "&rost={rost}&team={team}&pagenum=1&pageitems=2000000000"
)

FANGRAPHS_FIELDING_URL = (
    "https://www.fangraphs.com/leaders/major-league?"
    "pos={pos}&stats=fld&lg={league}&qual={qual}&type={stat_type}"
    "&season={end_season}&season1={start_season}"
    "&startdate={start_date}&enddate={end_date}"
    "&rost={rost}&team={team}&pagenum=1&pageitems=2000000000"
)
