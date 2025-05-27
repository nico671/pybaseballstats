# Fangraphs Documentation

## Source

The data is pulled from Fangraphs API endpoints:

- Batting: Fangraphs batting leaderboards API
- Pitching: Fangraphs pitching leaderboards API  
- Fielding: Fangraphs fielding leaderboards API

## Available Functions

The `fangraphs` module provides comprehensive MLB statistics across multiple categories:

- `fangraphs_batting_range`: Batting statistics for players/teams over specified date or season ranges
- `fangraphs_pitching_range`: Pitching statistics for players/teams over specified date or season ranges
- `fangraphs_fielding_range`: Fielding statistics for players/teams over specified season ranges

## Function Details

### fangraphs_batting_range()

**Parameters:**

- `start_date` (str | None): Start date in 'YYYY-MM-DD' format (for date range queries)
- `end_date` (str | None): End date in 'YYYY-MM-DD' format (for date range queries)
- `start_year` (int | None): Starting season year (for season range queries)
- `end_year` (int | None): Ending season year (for season range queries)
- `min_pa` (str | int): Minimum plate appearances (default: "y" for qualified)
- `stat_types` (List[FangraphsBattingStatType]): List of statistics to include
- `fielding_position` (FangraphsBattingPosTypes): Position filter (default: ALL)
- `active_roster_only` (bool): Include only active roster players (default: False)
- `team` (FangraphsTeams): Team filter (default: ALL)
- `league` (Literal["nl", "al", ""]): League filter (default: "")
- `min_age` (int | None): Minimum player age
- `max_age` (int | None): Maximum player age
- `batting_hand` (Literal["R", "L", "S", ""]): Batting handedness filter (default: "")
- `split_seasons` (bool): Split results by season (default: False)
- `return_pandas` (bool): Return pandas DataFrame (default: False)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Batting statistics

### fangraphs_pitching_range()

**Parameters:**

- `start_date` (str | None): Start date in 'YYYY-MM-DD' format
- `end_date` (str | None): End date in 'YYYY-MM-DD' format
- `start_year` (int | None): Starting season year
- `end_year` (int | None): Ending season year
- `min_ip` (str | int): Minimum innings pitched (default: "y" for qualified)
- `stat_types` (List[FangraphsPitchingStatType]): List of statistics to include
- `active_roster_only` (bool): Include only active roster players (default: False)
- `team` (FangraphsTeams): Team filter (default: ALL)
- `league` (Literal["nl", "al", ""]): League filter (default: "")
- `min_age` (int | None): Minimum player age
- `max_age` (int | None): Maximum player age
- `pitching_hand` (Literal["R", "L", "S", ""]): Pitching handedness filter (default: "")
- `starter_reliever` (Literal["sta", "rel", "pit"]): Role filter (default: "pit" for all)
- `split_seasons` (bool): Split results by season (default: False)
- `return_pandas` (bool): Return pandas DataFrame (default: False)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Pitching statistics

### fangraphs_fielding_range()

**Parameters:**

- `start_year` (int | None): Starting season year
- `end_year` (int | None): Ending season year
- `min_inn` (str | int): Minimum innings played (default: "y" for qualified)
- `stat_types` (List[FangraphsFieldingStatType]): List of statistics to include
- `active_roster_only` (bool): Include only active roster players (default: False)
- `team` (FangraphsTeams): Team filter (default: ALL)
- `league` (Literal["nl", "al", ""]): League filter (default: "")
- `fielding_position` (FangraphsBattingPosTypes): Position filter (default: ALL)
- `return_pandas` (bool): Return pandas DataFrame (default: False)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Fielding statistics

## Enum Options

### Teams

Use `FangraphsTeams` enum for team filtering:

```python
from pybaseballstats.utils.fangraphs_utils import FangraphsTeams
# Options include: ALL, LAA, HOU, OAK, TOR, ATL, MIL, STL, CHC, etc.
```

### Positions  

Use `FangraphsBattingPosTypes` enum for position filtering:

```python
from pybaseballstats.utils.fangraphs_utils import FangraphsBattingPosTypes
# Options include: ALL, C, 1B, 2B, 3B, SS, LF, CF, RF, OF, DH
```

### Stat Types

Use appropriate stat type enums:

```python
from pybaseballstats.utils.fangraphs_utils import (
    FangraphsBattingStatType,
    FangraphsPitchingStatType
)
from pybaseballstats.utils.fangraphs_consts import FangraphsFieldingStatType
```

## Usage Examples

### Basic Usage

```python
# Option 1: Direct import
from pybaseballstats.fangraphs import fangraphs_batting_range
from pybaseballstats.utils.fangraphs_utils import FangraphsBattingStatType

# Get qualified batting stats for 2023
batting_stats = fangraphs_batting_range(
    start_year=2023,
    end_year=2023,
    stat_types=[FangraphsBattingStatType.AVG, FangraphsBattingStatType.HR, FangraphsBattingStatType.WAR]
)

# Option 2: Module import  
import pybaseballstats as pyb
batting_stats = pyb.fangraphs.fangraphs_batting_range(start_year=2023, end_year=2023)
```

### Season Range Queries

```python
from pybaseballstats.fangraphs import fangraphs_pitching_range
from pybaseballstats.utils.fangraphs_utils import FangraphsPitchingStatType

# Get pitching stats for multiple seasons
pitching_stats = fangraphs_pitching_range(
    start_year=2020,
    end_year=2023,
    min_ip=50,
    stat_types=[FangraphsPitchingStatType.ERA, FangraphsPitchingStatType.FIP, FangraphsPitchingStatType.WAR],
    split_seasons=True  # Get separate rows for each season
)
```

### Date Range Queries

```python
# Get batting stats for specific date range
summer_stats = fangraphs_batting_range(
    start_date="2023-06-01",
    end_date="2023-08-31",
    min_pa=100
)
```

### Team and Position Filtering

```python
from pybaseballstats.utils.fangraphs_utils import FangraphsTeams, FangraphsBattingPosTypes

# Get Yankees catchers only
yankees_catchers = fangraphs_batting_range(
    start_year=2023,
    end_year=2023,
    team=FangraphsTeams.NYY,
    fielding_position=FangraphsBattingPosTypes.C
)

# Get National League pitchers
nl_pitchers = fangraphs_pitching_range(
    start_year=2023,
    end_year=2023,
    league="nl",
    starter_reliever="sta"  # Starters only
)
```

### Age and Handedness Filtering

```python
# Get young left-handed hitters
young_lefties = fangraphs_batting_range(
    start_year=2023,
    end_year=2023,
    min_age=20,
    max_age=25,
    batting_hand="L",
    min_pa=200
)
```

### Advanced Fielding Analysis

```python
from pybaseballstats.fangraphs import fangraphs_fielding_range
from pybaseballstats.utils.fangraphs_consts import FangraphsFieldingStatType

# Get shortstop fielding metrics
ss_fielding = fangraphs_fielding_range(
    start_year=2023,
    end_year=2023,
    fielding_position=FangraphsBattingPosTypes.SS,
    stat_types=[FangraphsFieldingStatType.UZR, FangraphsFieldingStatType.DRS],
    min_inn=500
)
```

### Working with Different Return Types

```python
# Get data as polars DataFrame (default)
polars_df = fangraphs_batting_range(start_year=2023, end_year=2023)

# Get data as pandas DataFrame
pandas_df = fangraphs_batting_range(start_year=2023, end_year=2023, return_pandas=True)

# Filter and analyze with polars
top_performers = polars_df.filter(pl.col("WAR") > 5.0).sort("WAR", descending=True)
```

### Multi-Season Analysis

```python
# Compare player performance across multiple seasons
multi_season = fangraphs_batting_range(
    start_year=2020,
    end_year=2023,
    split_seasons=True,
    min_pa=400
)

# Analyze year-over-year changes
player_trends = multi_season.group_by("fg_player_id").agg([
    pl.col("WAR").mean().alias("avg_war"),
    pl.col("Season").count().alias("seasons_played")
])
```

## Performance Notes

These functions use direct HTTP requests to Fangraphs APIs, making them faster than Selenium-based functions. Typical execution time is 1-5 seconds depending on query complexity and data size.

## Data Coverage

- **Historical Range**: Varies by statistic, generally 2002+ for advanced metrics
- **Real-time Updates**: Data is updated regularly during the season
- **Stat Categories**: Comprehensive coverage including traditional and advanced sabermetrics

## Error Handling

Functions will handle common issues gracefully:

- Invalid date ranges will be validated by utility functions
- Missing or invalid enum values will use defaults
- API errors will raise appropriate exceptions

Always verify that stat_types enums are properly imported and used for best results.
