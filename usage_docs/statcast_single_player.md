# Statcast Single Player Documentation

This module provides functions to retrieve grouped player-season data from the [Statcast](https://baseballsavant.mlb.com/statcast_search) website, which allows the extraction of Baseball Savant Statcast Search stats for one MLB player.

## Available Functions

- `single_player_season_stats(...)`: Fetches grouped Baseball Savant Statcast Search stats for one player and season.
  - Supports batter and pitcher player perspectives via `player_type`.
  - Uses MLBAM player IDs.
  - Uses a direct `requests` CSV call to Baseball Savant.
  - Returns a Polars `DataFrame`.

## Function Parameters

`single_player_season_stats(player_id, season, player_type, *, verbose=False)`

- `player_id` (int): MLBAM player identifier.
- `season` (int): MLB season year.
- `player_type` ("batter" | "pitcher"): Player perspective. Must be either `"batter"` or `"pitcher"`. It is not inferred from the player.
- `verbose` (bool): Print additional runtime logs.

## Return Value

- `pl.DataFrame` containing Baseball Savant grouped Statcast Search stats for the requested player season.
- The query is grouped by player name and uses Baseball Savant's unfiltered pitch-result selection. If you compare against a Baseball Savant web export, make sure the web UI does not have pitch-result filters such as bunts, competitive swings, or takes selected.

## Errors

- Raises `TypeError` when `player_id` or `season` is not an integer.
- Raises `ValueError` when `season` is not a supported Statcast season or when `player_type` is not `"batter"` or `"pitcher"`.
- Raises `RuntimeError` when Baseball Savant returns no CSV data for the requested player lookup, such as an invalid MLBAM ID or a valid player with no data for the requested `player_type` and season.
- Raises `RuntimeError` when Baseball Savant returns malformed CSV content.

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

### Verbose logging

```python
import pybaseballstats.statcast_single_player as ssp

data = ssp.single_player_season_stats(
    player_id=660271,
    season=2024,
    player_type="batter",
    verbose=True,
)
```

### Handling a missing player lookup

```python
import pybaseballstats.statcast_single_player as ssp

try:
    data = ssp.single_player_season_stats(
        player_id=999999999,
        season=2024,
        player_type="batter",
    )
except RuntimeError as exc:
    print(exc)
    # No Statcast single-player data found for batter 999999999 in 2024.
```

## Notes

1. The function uses a single synchronous `requests.get` call and does not expose async, progress, or concurrency controls.
2. `player_id` must be an MLBAM player identifier.
3. `player_type` must be either `"batter"` or `"pitcher"`.
