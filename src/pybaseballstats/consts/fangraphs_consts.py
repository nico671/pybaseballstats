from enum import Enum


# ENUMS
class FangraphsFieldingStatType(Enum):
    STANDARD = [
        "Name",
        "Team",
        "Pos",
        "G",
        "GS",
        "Inn",
        "PO",
        "A",
        "E",
        "FE",
        "TE",
        "DP",
        "DPS",
        "DPT",
        "DPF",
        "Scp",
        "SB",
        "CS",
        "PB",
        "WP",
        "FP",
        "TZ",
    ]
    ADVANCED = [
        "Name",
        "Team",
        "Pos",
        "Inn",
        "rSB",
        "rGDP",
        "rARM",
        "rGFP",
        "rPM",
        "rSZ",
        "rTS",
        "rCERA",
        "DRS",
        "BIZ",
        "Plays",
        "RZR",
        "OOZ",
        "TZL",
        "FSR",
        "CPP",
        "RPP",
        "ARM",
        "DPR",
        "RngR",
        "ErrR",
        "UZR",
        "UZR/150",
        "Defense",
    ]
    STATCAST = [
        "Name",
        "Team",
        "Pos",
        "Inn",
        "Made0",
        "Prob0",
        "Made10",
        "Prob10",
        "Made40",
        "Prob40",
        "Made60",
        "Prob60",
        "Made90",
        "Prob90",
        "Made100",
        "Prob100",
        "CStrikes",
        "CFraming",
        "OAA",
        "rFRP",
        "aFRP",
        "bFRP",
        "tFRP",
        "fFRP",
        "FRP",
    ]

    @classmethod
    def show_options(cls):
        return "\n".join([f"{team.name}: {team.value}" for team in cls])


class FangraphsPitchingStatType(Enum):
    DASHBOARD = [
        "Name",
        "Team",
        "W",
        "L",
        "SV",
        "G",
        "GS",
        "IP",
        "K/9",
        "BB/9",
        "HR/9",
        "BABIP",
        "LOB%",
        "GB%",
        "HR/FB",
        "pivFA",
        "ERA",
        "xERA",
        "FIP",
        "xFIP",
        "WAR",
    ]
    STANDARD = [
        "Name",
        "Team",
        "W",
        "L",
        "ERA",
        "G",
        "GS",
        "QS",
        "CG",
        "ShO",
        "SV",
        "HLD",
        "BS",
        "IP",
        "TBF",
        "H",
        "R",
        "ER",
        "HR",
        "BB",
        "IBB",
        "HBP",
        "WP",
        "BK",
        "SO",
    ]
    ADVANCED = [
        "Name",
        "Team",
        "K/9",
        "BB/9",
        "K/BB",
        "HR/9",
        "K%",
        "BB%",
        "K-BB%",
        "AVG",
        "WHIP",
        "BABIP",
        "LOB%",
        "ERA-",
        "FIP-",
        "xFIP-",
        "ERA",
        "FIP",
        "E-F",
        "xFIP",
        "SIERA",
    ]
    BATTED_BALL = [
        "Name",
        "Team",
        "BABIP",
        "GB/FB",
        "LD%",
        "GB%",
        "FB%",
        "IFFB%",
        "HR/FB",
        "RS",
        "RS/9",
        "Balls",
        "Strikes",
        "Pitches",
        "Pull%",
        "Cent%",
        "Oppo%",
        "Soft%",
        "Med%",
        "Hard%",
    ]
    WIN_PROBABILITY = [
        "Name",
        "Team",
        "WPA",
        "-WPA",
        "+WPA",
        "RE24",
        "REW",
        "pLI",
        "inLI",
        "gmLI",
        "exLI",
        "Pulls",
        "WPA/LI",
        "Clutch",
        "SD",
        "MD",
    ]
    VALUE = [
        "Name",
        "Team",
        "RA9-Wins",
        "BIP-Wins",
        "LOB-Wins",
        "BS-Wins",
        "RAR",
        "WAR",
        "Dollars",
    ]
    PLUS_STATS = [
        "Name",
        "Team",
        "IP",
        "K/9+",
        "BB/9+",
        "K/BB+",
        "HR/9+",
        "K%+",
        "BB%+",
        "AVG+",
        "WHIP+",
        "BABIP+",
        "LOB%+",
        "ERA-",
        "FIP-",
        "xFIP-",
        "LD%+",
        "GB%+",
        "FB%+",
    ]
    STATCAST = [
        "Name",
        "Team",
        "IP",
        "Events",
        "EV",
        "maxEV",
        "LA",
        "Barrels",
        "Barrel%",
        "HardHit",
        "HardHit%",
        "ERA",
        "xERA",
    ]
    VIOLATIONS = [
        "Name",
        "Team",
        "PPTV",
        "CPTV",
        "DGV",
        "DSV",
        "BPTV",
        "BTV",
        "rPPTV",
        "rCPTV",
        "rDGV",
        "rDSV",
        "rBPTV",
        "rBTV",
        "EBV",
        "ESV",
        "rFTeamV",
        "rBTeamV",
        "rTV",
    ]
    SPORTS_INFO_PITCH_TYPE = [
        "Name",
        "Team",
        "FB%1",
        "FBv",
        "SL%",
        "SLv",
        "CT%",
        "CTv",
        "CB%",
        "CBv",
        "CH%",
        "CHv",
        "SF%",
        "SFv",
        "KN%",
        "KNv",
        "XX%",
    ]
    SPORTS_INFO_PITCH_VALUE = [
        "Name",
        "Team",
        "wFB",
        "wSL",
        "wCT",
        "wCB",
        "wCH",
        "wSF",
        "wKN",
        "wFB/C",
        "wSL/C",
        "wCT/C",
        "wCB/C",
        "wCH/C",
        "wSF/C",
        "wKN/C",
    ]
    SPORTS_INFO_PLATE_DISCIPLINE = [
        "Name",
        "Team",
        "O-Swing%",
        "Z-Swing%",
        "Swing%",
        "O-Contact%",
        "Z-Contact%",
        "Contact%",
        "Zone%",
        "F-Strike%",
        "SwStr%",
        "CStr%",
        "C+SwStr%",
    ]
    STATCAST_PITCH_TYPE = [
        "Name",
        "Team",
        "IP",
        "pfxFA%",
        "pfxFT%",
        "pfxFC%",
        "pfxFS%",
        "pfxFO%",
        "pfxSI%",
        "pfxSL%",
        "pfxCU%",
        "pfxKC%",
        "pfxEP%",
        "pfxCH%",
        "pfxSC%",
        "pfxKN%",
        "pfxUN%",
    ]
    STATCAST_VELO = [
        "Name",
        "Team",
        "IP",
        "pfxvFA",
        "pfxvFT",
        "pfxvFC",
        "pfxvFS",
        "pfxvFO",
        "pfxvSI",
        "pfxvSL",
        "pfxvCU",
        "pfxvKC",
        "pfxvEP",
        "pfxvCH",
        "pfxvSC",
        "pfxvKN",
    ]
    STATCAST_H_MOVEMENT = [
        "Name",
        "Team",
        "IP",
        "pfxFA-X",
        "pfxFT-X",
        "pfxFC-X",
        "pfxFS-X",
        "pfxFO-X",
        "pfxSI-X",
        "pfxSL-X",
        "pfxCU-X",
        "pfxKC-X",
        "pfxEP-X",
        "pfxCH-X",
        "pfxSC-X",
        "pfxKN-X",
    ]
    STATCAST_V_MOVEMENT = [
        "Name",
        "Team",
        "IP",
        "pfxFA-Z",
        "pfxFT-Z",
        "pfxFC-Z",
        "pfxFS-Z",
        "pfxFO-Z",
        "pfxSI-Z",
        "pfxSL-Z",
        "pfxCU-Z",
        "pfxKC-Z",
        "pfxEP-Z",
        "pfxCH-Z",
        "pfxSC-Z",
        "pfxKN-Z",
    ]
    STATCAST_PITCH_TYPE_VALUE = [
        "Name",
        "Team",
        "IP",
        "pfxwFA",
        "pfxwFT",
        "pfxwFC",
        "pfxwFS",
        "pfxwFO",
        "pfxwSI",
        "pfxwSL",
        "pfxwCU",
        "pfxwKC",
        "pfxwEP",
        "pfxwCH",
        "pfxwSC",
        "pfxwKN",
    ]
    STATCAST_PITCH_TYPE_VALUE_PER_100 = [
        "Name",
        "Team",
        "IP",
        "pfxwFA/C",
        "pfxwFT/C",
        "pfxwFC/C",
        "pfxwFS/C",
        "pfxwFO/C",
        "pfxwSI/C",
        "pfxwSL/C",
        "pfxwCU/C",
        "pfxwKC/C",
        "pfxwEP/C",
        "pfxwCH/C",
        "pfxwSC/C",
        "pfxwKN/C",
    ]
    STATCAST_PLATE_DISCIPLINE = [
        "Name",
        "Team",
        "IP",
        "pfxO-Swing%",
        "pfxZ-Swing%",
        "pfxSwing%",
        "pfxO-Contact%",
        "pfxZ-Contact%",
        "pfxContact%",
        "pfxZone%",
        "pfxPace",
    ]
    PITCH_INFO_PITCH_TYPE = [
        "Name",
        "Team",
        "IP",
        "piFA%",
        "piFC%",
        "piFS%",
        "piSI%",
        "piCH%",
        "piSL%",
        "piCU%",
        "piCS%",
        "piKN%",
        "piSB%",
        "piXX%",
    ]
    PITCH_INFO_PITCH_VELOCITY = [
        "Name",
        "Team",
        "IP",
        "pivFA",
        "pivFC",
        "pivFS",
        "pivSI",
        "pivCH",
        "pivSL",
        "pivCU",
        "pivCS",
        "pivKN",
        "pivSB",
    ]
    PITCH_INFO_H_MOVEMENT = [
        "Name",
        "Team",
        "IP",
        "piFA-X",
        "piFC-X",
        "piFS-X",
        "piSI-X",
        "piCH-X",
        "piSL-X",
        "piCU-X",
        "piCS-X",
        "piKN-X",
        "piSB-X",
    ]
    PITCH_INFO_V_MOVEMENT = [
        "Name",
        "Team",
        "IP",
        "piFA-Z",
        "piFC-Z",
        "piFS-Z",
        "piSI-Z",
        "piCH-Z",
        "piSL-Z",
        "piCU-Z",
        "piCS-Z",
        "piKN-Z",
        "piSB-Z",
    ]
    PITCH_INFO_PITCH_TYPE_VALUE = [
        "Name",
        "Team",
        "IP",
        "piwFA",
        "piwFC",
        "piwFS",
        "piwSI",
        "piwCH",
        "piwSL",
        "piwCU",
        "piwCS",
        "piwKN",
        "piwSB",
    ]
    PITCH_INFO_PITCH_TYPE_VALUE_PER_100 = [
        "Name",
        "Team",
        "IP",
        "piwFA/C",
        "piwFC/C",
        "piwFS/C",
        "piwSI/C",
        "piwCH/C",
        "piwSL/C",
        "piwCU/C",
        "piwCS/C",
        "piwKN/C",
        "piwSB/C",
    ]
    PITCH_INFO_PLATE_DISCIPLINE = [
        "Name",
        "Team",
        "IP",
        "piO-Swing%",
        "piZ-Swing%",
        "piSwing%",
        "piO-Contact%",
        "piZ-Contact%",
        "piContact%",
        "piZone%",
        "piPace",
    ]
    PITCHING_BOT_STUFF = [
        "Name",
        "Team",
        "IP",
        "pb_s_FF",
        "pb_s_SI",
        "pb_s_FC",
        "pb_s_FS",
        "pb_s_SL",
        "pb_s_CU",
        "pb_s_CH",
        "pb_s_KC",
        "pb_overall",
        "pb_stuff",
        "pb_command",
        "pb_xRV100",
        "pb_ERA",
    ]
    PITCHING_BOT_COMMAND = [
        "Name",
        "Team",
        "IP",
        "pb_c_FF",
        "pb_c_SI",
        "pb_c_FC",
        "pb_c_FS",
        "pb_c_SL",
        "pb_c_CU",
        "pb_c_CH",
        "pb_c_KC",
        "pb_overall",
        "pb_stuff",
        "pb_command",
        "pb_xRV100",
        "pb_ERA",
    ]
    PITCHING_BOT_OVR = [
        "Name",
        "Team",
        "IP",
        "pb_o_FF",
        "pb_o_SI",
        "pb_o_FC",
        "pb_o_FS",
        "pb_o_SL",
        "pb_o_CU",
        "pb_o_CH",
        "pb_o_KC",
        "pb_overall",
        "pb_stuff",
        "pb_command",
        "pb_xRV100",
        "pb_ERA",
    ]
    STUFF_PLUS = [
        "Name",
        "Team",
        "IP",
        "sp_s_FF",
        "sp_s_SI",
        "sp_s_FC",
        "sp_s_FS",
        "sp_s_SL",
        "sp_s_CU",
        "sp_s_CH",
        "sp_s_KC",
        "sp_s_FO",
        "sp_stuff",
        "sp_location",
        "sp_pitching",
    ]
    LOCATION_PLUS = [
        "Name",
        "Team",
        "IP",
        "sp_l_FF",
        "sp_l_SI",
        "sp_l_FC",
        "sp_l_FS",
        "sp_l_SL",
        "sp_l_CU",
        "sp_l_CH",
        "sp_l_KC",
        "sp_l_FO",
        "sp_stuff",
        "sp_location",
        "sp_pitching",
    ]
    PITCHING_PLUS = [
        "Name",
        "Team",
        "IP",
        "sp_p_FF",
        "sp_p_SI",
        "sp_p_FC",
        "sp_p_FS",
        "sp_p_SL",
        "sp_p_CU",
        "sp_p_CH",
        "sp_p_KC",
        "sp_p_FO",
        "sp_stuff",
        "sp_location",
        "sp_pitching",
    ]

    @classmethod
    def show_options(cls):
        return "\n".join([f"{team.name}: {team.value}" for team in cls])


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

    @classmethod
    def show_options(cls):
        return "\n".join([f"{team.name}: {team.value}" for team in cls])


class FangraphsBattingStatType(Enum):
    DASHBOARD = [
        "Name",
        "Team",
        "G",
        "PA",
        "HR",
        "R",
        "RBI",
        "SB",
        "BB%",
        "K%",
        "ISO",
        "BABIP",
        "AVG",
        "OBP",
        "SLG",
        "wOBA",
        "xwOBA",
        "wRC+",
        "BaseRunning",
        "Offense",
        "Defense",
        "WAR",
    ]
    STANDARD = [
        "Name",
        "Team",
        "G",
        "AB",
        "PA",
        "H",
        "1B",
        "2B",
        "3B",
        "HR",
        "R",
        "RBI",
        "BB",
        "IBB",
        "SO",
        "HBP",
        "SF",
        "SH",
        "GDP",
        "SB",
        "CS",
        "AVG",
    ]
    ADVANCED = [
        "Name",
        "Team",
        "PA",
        "BB%",
        "K%",
        "BB/K",
        "AVG",
        "OBP",
        "SLG",
        "OPS",
        "ISO",
        "Spd",
        "BABIP",
        "UBR",
        "GDPRuns",
        "XBR",
        "wBsR",
        "wRC",
        "wRAA",
        "wOBA",
        "wRC+",
    ]
    BATTED_BALL = [
        "Name",
        "Team",
        "BABIP",
        "GB/FB",
        "LD%",
        "GB%",
        "FB%",
        "IFFB%",
        "HR/FB",
        "IFH",
        "IFH%",
        "BUH",
        "BUH%",
        "Pull%",
        "Cent%",
        "Oppo%",
        "Soft%",
        "Med%",
        "Hard%",
    ]
    WIN_PROBABILITY = [
        "Name",
        "Team",
        "WPA",
        "-WPA",
        "+WPA",
        "RE24",
        "REW",
        "pLI",
        "phLI",
        "PH",
        "WPA/LI",
        "Clutch",
    ]
    VALUE = [
        "Name",
        "Team",
        "Batting",
        "BaseRunning",
        "Fielding",
        "Positional",
        "Offense",
        "Defense",
        "wLeague",
        "Replacement",
        "RAR",
        "WAR",
        "Dollars",
    ]
    PLUS_STATS = [
        "Name",
        "Team",
        "PA",
        "BB%+",
        "K%+",
        "AVG+",
        "OBP+",
        "SLG+",
        "wRC+",
        "ISO+",
        "BABIP+",
        "LD%+",
        "GB%+",
        "FB%+",
        "Pull%+",
        "Cent%+",
        "Oppo%+",
    ]
    STATCAST = [
        "Name",
        "Team",
        "PA",
        "Events",
        "EV",
        "maxEV",
        "LA",
        "Barrels",
        "Barrel%",
        "HardHit",
        "HardHit%",
        "AVG",
        "xAVG",
        "SLG",
        "xSLG",
        "wOBA",
        "xwOBA",
    ]
    VIOLATIONS = [
        "Name",
        "Team",
        "PPTV",
        "CPTV",
        "DGV",
        "DSV",
        "BPTV",
        "BTV",
        "rPPTV",
        "rCPTV",
        "rDGV",
        "rDSV",
        "rBPTV",
        "rBTV",
        "EBV",
        "ESV",
        "rFTeamV",
        "rBTeamV",
        "rTV",
    ]
    SPORTS_INFO_PITCH_TYPE = [
        "Name",
        "Team",
        "FB%1",
        "FBv",
        "SL%",
        "SLv",
        "CT%",
        "CTv",
        "CB%",
        "CBv",
        "CH%",
        "CHv",
        "SF%",
        "SFv",
        "KN%",
        "KNv",
        "XX%",
    ]
    SPORTS_INFO_PITCH_VALUE = [
        "Name",
        "Team",
        "wFB",
        "wSL",
        "wCT",
        "wCB",
        "wCH",
        "wSF",
        "wKN",
        "wFB/C",
        "wSL/C",
        "wCT/C",
        "wCB/C",
        "wCH/C",
        "wSF/C",
        "wKN/C",
    ]
    SPORTS_INFO_PLATE_DISCIPLINE = [
        "Name",
        "Team",
        "O-Swing%",
        "Z-Swing%",
        "Swing%",
        "O-Contact%",
        "Z-Contact%",
        "Contact%",
        "Zone%",
        "F-Strike%",
        "SwStr%",
        "CStr%",
        "C+SwStr%",
    ]
    STATCAST_PITCH_TYPE = [
        "Name",
        "Team",
        "PA",
        "pfxFA%",
        "pfxFT%",
        "pfxFC%",
        "pfxFS%",
        "pfxFO%",
        "pfxSI%",
        "pfxSL%",
        "pfxCU%",
        "pfxKC%",
        "pfxEP%",
        "pfxCH%",
        "pfxSC%",
        "pfxKN%",
        "pfxUN%",
    ]
    STATCAST_VELO = [
        "Name",
        "Team",
        "PA",
        "pfxvFA",
        "pfxvFT",
        "pfxvFC",
        "pfxvFS",
        "pfxvFO",
        "pfxvSI",
        "pfxvSL",
        "pfxvCU",
        "pfxvKC",
        "pfxvEP",
        "pfxvCH",
        "pfxvSC",
        "pfxvKN",
    ]
    STATCAST_H_MOVEMENT = [
        "Name",
        "Team",
        "PA",
        "pfxFA-X",
        "pfxFT-X",
        "pfxFC-X",
        "pfxFS-X",
        "pfxFO-X",
        "pfxSI-X",
        "pfxSL-X",
        "pfxCU-X",
        "pfxKC-X",
        "pfxEP-X",
        "pfxCH-X",
        "pfxSC-X",
        "pfxKN-X",
    ]
    STATCAST_V_MOVEMENT = [
        "Name",
        "Team",
        "PA",
        "pfxFA-Z",
        "pfxFT-Z",
        "pfxFC-Z",
        "pfxFS-Z",
        "pfxFO-Z",
        "pfxSI-Z",
        "pfxSL-Z",
        "pfxCU-Z",
        "pfxKC-Z",
        "pfxEP-Z",
        "pfxCH-Z",
        "pfxSC-Z",
        "pfxKN-Z",
    ]
    STATCAST_PITCH_TYPE_VALUE = [
        "Name",
        "Team",
        "PA",
        "pfxwFA",
        "pfxwFT",
        "pfxwFC",
        "pfxwFS",
        "pfxwFO",
        "pfxwSI",
        "pfxwSL",
        "pfxwCU",
        "pfxwKC",
        "pfxwEP",
        "pfxwCH",
        "pfxwSC",
        "pfxwKN",
    ]
    STATCAST_PITCH_TYPE_VALUE_PER_100 = [
        "Name",
        "Team",
        "PA",
        "pfxwFA/C",
        "pfxwFT/C",
        "pfxwFC/C",
        "pfxwFS/C",
        "pfxwFO/C",
        "pfxwSI/C",
        "pfxwSL/C",
        "pfxwCU/C",
        "pfxwKC/C",
        "pfxwEP/C",
        "pfxwCH/C",
        "pfxwSC/C",
        "pfxwKN/C",
    ]
    STATCAST_PLATE_DISCIPLINE = [
        "Name",
        "Team",
        "PA",
        "pfxO-Swing%",
        "pfxZ-Swing%",
        "pfxSwing%",
        "pfxO-Contact%",
        "pfxZ-Contact%",
        "pfxContact%",
        "pfxZone%",
        "pfxPace",
    ]
    PITCH_INFO_PITCH_TYPE = [
        "Name",
        "Team",
        "PA",
        "piFA%",
        "piFC%",
        "piFS%",
        "piSI%",
        "piCH%",
        "piSL%",
        "piCU%",
        "piCS%",
        "piKN%",
        "piSB%",
        "piXX%",
    ]
    PITCH_INFO_PITCH_VELOCITY = [
        "Name",
        "Team",
        "PA",
        "pivFA",
        "pivFC",
        "pivFS",
        "pivSI",
        "pivCH",
        "pivSL",
        "pivCU",
        "pivCS",
        "pivKN",
        "pivSB",
    ]
    PITCH_INFO_H_MOVEMENT = [
        "Name",
        "Team",
        "PA",
        "piFA-X",
        "piFC-X",
        "piFS-X",
        "piSI-X",
        "piCH-X",
        "piSL-X",
        "piCU-X",
        "piCS-X",
        "piKN-X",
        "piSB-X",
    ]
    PITCH_INFO_V_MOVEMENT = [
        "Name",
        "Team",
        "PA",
        "piFA-Z",
        "piFC-Z",
        "piFS-Z",
        "piSI-Z",
        "piCH-Z",
        "piSL-Z",
        "piCU-Z",
        "piCS-Z",
        "piKN-Z",
        "piSB-Z",
    ]
    PITCH_INFO_PITCH_TYPE_VALUE = [
        "Name",
        "Team",
        "PA",
        "piwFA",
        "piwFC",
        "piwFS",
        "piwSI",
        "piwCH",
        "piwSL",
        "piwCU",
        "piwCS",
        "piwKN",
        "piwSB",
    ]
    PITCH_INFO_PITCH_TYPE_VALUE_PER_100 = [
        "Name",
        "Team",
        "PA",
        "piwFA/C",
        "piwFC/C",
        "piwFS/C",
        "piwSI/C",
        "piwCH/C",
        "piwSL/C",
        "piwCU/C",
        "piwCS/C",
        "piwKN/C",
        "piwSB/C",
    ]
    PITCH_INFO_PLATE_DISCIPLINE = [
        "Name",
        "Team",
        "PA",
        "piO-Swing%",
        "piZ-Swing%",
        "piSwing%",
        "piO-Contact%",
        "piZ-Contact%",
        "piContact%",
        "piZone%",
        "piPace",
    ]

    @classmethod
    def show_options(cls):
        return "\n".join([f"{team.name}: {team.value}" for team in cls])


class FangraphsSingleGameTeams(Enum):
    Angels = "Angels"
    Astros = "Astros"
    Athletics = "Athletics"
    Blue_Jays = "Blue+Jays"
    Braves = "Braves"
    Brewers = "Brewers"
    Cardinals = "Cardinals"
    Cubs = "Cubs"
    Diamondbacks = "Diamondbacks"
    Dodgers = "Dodgers"
    Giants = "Giants"
    Guardians = "Guardians"
    Mariners = "Mariners"
    Marlins = "Marlins"
    Mets = "Mets"
    Nationals = "Nationals"
    Orioles = "Orioles"
    Padres = "Padres"
    Phillies = "Phillies"
    Pirates = "Pirates"
    Rangers = "Rangers"
    Rays = "Rays"
    Red_Sox = "Red+Sox"
    Reds = "Reds"
    Rockies = "Rockies"
    Royals = "Royals"
    Tigers = "Tigers"
    Twins = "Twins"
    White_Sox = "White+Sox"
    Yankees = "Yankees"

    @classmethod
    def show_options(cls):
        return "\n".join([f"{team.name}: {team.value}" for team in cls])


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

    @classmethod
    def show_options(cls):
        return "\n".join([f"{team.name}: {team.value}" for team in cls])


# URLS
FG_SINGLE_GAME_URL = (
    "https://www.fangraphs.com/boxscore.aspx?date={date}&team={team}&dh=0"
)

FANGRAPHS_BATTING_API_URL = "https://www.fangraphs.com/api/leaders/major-league/data?age=&pos={pos}&stats=bat&lg={league}&qual={min_pa}&ind={split_seasons}&season={end_season}&season1={start_season}&startdate={start_date}&enddate={end_date}&month={month}&hand={batting_hand}&team={team}&pageitems=2000000000&pagenum=1&rost={active_roster_only}&players=0&postseason=&sort=21,d"
FANGRAPHS_FIELDING_API_URL = "https://www.fangraphs.com/api/leaders/major-league/data?age=&pos={fielding_position}&stats=fld&lg={league}&qual={min_inn}&season={end_year}&season1={start_year}&startdate=&enddate=&month=0&hand=&team={team}&pageitems=2000000000&pagenum=1&ind=0&rost={active_roster_only}&players=0&type=1&postseason=&sortdir=default&sortstat=Defense"
FANGRAPHS_PITCHING_API_URL = "https://www.fangraphs.com/api/leaders/major-league/data?age=&pos=all&lg={league}&qual={min_ip}&season={end_year}&season1={start_year}&startdate={start_date}&enddate={end_date}&month={month}&ind={split_seasons}&hand={pitching_hand}&team={team}&pagenum=1&pageitems=2000000000&ind=0&rost={active_roster_only}&stats={starter_reliever}&players=0&type=0&postseason=&sortdir=default&sortstat=SO"
