# Fangraphs Single Game Documentation

## Source

The data is pulled from Fangraphs single game play-by-play pages:

- URL format: `https://www.fangraphs.com/wins.aspx?date={date}&team={team}`

## Available Functions

- `fangraphs_single_game_play_by_play`: Returns play-by-play data for a specific game on a given date and team

## Function Details

### fangraphs_single_game_play_by_play()

**Parameters:**

- `date` (str): Date in 'YYYY-MM-DD' format specifying which game to retrieve
- `team` (FangraphsSingleGameTeams): Team enum value specifying which team's game to retrieve
- `return_pandas` (bool, optional): Whether to return a pandas DataFrame. Defaults to False (returns polars DataFrame)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Play-by-play data for the specified game

**Raises:**

- `ValueError`: If date is in the future
- `ValueError`: If date is before 1977-04-06 (earliest available data)
- `ValueError`: If team is not of type FangraphsSingleGameTeams

**Columns Returned:**

- `Inning`: Inning number
- `Outs`: Number of outs when play occurred
- `Batter`: Player at bat
- `Pitcher`: Pitcher facing the batter
- `Base State`: Runners on base situation
- `Play`: Description of the play
- `Leverage Index`: Situational importance of the at-bat
- `Win Probability Added`: Change in win probability from the play
- `Run Expectancy`: Expected runs in the inning
- `Win Expectancy`: Team's probability of winning after the play

## Team Options

Use the `FangraphsSingleGameTeams` enum for the team parameter. Available teams:

```python
from pybaseballstats.fangraphs_single_game import FangraphsSingleGameTeams

# View all available teams
print(FangraphsSingleGameTeams.show_options())
```

**Available Teams:**

- Angels, Astros, Athletics, Blue_Jays, Braves, Brewers, Cardinals, Cubs
- Diamondbacks, Dodgers, Giants, Guardians, Mariners, Marlins, Mets, Nationals
- Orioles, Padres, Phillies, Pirates, Rangers, Rays, Red_Sox, Reds
- Rockies, Royals, Tigers, Twins, White_Sox, Yankees

## Usage Examples

### Basic Usage

```python
# Option 1: Direct import
from pybaseballstats.fangraphs_single_game import (
    fangraphs_single_game_play_by_play,
    FangraphsSingleGameTeams
)

# Get play-by-play data for Yankees game on specific date
pbp_data = fangraphs_single_game_play_by_play(
    date="2023-07-15",
    team=FangraphsSingleGameTeams.Yankees
)

# Option 2: Module import
import pybaseballstats as pyb
pbp_data = pyb.fangraphs_single_game.fangraphs_single_game_play_by_play(
    date="2023-07-15",
    team=pyb.fangraphs_single_game.FangraphsSingleGameTeams.Yankees
)
```

## Date Format Requirements

- **Format**: Use 'YYYY-MM-DD' format (e.g., "2023-07-15")
- **Range**: Data available from April 6, 1977 to present
- **Validation**: Function automatically validates date format and range

```python
# Valid date formats
valid_dates = [
    "2023-07-15",
    "2022-10-28",
    "1977-04-06"  # Earliest available
]

# Invalid dates will raise ValueError
try:
    game_data = fangraphs_single_game_play_by_play(
        date="2030-01-01",  # Future date - will fail
        team=FangraphsSingleGameTeams.Yankees
    )
except ValueError as e:
    print(f"Error: {e}")
```

## Performance Notes

This function uses direct HTTP requests to Fangraphs, making it faster than Selenium-based functions. Typical execution time is 1-3 seconds per function call.

## Data Coverage

- **Historical Range**: April 6, 1977 to present
- **Game Availability**: Only games that actually occurred on the specified date
- **Team Coverage**: All current MLB teams with historical team names

## Error Handling

The function will raise exceptions if:

- Date is in an invalid format
- Date is in the future or before 1977-04-06
- Team enum is not properly specified
- No game exists for the specified date and team combination

Always use proper error handling when calling this function, especially when processing multiple games.
