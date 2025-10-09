# Statcast Documentation

This module provides functions to retrieve data from the [Statcast](https://baseballsavant.mlb.com/statcast_search) website, which allows the extraction of pitch-by-pitch level Statcast data for MLB games.

## Available Functions

- `pitch_by_pitch_data(...)`: Fetches Statcast data for a specific date range.
  - Currently this function doesn't support filtering by team or player, but it can be extended in the future.

## Example Usage

```python
from pybaseball import statcast

# Fetch Statcast data for a specific date range
data = statcast.pitch_by_pitch_data(start_date="2022-05-01", end_date="2022-05-31")
```
