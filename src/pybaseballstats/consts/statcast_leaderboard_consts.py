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


# URLS
BAT_TRACKING_URL = "https://baseballsavant.mlb.com/leaderboard/bat-tracking?attackZone=&batSide=&contactType=&count=&dateStart={start_dt}&dateEnd={end_dt}&gameType=&groupBy=&isHardHit=&minSwings={min_swings}&minGroupSwings=1&pitchHand=&pitchType=&seasonStart={start_season}&seasonEnd={end_season}&team=&type={perspective}&csv=true"

EXIT_VELO_BARRELS_URL = "https://baseballsavant.mlb.com/leaderboard/statcast?type={perspective}&year={year}&position=&team=&min={min_swings}&sort=barrels_per_pa&sortDir=desc&csv=true"


EXPECTED_STATS_URL = "https://baseballsavant.mlb.com/leaderboard/expected_statistics?type={perspective}&year={year}&position=&team=&filterType=bip&min={min_balls_in_play}&csv=true"

PITCH_ARSENAL_STATS_URL = "https://baseballsavant.mlb.com/leaderboard/pitch-arsenal-stats?type={perspective}&pitchType={pitch_type}&year={year}&team=&min={min_pa}&csv=true"

PITCH_ARSENALS_URL = "https://baseballsavant.mlb.com/leaderboard/pitch-arsenals?year={year}&min={min_pitches}&type={type}&hand={hand}&csv=true"

ARM_STRENGTH_URL = "https://baseballsavant.mlb.com/leaderboard/arm-strength?type={perspective}&year={year}&minThrows={min_throws}&pos=&team=&csv=true"

ARM_VALUE_URL = "https://baseballsavant.mlb.com/leaderboard/baserunning?game_type=All&n={min_oppurtunities}&key_base_out=All&season_end={end_season}&season_start={start_season}&split={split_years}&team=&type={perspective}&with_team_only=1&csv=true"


CATCHER_BLOCKING_URL = "https://baseballsavant.mlb.com/leaderboard/catcher-blocking?game_type=All&n={min_pitches}&season_end={end_season}&season_start={start_season}&split={split_years}&team=&type={perspective}&with_team_only=1&sortColumn=diff_runner_pbwp&sortDirection=desc&players=&selected_idx=0&csv=true"


CATCHER_FRAMING_URL = "https://baseballsavant.mlb.com/catcher_framing?year={year}&team=&min={min_pitches_called}&type={perspective}&sort=4%2C1&csv=true"

CATCHER_POPTIME_URL = "https://baseballsavant.mlb.com/leaderboard/poptime?year={year}&team=&min2b={min_2b_attempts}&min3b={min_3b_attempts}&csv=true"

OUTFIELD_CATCH_PROB_URL = "https://baseballsavant.mlb.com/leaderboard/catch_probability?type=player&min={min_oppurtunities}&year={year}&total=5&sort=2&sortDir=desc&csv=true"
OOA_URL = "https://baseballsavant.mlb.com/leaderboard/outs_above_average?type={perspective}&startYear={start_year}&endYear={end_year}&split={split_years}&team=&range=year&min={min_attempts}&pos=&roles=&viz=hide&csv=true"

BASERUNNING_RV_URL = "https://baseballsavant.mlb.com/leaderboard/baserunning-run-value?game_type=All&season_start={start_year}&season_end={end_year}&sortColumn=runner_runs_XB_swipe&sortDirection=desc&split={split_years}&n={min_oppurtunities}&team=&type={perspective}&with_team_only=1&csv=true"
BASESTEALING_RUN_VALUE_URL = "https://baseballsavant.mlb.com/leaderboard/basestealing-run-value?game_type=All&n={min_sb_oppurtunities}&pitch_hand={pitch_hand}&runner_moved={runner_movement}&target_base={target_base}&prior_pk=All&season_end={end_year}&season_start={start_year}&sortColumn=simple_stolen_on_running_act&sortDirection=desc&split={split_years}&team=&type={perspective}&with_team_only=1&expanded=0&csv=true"

PARK_FACTORS_BY_YEAR_LEADERBOARD_URL = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year={year}&batSide={bat_side}&condition={condition}&rolling={rolling_years}&parks=mlb"

PARK_FACTORS_DISTANCE_LEADERBOARD_URL = "https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=distance&year={year}&batSide=&stat=index_wOBA&condition=All&rolling=3&parks=mlb&csv=true"

STATCAST_ARM_ANGLE_URL = "https://baseballsavant.mlb.com/leaderboard/pitcher-arm-angles?batSide=&dateStart={start_date}&dateEnd={end_date}&gameType=R%7CF%7CD%7CL%7CW&groupBy=&min={min_pitches}&minGroupPitches=1&perspective={perspective}&pitchHand=&pitchType=&season=&size=small&sort=ascending&team=&csv=true"

STATCAST_SWING_DATA_LEADERBOARD_URL = "https://baseballsavant.mlb.com/leaderboard/bat-tracking/swing-path-attack-angle?attackZone={attack_zone}&batSide={bat_side}&contactType={contact_type}&count={counts}&dateStart={start_date}&dateEnd={end_date}&gameType={game_type}&isHardHit={is_hard_hit}&minSwings={min_swings}&pitchHand={pitch_hand}&pitchType={pitch_types}&seasonStart={start_year}&seasonEnd={end_year}{team_needs_enum}&gameType={game_type}&type={data_type}&csv=true"

STATCAST_BATTING_STANCE_LEADERBOARD_URL = "https://baseballsavant.mlb.com/visuals/batting-stance?batSide={bat_side}&contactType={contact_type}&gameType={game_type}&isHardHit={is_hard_hit}&minSwings={min_swings}&seasonStart={start_year}&seasonEnd={end_year}&csv=true"
