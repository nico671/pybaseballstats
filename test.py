import time

import pbstats.statcast as statcast

# game_pk = 775300
# print(statcast_single_game(game_pk=game_pk))
start = time.time()
start_dt = "2015-01-01"
end_dt = "2024-12-24"
data = statcast.statcast(
    start_dt=start_dt, end_dt=end_dt, extra_stats=True
).write_parquet(
    "notebooks/statcast.parquet",
)
print(f"Time: {time.time() - start}")
print(data)
