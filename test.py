import time

import pybaseball as pb

import statcast

# game_pk = 775300
# print(statcast_single_game(game_pk=game_pk))
start = time.time()
start_dt = "2022-08-24"
end_dt = "2024-03-24"
data = statcast.statcast(start_dt=start_dt, end_dt=end_dt, extra_stats=False)
print(f"Time: {time.time() - start}")

print(data.shape)
start = time.time()
confirm = pb.statcast(start_dt=start_dt, end_dt=end_dt)
print(f"Time: {time.time() - start}")
print(confirm.shape)
print(data.shape[0] == confirm.shape[0])
