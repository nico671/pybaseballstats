from enum import Enum


#  ENUMS
class StatcastPitchTypes(Enum):
    FOUR_SEAM_FASTBALL = "FF"
    SINKER = "SI"
    CUTTER = "FC"
    CHANGEUP = "CH"
    SPLITTER = "FS"
    FORKBALL = "FO"
    SCREWBALL = "SC"
    CURVEBALL = "CU"
    KNUCKLE_CURVE = "KC"
    SLOW_CURVE = "CS"
    SLIDER = "SL"
    SWEEPER = "ST"
    SLURVE = "SV"
    KNUCKLEBALL = "KN"

    @classmethod
    def show_options(cls):
        return "\n".join([f"{team.name}: {team.value}" for team in cls])


# URLS
PITCH_TIMER_INFRACTIONS_LEADERBOARD_URL = "https://baseballsavant.mlb.com/leaderboard/pitch-timer-infractions?type={stat_type}&season={season}&min_pitches={min_pitches}&include_zeroes={include_pitchers_with_zeroes}&csv=true"
