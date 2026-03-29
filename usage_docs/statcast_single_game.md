# Baseball Savant Single Game Data Documentation

This module provides functionality to retrieve information from [Baseball Savant](https://baseballsavant.mlb.com/) for a single MLB game.

## Available Functions

- `get_available_game_pks_for_date(...)`: Returns a list of all available gamePKs for a given date, as well as information on the home and away team for each game.
- `single_game_pitch_by_pitch(...)`: Returns a dataframe containing pitch-by-pitch information for a specific game.

> Note: Only the two functions above are currently exported in this module.

## Function Parameters

### `get_available_game_pks_for_date(game_date)`

- `game_date` (str): Date in `YYYY-MM-DD` format.

### `single_game_pitch_by_pitch(game_pk)`

- `game_pk` (int): Baseball Savant game identifier.

## Example Usage

### Getting Available Game PKs for a Date

This function takes a single parameter, `game_date`, which is a string representing the date in 'YYYY-MM-DD' format.

```python
import pybaseballstats.statcast_single_game as ssg
# Get available game PKs for April 1, 2023
available_games = ssg.get_available_game_pks_for_date("2023-04-01")
print(available_games)
```

### Fetching Pitch-by-Pitch Data for a Single Game

This function takes one parameter, `game_pk` (Baseball Savant game ID).

```python
import pybaseballstats.statcast_single_game as ssg
# Fetch pitch-by-pitch data for a specific game
game_pk = 634373
pitch_data = ssg.single_game_pitch_by_pitch(game_pk=game_pk)
print(pitch_data)
```

## Notes

1. `get_available_game_pks_for_date` internally calls `statcast.pitch_by_pitch_data` for the given day and groups results by `game_pk`.
2. `single_game_pitch_by_pitch` directly pulls one-game CSV data from Baseball Savant.
3. Both functions return standard Python/Polars objects and can be used in scripts or notebooks.
