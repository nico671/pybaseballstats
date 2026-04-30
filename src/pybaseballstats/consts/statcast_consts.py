from datetime import date
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
STATCAST_SINGLE_PLAYER_STATS_URL = "https://baseballsavant.mlb.com/statcast_search/csv?hfPT=&hfAB=&hfGT=R%7C&hfPR=&hfZ=&hfStadium=&hfBBL=&hfNewZones=&hfPull=&hfC=&hfSea={season}%7C&hfSit=&player_type={player_type}&hfOuts=&home_road=&pitcher_throws=&batter_stands=&hfSA=&hfEventOuts=&hfEventRuns=&hfABSFlag=&game_date_gt=&game_date_lt=&hfMo=&hfTeam=&hfOpponent=&hfRO=&position=&hfInfield=&hfOutfield=&hfInn=&hfBBT=&{player_lookup_param}={player_id}&hfFlag=is%5C.%5C.bunt%5C.%5C.not%7Cis%5C.%5C.competitive%7C&metric_1=&group_by=name&min_pitches=0&min_results=0&min_pas=0&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc&chk_stats_pa=on&chk_stats_abs=on&chk_stats_bip=on&chk_stats_hits=on&chk_stats_singles=on&chk_stats_dbls=on&chk_stats_triples=on&chk_stats_hrs=on&chk_stats_so=on&chk_stats_k_percent=on&chk_stats_bb=on&chk_stats_bb_percent=on&chk_stats_hbp=on&chk_stats_whiffs=on&chk_stats_swings=on&chk_stats_api_break_z_with_gravity=on&chk_stats_api_break_x_arm=on&chk_stats_api_break_z_induced=on&chk_stats_api_break_x_batter_in=on&chk_stats_ba=on&chk_stats_xba=on&chk_stats_xbadiff=on&chk_stats_obp=on&chk_stats_xobp=on&chk_stats_xobpdiff=on&chk_stats_slg=on&chk_stats_xslg=on&chk_stats_xslgdiff=on&chk_stats_woba=on&chk_stats_xwoba=on&chk_stats_wobadiff=on&chk_stats_barrels_total=on&chk_stats_babip=on&chk_stats_iso=on&chk_stats_swing_miss_percent=on&chk_stats_delev_run_exp=on&chk_stats_delev_pitcher_run_exp=on&chk_stats_delev_batter_run_value_per_100=on&chk_stats_delev_pitcher_run_value_per_100=on&chk_stats_unadj_run_exp=on&chk_stats_unadj_pitcher_run_exp=on&chk_stats_unadj_batter_run_value_per_100=on&chk_stats_unadj_pitcher_run_value_per_100=on&chk_stats_velocity=on&chk_stats_effective_speed=on&chk_stats_spin_rate=on&chk_stats_release_pos_z=on&chk_stats_release_pos_x=on&chk_stats_release_extension=on&chk_stats_plate_x=on&chk_stats_plate_z=on&chk_stats_arm_angle=on&chk_stats_launch_speed=on&chk_stats_hyper_speed=on&chk_stats_launch_angle=on&chk_stats_bbdist=on&chk_stats_hardhit_percent=on&chk_stats_barrels_per_bbe_percent=on&chk_stats_barrels_per_pa_percent=on&chk_stats_sweetspot_speed_mph=on&chk_stats_attack_angle=on&chk_stats_swing_length=on&chk_stats_attack_direction=on&chk_stats_swing_path_tilt=on&chk_stats_rate_ideal_attack_angle=on&chk_stats_intercept_ball_minus_batter_pos_x_inches=on&chk_stats_intercept_ball_minus_batter_pos_y_inches=on&chk_stats_pos3_int_start_distance=on&chk_stats_pos4_int_start_distance=on&chk_stats_pos5_int_start_distance=on&chk_stats_pos6_int_start_distance=on&chk_stats_pos7_int_start_distance=on&chk_stats_pos8_int_start_distance=on&chk_stats_pos9_int_start_distance=on#results"
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
    2025: (date(2025, 3, 18), date(2025, 11, 1)),
    2026: (date(2026, 3, 25), date(2026, 11, 1)),
}
STATCAST_SINGLE_GAME_EV_PV_WP_URL = "https://baseballsavant.mlb.com/gamefeed?date={game_date}&gamePk={game_pk}&chartType=pitch&legendType=pitchName&playerType=pitcher&inning=&count=&pitchHand=&batSide=&descFilter=&ptFilter=&resultFilter=&hf={stat_type}&sportId=1"
STATCAST_DATE_FORMAT = "%Y-%m-%d"
