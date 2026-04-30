# Statcast Single Player Documentation

This module provides functions to retrieve grouped player-season data from the [Statcast](https://baseballsavant.mlb.com/statcast_search) website, which allows the extraction of Baseball Savant Statcast Search stats for one MLB player.

## Available Functions

- `single_player_season_stats(...)`: Fetches grouped Baseball Savant Statcast Search stats for one player and season.
  - Supports batter and pitcher player perspectives via `player_type`.
  - Uses MLBAM player IDs.
  - Returns a Polars `DataFrame`.

## Function Parameters

`single_player_season_stats(player_id, season, player_type, *, show_progress=True, concurrency=None, verbose=False)`

- `player_id` (int): MLBAM player identifier.
- `season` (int): MLB season year.
- `player_type` ("batter" | "pitcher"): Player perspective. Must be either `"batter"` or `"pitcher"`.
- `show_progress` (bool): Show progress indicators while downloading/loading the response.
- `concurrency` (int | None): Optional max concurrency override for HTTP requests.
- `verbose` (bool): Print additional runtime logs.

## Return Value

- `pl.DataFrame` containing Baseball Savant grouped Statcast Search stats for the requested player season.
- Returns an empty `pl.DataFrame` when no data is returned for the requested player/season/player type.

## Example Usage

### Basic batter usage

```python
import pybaseballstats.statcast_single_player as ssp

# Fetch grouped Statcast Search stats for Shohei Ohtani's 2024 batting season
data = ssp.single_player_season_stats(
    player_id=660271,
    season=2024,
    player_type="batter",
)
```

### Basic pitcher usage

```python
import pybaseballstats.statcast_single_player as ssp

# Fetch grouped Statcast Search stats for Yoshinobu Yamamoto's 2025 pitching season
data = ssp.single_player_season_stats(
    player_id=808967,
    season=2025,
    player_type="pitcher",
)
```

### Selecting specific stats

```python
import pybaseballstats.statcast_single_player as ssp

data = ssp.single_player_season_stats(
    player_id=660271,
    season=2024,
    player_type="batter",
)

summary = data.select(["player_name", "pa", "ba", "slg", "woba", "xwoba"])
```

### Advanced download options

```python
import pybaseballstats.statcast_single_player as ssp

data = ssp.single_player_season_stats(
    player_id=660271,
    season=2024,
    player_type="batter",
    concurrency=1,
    show_progress=True,
    verbose=False,
)
```

## Notes

1. The function internally uses async execution for performance, but exposes a synchronous API.
2. In notebook/active-event-loop environments, it applies `nest_asyncio` so the call still works.
3. `player_id` must be an MLBAM player identifier.
4. `player_type` must be either `"batter"` or `"pitcher"`.
