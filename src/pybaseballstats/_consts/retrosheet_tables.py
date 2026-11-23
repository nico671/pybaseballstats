"""Retrosheet's published positional formats and Daily Logs column groups."""

import polars as pl

_NUMERIC = """at_bats hits doubles triples home_runs rbi sacrifice_hits
    sacrifice_flies hit_by_pitch walks intentional_walks strikeouts stolen_bases
    caught_stealing grounded_into_double_plays catchers_interference left_on_base
    pitchers_used individual_earned_runs team_earned_runs wild_pitches balks
    putouts assists errors passed_balls double_plays triple_plays""".split()
_GAME_START = """date number day visitor_team visitor_league visitor_game_number
    home_team home_league home_game_number visitor_score home_score outs day_night
    completion forfeit protest park_id attendance duration_minutes
    visitor_line_score home_line_score""".split()
_GAME_PAIRS = """plate_umpire first_base_umpire second_base_umpire third_base_umpire
    left_field_umpire right_field_umpire visitor_manager home_manager winning_pitcher
    losing_pitcher saving_pitcher game_winning_rbi_batter visitor_starting_pitcher
    home_starting_pitcher""".split()
GAME_LOG_COLUMNS = [
    *_GAME_START,
    *(f"{side}_{stat}" for side in ("visitor", "home") for stat in _NUMERIC),
    *(f"{role}_{field}" for role in _GAME_PAIRS for field in ("id", "name")),
    *(
        f"{side}_starter_{slot}_{field}"
        for side in ("visitor", "home")
        for slot in range(1, 10)
        for field in ("id", "name", "position")
    ),
    "additional_information",
    "acquisition",
]
GAME_LOG_NUMERIC = {
    "visitor_game_number",
    "home_game_number",
    "visitor_score",
    "home_score",
    "outs",
    "attendance",
    "duration_minutes",
    *GAME_LOG_COLUMNS[21:77],
    *(name for name in GAME_LOG_COLUMNS if name.endswith("_position")),
}
SCHEDULE_COLUMNS = """date number day visitor_team visitor_league visitor_game_number
    home_team home_league home_game_number day_night postponed makeup""".split()

_PLAYER_GAME_FIELDS = "date number site vishome opp win loss tie gametype box pbp eject"
PLAYER_LOG_COLUMNS = {
    "batting.csv": (
        """gid id team b_lp b_seq stattype b_pa b_ab b_r b_h b_d b_t
        b_hr b_rbi b_sh b_sf b_hbp b_w b_iw b_k b_sb b_cs b_gdp b_xi b_roe dh ph pr """
        + _PLAYER_GAME_FIELDS
    ).split(),
    "fielding.csv": (
        """gid id team d_seq d_pos stattype d_ifouts d_po d_a d_e d_dp d_tp
        d_pb d_wp d_sb d_cs d_gs """
        + _PLAYER_GAME_FIELDS
    ).split(),
    "pitching.csv": (
        """gid id team p_seq stattype p_ipouts p_noout p_bfp p_h p_d p_t
        p_hr p_r p_er p_w p_iw p_k p_hbp p_wp p_bk p_sh p_sf p_sb p_cs p_pb
        wp lp save p_gs p_gf p_cg """
        + _PLAYER_GAME_FIELDS
    ).split(),
}

PLAY_COLUMNS = """gid event inning top_bot vis_home site batteam pitteam score_v score_h
    batter pitcher lp bat_f bathand pithand balls strikes count pitches nump pa ab
    single double triple hr sh sf hbp walk k xi roe fc othout noout oth bip bunt
    ground fly line iw gdp othdp tp fle wp pb bk oa di sb2 sb3 sbh cs2 cs3 csh
    pko1 pko2 pko3 k_safe e1 e2 e3 e4 e5 e6 e7 e8 e9 outs_pre outs_post
    br1_pre br2_pre br3_pre br1_post br2_post br3_post lob_id1 lob_id2 lob_id3
    pr1_pre pr2_pre pr3_pre pr1_post pr2_post pr3_post run_b run1 run2 run3
    prun_b prun1 prun2 prun3 ur_b ur1 ur2 ur3 rbi_b rbi1 rbi2 rbi3 runs rbi er tur
    l1 l2 l3 l4 l5 l6 l7 l8 l9 lf1 lf2 lf3 lf4 lf5 lf6 lf7 lf8 lf9
    f2 f3 f4 f5 f6 f7 f8 f9 po0 po1 po2 po3 po4 po5 po6 po7 po8 po9
    a1 a2 a3 a4 a5 a6 a7 a8 a9 fseq batout1 batout2 batout3
    brout_b brout1 brout2 brout3 firstf loc hittype dpopp pivot pn
    umphome ump1b ump2b ump3b umplf umprf date gametype pbp""".split()
_PLAY_NUMERIC = set(
    """inning top_bot vis_home score_v score_h lp bat_f balls strikes nump pa ab
    single double triple hr sh sf hbp walk k xi roe fc othout noout oth bip bunt
    ground fly line iw gdp othdp tp fle wp pb bk oa di sb2 sb3 sbh cs2 cs3 csh
    pko1 pko2 pko3 k_safe outs_pre outs_post ur_b ur1 ur2 ur3 rbi_b rbi1 rbi2
    rbi3 runs rbi er tur batout1 batout2 batout3 brout_b brout1 brout2 brout3
    firstf dpopp pivot pn""".split()
) | {
    *(f"po{position}" for position in range(10)),
    *(
        f"{prefix}{position}"
        for prefix in ("e", "a", "lf")
        for position in range(1, 10)
    ),
}
_DAILY_NUMERIC = set(
    """season g lob win loss tie vruns hruns innings attendance timeofgame temp
    windspeed dh ph pr gs inn""".split()
)
_DATE_COLUMNS = {"date", "first_g", "last_g"}


def daily_type(member: str, name: str) -> type[pl.DataType]:
    if name in _DATE_COLUMNS:
        return pl.Date
    if member == "plays.csv":
        return pl.Int64 if name in _PLAY_NUMERIC else pl.String
    if (
        name in _DAILY_NUMERIC
        or name.startswith(("b_", "p_", "d_", "g_"))
        or (name.startswith("inn") and name[3:].isdigit())
        or (member == "umpire.csv" and name == "eject")
    ):
        return pl.Int64
    return pl.String
