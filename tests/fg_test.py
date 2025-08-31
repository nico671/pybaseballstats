import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb

print(pyb.fangraphs.fangraphs_batting_leaderboard(start_season=2024, end_season=2024))
