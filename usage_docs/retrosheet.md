# Retrosheet Documentation

This module provides functionality to retrieve data from the [Retrosheet](https://retrosheet.org/) website. Specifically, it includes functions for looking up player information and retrieving ejection data.

## Available Functions

- `player_lookup`: Look up players by first and/or last name.
- `ejections_data`: Retrieve ejection data for a specific date range, ejectee, umpire, or inning.

## Function Parameters

### `player_lookup(first_name=None, last_name=None, strip_accents=False)`

- `first_name` (str, optional): The first name of the player.
- `last_name` (str, optional): The last name of the player.
- `strip_accents` (bool, optional): Whether to normalize accents before matching. Defaults to `False`.

### `ejections_data(start_date=None, end_date=None, ejectee_name=None, umpire_name=None, inning=None)`

- `start_date` (str, optional): Start date in `MM/DD/YYYY` format.
- `end_date` (str, optional): End date in `MM/DD/YYYY` format.
- `ejectee_name` (str, optional): Case-sensitive substring filter on ejected person name.
- `umpire_name` (str, optional): Case-sensitive substring filter on umpire name.
- `inning` (int, optional): Inning filter from -1 to 20 (excluding 0).

## Example Usage

### Player Lookup

This function is most commonly used to get a player's `key_bbref` value, which can then be passed into functions in `bref_single_player`.

```python
import pybaseballstats.retrosheet as rs
import pybaseballstats.bref_single_player as bsp
import polars as pl

# Lookup a player by first and last name
player_info = rs.player_lookup(first_name="Mike", last_name="Trout")
key_bbref = player_info.select(pl.col("key_bbref")).to_series()[0]  
# Use the player ID to get more detailed information from Baseball Reference
bsp.single_player_standard_batting(player_code=key_bbref)
```

```python
# Lookup a player by last name only
import pybaseballstats.retrosheet as rs
player_info = rs.player_lookup(last_name="Rodriguez")
```

### Ejections Data

This function allows you to retrieve ejection data for a specific date range, ejectee, umpire, or inning. You can combine filters to narrow your search.

## Notes

- `start_date`/`end_date` must use `MM/DD/YYYY` format.
- If you omit `start_date` and/or `end_date`, the full available range is used for that side of the filter.

```python
import pybaseballstats.retrosheet as rs
rs.ejections_data(start_date="04/01/2010", end_date="04/30/2023", ejectee_name="Harper")
```
