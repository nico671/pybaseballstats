from datetime import date, datetime

STATCAST_SINGLE_GAME_URL = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&type=details&game_pk={game_pk}"
STATCAST_DATE_RANGE_URL = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&player_type=pitcher&game_date_gt={start_date}&game_date_lt={end_date}&sort_col=pitches&player_event_sort=api_p_release_speed&sort_order=desc&type=details#results"
STATCAST_YEAR_RANGES = {
    2022: (date(2022, 3, 17), date(2022, 11, 5)),
    2016: (date(2016, 4, 3), date(2016, 11, 2)),
    2019: (date(2019, 3, 20), date(2019, 10, 30)),
    2017: (date(2017, 4, 2), date(2017, 11, 1)),
    2023: (date(2023, 3, 15), date(2023, 11, 1)),
    2020: (date(2020, 7, 23), date(2020, 10, 27)),
    2018: (date(2018, 3, 29), date(2018, 10, 28)),
    2015: (date(2015, 4, 5), date(2015, 11, 1)),
    2024: (date(2024, 3, 15), date(2024, 10, 25)),
    2021: (date(2021, 3, 15), date(2021, 11, 2)),
    2025: (date(2025, 3, 18), datetime.now().date()),
}
STATCAST_SINGLE_GAME_EV_PV_WP_URL = "https://baseballsavant.mlb.com/gamefeed?date={game_date}&gamePk={game_pk}&chartType=pitch&legendType=pitchName&playerType=pitcher&inning=&count=&pitchHand=&batSide=&descFilter=&ptFilter=&resultFilter=&hf={stat_type}&sportId=1&liveAb=#{game_pk}"


STATCAST_DATE_FORMAT = "%Y-%m-%d"
