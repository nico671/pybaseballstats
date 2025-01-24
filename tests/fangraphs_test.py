import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb

# print(pyb.show_fangraphs_batting_stat_types())
# print(pyb.show_batting_pos_options())
#     # stat type
#     stat_types[stat_type],
#     # position
#     "all",
#     # league
#     "",
#     # start date
#     "2024-04-01",
#     # end date
#     "2024-05-01",
#     # qual
#     "y",
#     # start season
#     "",
#     # end season
#     "",
data = pyb.fangraphs_batting_range(
    start_date="2024-04-01",
    end_date="2024-05-01",
    stat_types=None,
    return_pandas=False,
    pos="all",
    league="",
    qual="y",
    start_season=None,
    end_season=None,
)
