# Umpire Scorecard Documentation

This module provides functions to retrieve data from the [Umpire Scorecards](https://umpscorecards.com/) website. This site offers detailed statistics and performance metrics for MLB umpires.

## Available Functions

- `game_type_options()`: Prints the game types for filtering.
- `game_data(...)`: Fetches umpire performance data on a game by game basis over a specific date range and set of filters.
- `umpire_data(...)`: Fetches umpire data for a specific date range and set of filters.
- `team_data(...)`: Fetches team data for a specific date range and set of filters.

## Example Usage

### Seeing Available Teams

This function doesn't return any data from the Umpire Scorecards website. Instead, it prints the available teams that can be used as filters in other functions.

```python
import pybaseballstats.umpire_scorecards as us
print(us.UmpireScorecardTeams.show_options()) # will print all of the available teams
""" 
ALL: *
DIAMONDBACKS: AZ
ATHLETICS: ATH
BRAVES: ATL
ORIOLES: BAL
RED_SOX: BOS
CUBS: CHC
REDS: CIN
WHITE_SOX: CWS
GAURDIANS: CLE
ROCKIES: COL
ASTROS: HOU
ROYALS: KC
ANGELS: LAA
DODGERS: LAD
MARLINS: MIA
BREWERS: MIL
TWINS: MIN
METS: NYM
YANKEES: NYY
PHILLIES: PHI
PIRATES: PIT
PADRES: SD
MARINERS: SEA
GIANTS: SF
CARDINALS: STL
RAYS: TB
RANGERS: TEX
BLUE_JAYS: TOR
NATIONALS: WSH
"""
```

### Understanding Game Type Options

game_type is a filter that can be used in the `game_data`, `umpire_data`, and `team_data` functions. The following function prints the available game types.

```python
import pybaseballstats.umpire_scorecards as us
us.game_type_options() # will print all of the available game types
""" 
Game Type Options:
* : All games
R : Regular Season
A : All-Star Game
P : All Postseason games
F : Wild Card games
D : Division Series games
L : League Championship Series games
W : World Series games
"""
```

### Fetching Game By Game Umpire Data

If you want umpire performance data on a game by game basis, you can use the `game_data` function. This function allows you to filter by date range, umpire, team, and game type.

#### Understanding the game by game data function parameters

Note that only the `start_date` and `end_date` parameters are required. The other parameters have default values that will return all data if not specified.

- `start_date` (str): The start date for the data in "YYYY-MM-DD" format.
- `end_date` (str): The end date for the data in "YYYY-MM-DD" format.
- `umpire_name` (str): The umpire's name to filter by. Use "" to include all umpires.
- `focus_team` (UmpireScorecardTeams): The team abbreviation to filter by. Use "*" to include all teams. See the "Seeing Available Teams" section above for a list of team abbreviations.
- `focus_team_home_away` (str): Filter by whether the focus team is home or away. Use "*" to include both. Options are "h" for home, "a" for away, and "*" for both.
- `opponent_team` (UmpireScorecardTeams): The opponent team abbreviation to filter by. Use "*" to include all teams. See the "Seeing Available Teams" section above for a list of team abbreviations.
- `game_type` (str): The type of game to filter by. Use "*" to include all game types. See the "Understanding Game Type Options" section above for a list of game types.

#### Example 1: Fetch all game data for a specific date range

```python
import pybaseballstats.umpire_scorecards as us
# 1. Fetch all game data for a specific date range
df = us.game_data(start_date="2023-04-01", end_date="2023-04-30")
print(df)
```

#### Example 2: Fetch game data for a specific umpire and team

```python
import pybaseballstats.umpire_scorecards as us
# 2. Fetch game data for a specific umpire and team
df = us.game_data(start_date="2023-04-01", end_date="2025-09-09", umpire_name="Brian O'Nora", focus_team=us.UmpireScorecardTeams.MARLINS)
print(df)
```

#### Example 3: Fetch game data for a specific team when they are playing at home against a specific opponent

```python
import pybaseballstats.umpire_scorecards as us
# 3. Fetch game data for a specific team when they are playing at home against a specific opponent
df = us.game_data(
    start_date="2023-04-01",
    end_date="2025-04-30",
    focus_team=us.UmpireScorecardTeams.DIAMONDBACKS,
    focus_team_home_away="h",
    opponent_team=us.UmpireScorecardTeams.CUBS
)
print(df)
```

### Fetching Umpire Data

If you want aggregated umpire data over a specific date range, you can use the `umpire_data` function. This function allows you to filter by date range, umpire, team, game type, and minimum games called.

#### Understanding the umpire data function parameters

The parameters are similar to those in the `game_data` function, with the addition of `min_games_called`. Please refer to the `game_data` section above for explanations of the common parameters.

- `min_games_called` (int): The minimum number of games an umpire must have called to be included in the results. Default is 0, which includes all umpires regardless of the number of games called.

#### Example 1: Fetch all umpire data for a specific date range

```python
import pybaseballstats.umpire_scorecards as us
# 1. Fetch all umpire data for a specific date range
df = us.umpire_data(start_date="2023-04-01", end_date="2023-04-30")
print(df)
```

#### Example 2: Fetch umpire data for a specific team with a minimum number of games called

```python
import pybaseballstats.umpire_scorecards as us
# 2. Fetch umpire data for a specific team with a minimum number of games called
df = us.umpire_data(
    start_date="2023-04-01",
    end_date="2025-09-09",focus_team=us.UmpireScorecardTeams.MARLINS,
    min_games_called=10,
)
print(df)
```

## Fetching Team Data

If you want aggregated team data over a specific date range, you can use the `team_data` function. This function allows you to filter by date range, umpire, team, game type, and minimum games called.

### Understanding the team data function parameters

The `team_data` function's parameters are all repeats of those in the other functions, please review those sections for an explanation of each parameter.

#### Example 1: Fetch all team data for a specific date range

```python
import pybaseballstats.umpire_scorecards as us
# 1. Fetch all team data for a specific date range
df = us.team_data(start_date="2023-04-01", end_date="2023-04-30")
print(df)
```

#### Example 2: Fetch team data for a specific umpire and team

```python
import pybaseballstats.umpire_scorecards as us
# 1. Fetch all team data for a specific date range  
df = us.team_data(start_date="2023-04-01", end_date="2023-04-30")
print(df)
```

## Final Notes

1. Please note that some of the restrictions you can enable through the parameters may result in no data being returned. For example, if you try to filter by an umpire name that does not exist in the data for the specified date range, a warning will be printed and all umpires will be returned instead. In other cases, this may not be caught and an empty DataFrame will be returned. Please ensure that your filters are valid for the date range you are querying. I recommend starting with a broader query and then narrowing down your filters as needed.
2. Please refer to the [Umpire Scorecard glossary](https://umpscorecards.com/page/info/glossary) provided by Umpire Scorecards for definitions of the columns in the returned DataFrame. There will be some extra columns that are not in the glossary, as they aren't available publicly on the website rather they are present in the API response. These columns are left in because they do have some value in understanding the data.
3. This package uses the `polars` library for data manipulation. If you wish to convert the returned DataFrame to a pandas DataFrame, you can use the `.to_pandas()` method on the returned DataFrame to convert it.
