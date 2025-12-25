# Fangraphs Single Game Data Documentation

This module provides functionality for extracting single game data from [Fangraphs](https://www.fangraphs.com/). It currently only includes a function to pull play-by-play data for a specific game, but more functionality may be added in the future.

## Available Functions

- `fangraphs_single_game_play_by_play(...)`: Returns a DataFrame of play-by-play data for a given date and team from Fangraphs.

## Example Usage

### Fetching Play-by-Play Data for a Single Game

This function takes two parameters: `date`, which is a string representing the date of the game in 'YYYY-MM-DD' format, and `team`, which is a member of the FangraphsSingleGameTeams enum.

```python
# list available teams
import pybaseballstats.fangraphs_single_game as fsg
print(fsg.FangraphsSingleGameTeams.show_options())

# Fetch play-by-play data for a specific game
import pybaseballstats.fangraphs_single_game as fsg
game_date = "2023-04-01"
team = fsg.FangraphsSingleGameTeams.Angels
play_by_play_data = fsg.fangraphs_single_game_play_by_play(date=game_date, team=team)
print(play_by_play_data)
```
