# Statcast Single Player Documentation

This module provides functions to retrieve grouped player-season stats and pitch-by-pitch data from the [Statcast](https://baseballsavant.mlb.com/statcast_search) website for one MLB player.

## Available Functions

- `single_player_pitch_by_pitch(...)`: Fetches regular-season pitch details for one player and season.
  - Supports batter and pitcher player perspectives via `player_type`.
  - Sends the player lookup to Baseball Savant for every date chunk, so only pitches thrown by or seen by the requested player are returned.
  - Supports chunking and concurrency controls.
  - Returns a Polars `LazyFrame` by default (or `DataFrame` when `force_collect=True`).
- `single_player_season_stats(...)`: Fetches grouped Baseball Savant Statcast Search stats for one player and season.
  - Supports batter and pitcher player perspectives via `player_type`.
  - Uses MLBAM player IDs.
  - Uses a direct `requests` CSV call to Baseball Savant.
  - Returns a Polars `DataFrame`.

## Function Parameters

### `single_player_pitch_by_pitch`

`single_player_pitch_by_pitch(player_id, season, player_type, force_collect=False, *, chunk_size_days=7, show_progress=True, concurrency=None, verbose=False)`

- `player_id` (int): MLBAM player identifier.
- `season` (int): MLB season year.
- `player_type` ("batter" | "pitcher"): Player perspective. Use `"batter"` for pitches seen by the player or `"pitcher"` for pitches thrown by the player.
- `force_collect` (bool): If `True`, returns a Polars `DataFrame`; otherwise returns a Polars `LazyFrame`.
- `chunk_size_days` (int): Number of days per request chunk. Must be greater than 0.
- `show_progress` (bool): Show progress indicators while downloading and processing chunks.
- `concurrency` (int | None): Optional maximum number of concurrent HTTP requests. When omitted, concurrency is selected automatically.
- `verbose` (bool): Print additional runtime logs.

### `single_player_season_stats`

`single_player_season_stats(player_id, season, player_type, *, verbose=False)`

- `player_id` (int): MLBAM player identifier.
- `season` (int): MLB season year.
- `player_type` ("batter" | "pitcher"): Player perspective. Must be either `"batter"` or `"pitcher"`. It is not inferred from the player.
- `verbose` (bool): Print additional runtime logs.

## Return Value

### `single_player_pitch_by_pitch`

- `pl.LazyFrame` when `force_collect=False`.
- `pl.DataFrame` when `force_collect=True`.
- Each row represents a pitch from a regular-season game in the requested player's role. The season date range is configured internally, and a current-season request stops at the current date.

### `single_player_season_stats`

- Returns a `pl.DataFrame` containing Baseball Savant grouped Statcast Search stats for the requested player season.
- The query is grouped by player name and uses Baseball Savant's unfiltered pitch-result selection. If you compare against a Baseball Savant web export, make sure the web UI does not have pitch-result filters such as bunts, competitive swings, or takes selected.

## Errors

- Both functions raise `TypeError` when `player_id` or `season` is not an integer.
- Both functions raise `ValueError` when `season` is not a supported Statcast season or when `player_type` is not `"batter"` or `"pitcher"`.
- `single_player_pitch_by_pitch` raises `TypeError` when `chunk_size_days` is not an integer or when `concurrency` is neither an integer nor `None`.
- `single_player_pitch_by_pitch` raises `ValueError` when `chunk_size_days` or an explicit `concurrency` value is not positive.
- `single_player_pitch_by_pitch` raises `RuntimeError` when a chunk cannot be downloaded after retries, no matching pitches exist, or the downloaded chunks cannot be processed. It does not return partial data when a chunk fails.
- `single_player_season_stats` raises `RuntimeError` when Baseball Savant returns no CSV data for the requested player lookup, such as an invalid MLBAM ID or a valid player with no data for the requested `player_type` and season.
- `single_player_season_stats` raises `RuntimeError` when Baseball Savant returns malformed CSV content.

## Example Usage

### Fetching batter pitch-by-pitch data

```python
import pybaseballstats.statcast_single_player as ssp

# Fetch every regular-season pitch Shohei Ohtani saw in 2024
data = ssp.single_player_pitch_by_pitch(
    player_id=660271,
    season=2024,
    player_type="batter",
)
```

### Fetching pitcher pitch-by-pitch data as a DataFrame

```python
import pybaseballstats.statcast_single_player as ssp

# Fetch every regular-season pitch Yoshinobu Yamamoto threw in 2025
data = ssp.single_player_pitch_by_pitch(
    player_id=808967,
    season=2025,
    player_type="pitcher",
    force_collect=True,
)
```

### Controlling pitch-by-pitch downloads

```python
import pybaseballstats.statcast_single_player as ssp

data = ssp.single_player_pitch_by_pitch(
    player_id=808967,
    season=2025,
    player_type="pitcher",
    chunk_size_days=14,
    concurrency=4,
    show_progress=False,
    verbose=True,
)
```

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

1. `single_player_pitch_by_pitch` downloads a season in date chunks and retries failed requests. Larger chunks make fewer requests, while smaller chunks reduce the amount of data requested at once.
2. `single_player_season_stats` uses a single synchronous `requests.get` call and does not expose progress or concurrency controls.
3. `player_id` must be an MLBAM player identifier.
4. `player_type` must be either `"batter"` or `"pitcher"`; it is not inferred from the player.
5. Pitch-by-pitch queries include regular-season games only.
