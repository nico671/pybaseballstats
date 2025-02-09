from src.pybaseballstats.fangraphs import fangraphs_pitching_range

data = fangraphs_pitching_range(
    start_date="2021-04-01", end_date="2021-04-30", stat_types=None
)
print(data)
