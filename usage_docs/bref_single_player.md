# Baseball Reference Single Player Documentation

This module provides functions to retrieve data from the [Baseball Reference](https://www.baseball-reference.com/) website, specifically for single player statistics.

## Available Functions

- `single_player_standard_batting(...)`: Fetches standard batting statistics for a single player.
- `single_player_advanced_batting(...)`: Fetches advanced batting statistics for a single player.
- `single_player_value_batting(...)`: Fetches value batting statistics for a single player.
- `single_player_standard_fielding(...)`: Fetches standard fielding statistics for a single player.
- `single_player_sabermetric_fielding(...)`: Fetches advanced fielding statistics for a single player.
- `single_player_standard_pitching(...)`: Fetches standard pitching statistics for a single player.
- `single_player_advanced_pitching(...)`: Fetches advanced pitching statistics for a single player.
- `single_player_value_pitching(...)`: Fetches value pitching statistics for a single player.

## Function Parameters

All functions in this module use:

- `player_code` (str): Baseball Reference player identifier (example: `troutmi01`).

## Example Usage

All functions require a `player_code` parameter (Baseball Reference player identifier, e.g. `troutmi01`).

You can get a valid code from:

- the player's Baseball Reference URL, or
- `pybaseballstats.retrosheet.player_lookup`.

Since all of these functions are so similar, we will only show an example of one of them here. The usage for the other functions is analogous.

```python
# Assuming you already looked up player_code (e.g. via retrosheet.player_lookup)
import pybaseballstats.bref_single_player as bsp

df = bsp.single_player_standard_batting(player_code="troutmi01")
print(df)
```

## Notes

1. Each function returns a Polars DataFrame.
2. These functions use Baseball Reference pages/tables and may be slower than API-backed endpoints.
3. Some functions rely on Playwright-backed page loading for dynamic content.
