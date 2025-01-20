import time

import pybaseballstats as pyb

game_pk = 775300
print(pyb.statcast_single_game(game_pk=game_pk, extra_stats=True).head())
start = time.time()
start_dt = "2015-01-01"
end_dt = "2024-12-24"
data = pyb.statcast_date_range(start_dt=start_dt, end_dt=end_dt, extra_stats=True)
print(f"Time: {time.time() - start}")
print(data.collect().head())
