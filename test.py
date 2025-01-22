import time

import pybaseballstats as pyb

# start = time.time()
# game_pk = 775300
# single_game_data = pyb.statcast_single_game(game_pk=game_pk, extra_stats=True)
# print(f"Time for single game: {time.time() - start}")
# single_game_data.collect().write_parquet(
#     "statcast_single_game.parquet",
# )
start = time.time()
start_dt = "2015-01-01"
end_dt = "2024-12-24"
data = pyb.statcast_date_range(start_dt=start_dt, end_dt=end_dt, extra_stats=True)
print(f"Time for date range: {time.time() - start}")
data.collect().write_parquet(f"{start_dt}_{end_dt}_statcast.parquet")
