# Umpire Scorecard Documentation

This module provides functions to retrieve data from the [Umpire Scorecards](https://umpscorecards.com/) website. This site offers detailed statistics and performance metrics for MLB umpires.

The source has data that starts in 2008. These package functions accept dates
from 2015 onward.

## Available Functions

- `game_data(...)`: Fetches umpire performance data on a game by game basis over a specific date range and set of filters.
- `umpire_data(...)`: Fetches umpire data for a specific date range and set of filters.
- `team_data(...)`: Fetches team data for a specific date range and set of filters.
- `player_data(...)`: Fetches player-level framing data for catchers (`C`), pitchers (`P`), or batters (`B`) over a specific date range and set of filters.

## Function Parameters

Parameter details are organized by function in the sections below.

## Example Usage

### Seeing Available Teams

`UmpireScorecardTeams.show_options()` returns a string of available team options. Use `print()` to display it. It does not fetch source data.

```python
import pybaseballstats.umpire_scorecards as us
from pybaseballstats.enums import UmpireScorecardTeams
print(UmpireScorecardTeams.show_options()) # will print all of the available teams
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
GUARDIANS: CLE
TIGERS: DET
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

`game_type` filters `game_data`, `umpire_data`, `team_data`, and `player_data`.
Use `"*"` for all games, `"R"` for regular season, `"A"` for the All-Star Game,
`"P"` for all postseason games, `"F"` for Wild Card, `"D"` for Division Series,
`"L"` for League Championship Series, or `"W"` for World Series.

### Fetching Game By Game Umpire Data

If you want umpire performance data on a game by game basis, you can use the `game_data` function. This function allows you to filter by date range, umpire, team, and game type.

#### Understanding the game by game data function parameters

Note that only the `start_date` and `end_date` parameters are required. The other parameters have default values that will return all data if not specified.

- `start_date` (str): The start date for the data in "YYYY-MM-DD" format.
- `end_date` (str): The end date for the data in "YYYY-MM-DD" format.
- `umpire_name` (str): The umpire's name to filter by. Use "" to include all umpires.
- `focus_team` (UmpireScorecardTeams): Team filter. Use `UmpireScorecardTeams.ALL` to include all teams. See "Seeing Available Teams" for the enum options.
- `focus_team_home_away` (str): Filter by whether the focus team is home or away. Use "*" to include both. Options are "h" for home, "a" for away, and "*" for both.
- `opponent_team` (UmpireScorecardTeams): Opponent team filter. Use `UmpireScorecardTeams.ALL` to include all opponents. See "Seeing Available Teams" for the enum options.
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
from pybaseballstats.enums import UmpireScorecardTeams
# 2. Fetch game data for a specific umpire and team
df = us.game_data(start_date="2023-04-01", end_date="2025-09-09", umpire_name="Brian O'Nora", focus_team=UmpireScorecardTeams.MARLINS)
print(df)
```

#### Example 3: Fetch game data for a specific team when they are playing at home against a specific opponent

```python
import pybaseballstats.umpire_scorecards as us
from pybaseballstats.enums import UmpireScorecardTeams
# 3. Fetch game data for a specific team when they are playing at home against a specific opponent
df = us.game_data(
    start_date="2023-04-01",
    end_date="2025-04-30",
    focus_team=UmpireScorecardTeams.DIAMONDBACKS,
    focus_team_home_away="h",
    opponent_team=UmpireScorecardTeams.CUBS
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
from pybaseballstats.enums import UmpireScorecardTeams
# 2. Fetch umpire data for a specific team with a minimum number of games called
df = us.umpire_data(
    start_date="2023-04-01",
    end_date="2025-09-09",
    focus_team=UmpireScorecardTeams.MARLINS,
    min_games_called=10,
)
print(df)
```

## Fetching Team Data

`team_data` returns aggregated team data for a date range. It supports game-type and team filters. It does not accept an umpire filter or a minimum-games filter.

### Understanding the team data function parameters

`team_data(start_date, end_date, game_type="*", focus_team=UmpireScorecardTeams.ALL)`

- `start_date` (str, required): Inclusive start date in `YYYY-MM-DD` format.
- `end_date` (str, required): Inclusive end date in `YYYY-MM-DD` format.
- `game_type` (str): One of `"*"`, `"R"`, `"A"`, `"P"`, `"F"`, `"D"`, `"L"`, or `"W"`. Defaults to `"*"` for all game types.
- `focus_team` (UmpireScorecardTeams): Team filter. Defaults to `UmpireScorecardTeams.ALL`. The function applies this filter to the returned team rows.

#### Example 1: Fetch all team data for a specific date range

```python
import pybaseballstats.umpire_scorecards as us
# 1. Fetch all team data for a specific date range
df = us.team_data(start_date="2023-04-01", end_date="2023-04-30")
print(df)
```

#### Example 2: Fetch regular-season team data for the Marlins

```python
import pybaseballstats.umpire_scorecards as us
from pybaseballstats.enums import UmpireScorecardTeams
df = us.team_data(
    start_date="2023-04-01",
    end_date="2023-04-30",
    game_type="R",
    focus_team=UmpireScorecardTeams.MARLINS,
)
print(df)
```

## Fetching Player Data

If you want player-level umpire scorecard data, you can use the `player_data` function. This function allows you to filter by date range, player type, game type, and team.

### Understanding the player data function parameters

Only `start_date`, `end_date`, and `player_type` are required. The other parameters have defaults that return broader data when not specified.

- `start_date` (str): The start date for the data in `YYYY-MM-DD` format.
- `end_date` (str): The end date for the data in `YYYY-MM-DD` format.
- `player_type` (str): The type of player data to return. Options are:
  - `"C"` for catchers
  - `"P"` for pitchers
  - `"B"` for batters
- `game_type` (str): The game type filter. Defaults to `"*"` (all game types). See the game type options section above.
- `team` (UmpireScorecardTeams): Team filter. Defaults to `UmpireScorecardTeams.ALL`.

#### Example 1: Fetch all regular season pitcher player data for a date range

```python
import pybaseballstats.umpire_scorecards as us

df = us.player_data(
    start_date="2025-01-01",
    end_date="2025-10-01",
    player_type="P",
    game_type="R",
)
print(df)
```

#### Example 2: Fetch catcher data for a specific team

```python
import pybaseballstats.umpire_scorecards as us
from pybaseballstats.enums import UmpireScorecardTeams

df = us.player_data(
    start_date="2025-01-01",
    end_date="2025-10-01",
    player_type="C",
    game_type="R",
    team=UmpireScorecardTeams.ANGELS,
)
print(df)
```

#### Example 3: Fetch batter data across all game types

```python
import pybaseballstats.umpire_scorecards as us

df = us.player_data(
    start_date="2025-01-01",
    end_date="2025-10-01",
    player_type="B",
)
print(df)
```

## Notes

1. A valid request with no matching umpire returns an empty DataFrame. The name filter uses exact equality. A failed request or invalid source response raises `RuntimeError`.
2. Please refer to the [Umpire Scorecard glossary](https://umpscorecards.com/page/info/glossary) provided by Umpire Scorecards for definitions of the columns in the returned DataFrame. There will be some extra columns that are not in the glossary, as they aren't available publicly on the website rather they are present in the API response. These columns are left in because they do have some value in understanding the data.
3. Team filters should use the `UmpireScorecardTeams` enum (view options via `UmpireScorecardTeams.show_options()`).
