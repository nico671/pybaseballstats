# Retrosheet Documentation

This module provides functionality to retrieve data from the [Retrosheet](https://retrosheet.org/) website. Specifically, it includes functions for looking up player information and retrieving ejection data.

## Available Functions

- `player_lookup`: Look up players by first and/or last name.
- `ejections_data`: Retrieve ejection data for a specific date range, ejectee, umpire, or inning.

## Example Usage

### Player Lookup

This will most often be done to use the player information returned by this function as an input to other functions in this package. The inputs to this function are flexible. You can search by first name, last name, or both. You also have the option to strip accents from names to improve search results. The parameters are as follows:

- `first_name` (str, optional): The first name of the player.
- `last_name` (str, optional): The last name of the player.
- `strip_accents` (bool, optional): Whether to strip accents from the names (default is True).

```python
import pybaseballstats.retrosheet as rs
import pybaseballstats.bref_single_player as bsp

# Lookup a player by first and last name
player_info = rs.player_lookup(first_name="Mike", last_name="Trout")
key_bbref = player_info.select(pl.col("key_bbref")).to_series()[0]  
# Use the player ID to get more detailed information from Baseball Reference
bsp.single_player_standard_batting(player_code=key_bbref)
```

### Ejections Data

This function allows you to retrieve ejection data for a specific date range, ejectee, umpire, or inning. You can combine these filters to narrow down your search. The parameters are as follows:

- `start_date` (str): The start date for the data in "MM/DD/YYYY" format.
- `end_date` (str): The end date for the data in "MM/DD/YYYY" format.
- `ejectee_name` (str, optional): The name of the player who was ejected (fuzzy matching).
- `umpire_name` (str, optional): The name of the umpire involved in the ejection (fuzzy matching).
- `inning` (int, optional): The inning during which the ejection occurred, between -1 and 20 (but not 0).

```python
import pybaseballstats.retrosheet as rs
rs.ejections_data(start_date="04/01/2010", end_date="04/30/2023", ejectee_name="Harper")
```
