# Statcast Documentation

This module provides functions to retrieve data from the [Statcast](https://baseballsavant.mlb.com/statcast_search) website, which allows the extraction of pitch-by-pitch level Statcast data for MLB games.

## Available Functions

- `pitch_by_pitch_data(...)`: Fetches Statcast data for a specific date range.
  - Use team abbreviation to filter by team. (AZ, ATL, KC, etc...)
  - Currently this function doesn't support filtering by player, but it can be extended in the future.

## Example Usage

```python
from pybaseballstats.statcast import pitch_by_pitch_data

# Fetch Statcast data for a specific date range
data = pitch_by_pitch_data(start_date="2022-05-01", end_date="2022-05-31")

# Fetch Statcast data for a specific date range + specific team"
data = pitch_by_pitch_data(start_date="2022-05-01", end_date="2022-05-31", team="NYY")

```
