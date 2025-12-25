# Baseball Savant Single Game Data Documentation

This module provides functionality to retrieve information from [Baseball Savant](https://baseballsavant.mlb.com/) for a single MLB game.

## Available Functions

- `get_available_game_pks_for_date(...)`: Returns a list of all available gamePKs for a given date, as well as information on the home and away team for each game.
- `single_game_pitch_by_pitch(...)`: Returns a dataframe containing information on each pitch thrown in a specific game on a specific date.
- `single_game_exit_velocity(...)`: Returns a dataframe containing exit velocity information for every ball put in play in a specific game on a specific date.
- `single_game_pitch_velocity(...)`: Returns a dataframe containing pitch velocity information for every pitch thrown in a specific game on a specific date.
- `single_game_win_probability(...)`: Returns a dataframe containing win probability information prior to every pitch in a specific game on a specific date.

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

This function takes a single parameter, `game_pk`, which is the Baseball Savant game ID for the desired game.

```python
import pybaseballstats.statcast_single_game as ssg
# Fetch pitch-by-pitch data for a specific game
game_pk = 634373
pitch_data = ssg.single_game_pitch_by_pitch(game_pk=game_pk)
print(pitch_data)
```

### Fetching Exit Velocity Data for a Single Game

This function takes two parameters: `game_pk`, which is the Baseball Savant game ID for the desired game, and `game_date`, which is a string representing the date of the game in 'YYYY-MM-DD' format.

```python
import pybaseballstats.statcast_single_game as ssg
# Fetch exit velocity data for a specific game
game_pk = 634373
game_date = "2023-04-01"
exit_velocity_data = ssg.single_game_exit_velocity(game_pk=game_pk, game_date=game_date)
print(exit_velocity_data)
```

### Fetching Pitch Velocity Data for a Single Game

This function takes two parameters: `game_pk`, which is the Baseball Savant game ID for the desired game, and `game_date`, which is a string representing the date of the game in 'YYYY-MM-DD' format.

```python
import pybaseballstats.statcast_single_game as ssg
# Fetch pitch velocity data for a specific game
game_pk = 634373
game_date = "2023-04-01"
pitch_velocity_data = ssg.single_game_pitch_velocity(game_pk=game_pk, game_date=game_date)
print(pitch_velocity_data)
```

### Fetching Win Probability Data for a Single Game

This function takes two parameters: `game_pk`, which is the Baseball Savant game ID for the desired game, and `game_date`, which is a string representing the date of the game in 'YYYY-MM-DD' format.

```python
import pybaseballstats.statcast_single_game as ssg
# Fetch win probability data for a specific game
game_pk = 634373
game_date = "2023-04-01"
win_probability_data = ssg.single_game_win_probability(game_pk=game_pk, game_date=game_date)
print(win_probability_data)
```
