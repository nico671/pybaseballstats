# Umpire Scorecard Documentation

## Source

The data is pulled from Umpire Scorecard's API endpoints:

- Individual Games: Umpire performance data for specific games
- Umpire Statistics: Aggregated umpire performance metrics
- Team Statistics: Team-specific umpire interaction data

## Available Functions

- `umpire_scorecard_games_date_range`: Individual game umpire performance data for a date range
- `umpire_scorecard_umpires_date_range`: Aggregated umpire statistics for a date range
- `umpire_scorecard_teams_date_range`: Team-specific umpire data for a date range

## Function Details

### umpire_scorecard_games_date_range()

**Parameters:**

- `start_date` (str): Start date in any parseable format (recommended: 'YYYY-MM-DD')
- `end_date` (str): End date in any parseable format (recommended: 'YYYY-MM-DD')
- `game_type` (Literal["*", "R", "A", "P", "F", "D", "L", "W"]): Game type filter (default: "*" for all)
- `focus_team` (UmpireScorecardTeams): Team to focus analysis on (default: ALL)
- `focus_team_home_away` (Literal["h", "a", "*"]): Home/away filter for focus team (default: "*")
- `opponent_team` (UmpireScorecardTeams): Opponent team filter (default: ALL)
- `umpire_name` (str): Filter by umpire name (partial matches allowed, default: "")
- `return_pandas` (bool): Return pandas DataFrame (default: False)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Individual game umpire performance data

**Game Type Options:**

- "*": All games
- "R": Regular season
- "A": All-Star Game
- "P": Playoffs
- "F": Wild Card
- "D": Division Series
- "L": League Championship
- "W": World Series

### umpire_scorecard_umpires_date_range()

**Parameters:**

- `start_date` (str): Start date
- `end_date` (str): End date
- `game_type` (Literal): Game type filter (default: "*")
- `focus_team` (UmpireScorecardTeams): Team focus (default: ALL)
- `focus_team_home_away` (Literal["h", "a", "*"]): Home/away filter (default: "*")
- `opponent_team` (UmpireScorecardTeams): Opponent filter (default: ALL)
- `umpire_name` (str): Umpire name filter (default: "")
- `min_games_called` (int): Minimum games called threshold (default: 0)
- `return_pandas` (bool): Return format (default: False)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Aggregated umpire performance statistics

### umpire_scorecard_teams_date_range()

**Parameters:**

- `start_date` (str): Start date
- `end_date` (str): End date
- `game_type` (Literal): Game type filter (default: "*")
- `focus_team` (UmpireScorecardTeams): Team to focus on (default: ALL)
- `return_pandas` (bool): Return format (default: False)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Team-specific umpire interaction data

## Team Options

Use the `UmpireScorecardTeams` enum for team filtering:

```python
from pybaseballstats.umpire_scorecard import UmpireScorecardTeams

# View all available teams
print(UmpireScorecardTeams.show_options())
```

**Available Teams:**

- ALL, DIAMONDBACKS, ATHLETICS, BRAVES, ORIOLES, RED_SOX, CUBS, REDS
- WHITE_SOX, GAURDIANS, ROCKIES, ASTROS, ROYALS, ANGELS, DODGERS, MARLINS
- BREWERS, TWINS, METS, YANKEES, PHILLIES, PIRATES, PADRES, MARINERS
- GIANTS, CARDINALS, RAYS, RANGERS, BLUE_JAYS, NATIONALS

## Usage Examples

### Basic Usage

```python
# Option 1: Direct import
from pybaseballstats.umpire_scorecard import (
    umpire_scorecard_games_date_range,
    UmpireScorecardTeams
)

# Get all games for a date range
games_data = umpire_scorecard_games_date_range(
    start_date="2023-07-01",
    end_date="2023-07-31"
)

# Option 2: Module import
import pybaseballstats as pyb
games_data = pyb.umpire_scorecard.umpire_scorecard_games_date_range(
    start_date="2023-07-01",
    end_date="2023-07-31"
)
```

### Team-Specific Analysis

```python
from pybaseballstats.umpire_scorecard import (
    umpire_scorecard_games_date_range,
    UmpireScorecardTeams
)

# Yankees home games only
yankees_home = umpire_scorecard_games_date_range(
    start_date="2023-04-01",
    end_date="2023-09-30",
    focus_team=UmpireScorecardTeams.YANKEES,
    focus_team_home_away="h"
)

# Red Sox vs Yankees matchups
rivalry_games = umpire_scorecard_games_date_range(
    start_date="2023-04-01", 
    end_date="2023-09-30",
    focus_team=UmpireScorecardTeams.RED_SOX,
    opponent_team=UmpireScorecardTeams.YANKEES
)
```

### Umpire Performance Analysis

```python
from pybaseballstats.umpire_scorecard import umpire_scorecard_umpires_date_range

# Get umpire statistics for the season
umpire_stats = umpire_scorecard_umpires_date_range(
    start_date="2023-04-01",
    end_date="2023-09-30",
    min_games_called=10  # Only umpires with 10+ games
)

# Specific umpire analysis
angel_hernandez = umpire_scorecard_umpires_date_range(
    start_date="2023-04-01",
    end_date="2023-09-30",
    umpire_name="Angel Hernandez"
)
```

### Playoff Analysis

```python
# Playoff games only
playoff_games = umpire_scorecard_games_date_range(
    start_date="2023-10-01",
    end_date="2023-11-01",
    game_type="P"
)

# World Series games
world_series = umpire_scorecard_games_date_range(
    start_date="2023-10-01",
    end_date="2023-11-01", 
    game_type="W"
)
```

### Team Impact Analysis

```python
from pybaseballstats.umpire_scorecard import umpire_scorecard_teams_date_range

# Team performance with different umpires
team_stats = umpire_scorecard_teams_date_range(
    start_date="2023-04-01",
    end_date="2023-09-30"
)

# Focus on specific team
dodgers_impact = umpire_scorecard_teams_date_range(
    start_date="2023-04-01",
    end_date="2023-09-30",
    focus_team=UmpireScorecardTeams.DODGERS
)
```

### Working with Different Return Types

```python
# Get data as polars DataFrame (default)
polars_df = umpire_scorecard_games_date_range(
    start_date="2023-08-01",
    end_date="2023-08-31"
)

# Get data as pandas DataFrame
pandas_df = umpire_scorecard_games_date_range(
    start_date="2023-08-01",
    end_date="2023-08-31",
    return_pandas=True
)

# Filter and analyze
high_impact_games = polars_df.filter(pl.col("favor_home") > 0.5)
```

### Multi-Function Analysis

```python
# Compare individual games to umpire aggregates
games = umpire_scorecard_games_date_range(
    start_date="2023-07-01",
    end_date="2023-07-31"
)

umpires = umpire_scorecard_umpires_date_range(
    start_date="2023-07-01", 
    end_date="2023-07-31",
    min_games_called=5
)

teams = umpire_scorecard_teams_date_range(
    start_date="2023-07-01",
    end_date="2023-07-31"
)

# Analyze patterns across all three datasets
```

## Date Format Requirements

- **Flexibility**: Uses `dateparser` library for flexible date parsing
- **Recommended**: 'YYYY-MM-DD' format (e.g., "2023-07-15")
- **Range**: Data available from 2015 onward
- **Validation**: Automatic validation ensures start_date < end_date

```python
# All these formats work
valid_dates = [
    "2023-07-15",
    "July 15, 2023", 
    "15/07/2023",
    "2023-07-15"
]

# Invalid scenarios
try:
    data = umpire_scorecard_games_date_range(
        start_date="2023-07-15",
        end_date="2023-07-01"  # End before start - will fail
    )
except ValueError as e:
    print(f"Error: {e}")
```

## Performance Notes

- Uses direct HTTP requests to Umpire Scorecard APIs
- Typical execution time: 2-5 seconds per function call
- Larger date ranges may take longer to process
- Real-time data updates during active seasons

## Data Coverage

### Historical Range

- **Available**: 2015 to present
- **Complete Coverage**: All MLB games with umpire performance metrics
- **Game Types**: Regular season, playoffs, All-Star games

### Metrics Available

- Umpire accuracy percentages
- Team favor measurements
- Strike zone consistency
- Game impact scores

## Error Handling

Functions include comprehensive validation:

```python
# Common error scenarios
try:
    # Date too early
    data = umpire_scorecard_games_date_range("2010-01-01", "2010-01-31")
except ValueError as e:
    print("Dates must be 2015 or later")

try:
    # Same team as focus and opponent
    data = umpire_scorecard_games_date_range(
        start_date="2023-07-01",
        end_date="2023-07-31",
        focus_team=UmpireScorecardTeams.YANKEES,
        opponent_team=UmpireScorecardTeams.YANKEES
    )
except ValueError as e:
    print("Focus team and opponent cannot be the same")
```

## Integration with Other Functions

These functions complement other pybaseballstats modules:

```python
# Combine with Statcast data for comprehensive game analysis
from pybaseballstats.statcast_single_game import get_available_game_pks_for_date

# Get games for a date
games = get_available_game_pks_for_date("2023-07-15")

# Get umpire data for the same date
umpire_data = umpire_scorecard_games_date_range(
    start_date="2023-07-15",
    end_date="2023-07-15"
)

# Analyze umpire impact on game outcomes
```
