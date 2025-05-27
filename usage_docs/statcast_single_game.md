# Statcast Single Game Documentation

## Source

The data is pulled from Baseball Savant's Statcast single game pages:

- Pitch-by-pitch data: Baseball Savant game CSV exports
- Exit velocity, pitch velocity, and win probability: Baseball Savant game detail pages

## Available Functions

- `statcast_single_game_pitch_by_pitch`: Complete pitch-by-pitch Statcast data for a single game
- `get_available_game_pks_for_date`: Find game_pk identifiers for games on a specific date
- `get_statcast_single_game_exit_velocity`: Exit velocity and batted ball data for a game
- `get_statcast_single_game_pitch_velocity`: Pitch velocity and movement data for a game
- `get_statcast_single_game_wp_table`: Win probability data for key moments in a game

## Function Details

### statcast_single_game_pitch_by_pitch()

**Parameters:**

- `game_pk` (int): MLB game identifier (unique for each game)
- `return_pandas` (bool, optional): Whether to return a pandas DataFrame. Defaults to False (returns polars DataFrame)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Complete pitch-by-pitch Statcast data

**Description:**
Downloads the complete Statcast dataset for a single game, including all pitch data, batted ball events, and advanced metrics.

### get_available_game_pks_for_date()

**Parameters:**

- `game_date` (str): Date in 'YYYY-MM-DD' format

**Returns:**

- `dict`: Dictionary mapping game_pk to team information

**Description:**
Finds all games played on a specific date and returns their game_pk identifiers along with home/away team information.

### get_statcast_single_game_exit_velocity()

**Parameters:**

- `game_pk` (int): MLB game identifier
- `game_date` (str): Date in 'YYYY-MM-DD' format
- `return_pandas` (bool, optional): Whether to return a pandas DataFrame. Defaults to False (returns polars DataFrame)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Exit velocity and batted ball metrics

**Key Columns:**

- `batter_name`: Player who made contact
- `exit_velo`: Exit velocity in MPH
- `launch_angle`: Launch angle in degrees
- `hit_distance`: Hit distance in feet
- `bat_speed`: Bat speed in MPH
- `xBA`: Expected batting average
- `hr_in_how_many_parks`: Number of parks where hit would be a home run

**Note:** Uses Selenium for web scraping and may be slower than other functions.

### get_statcast_single_game_pitch_velocity()

**Parameters:**

- `game_pk` (int): MLB game identifier
- `game_date` (str): Date in 'YYYY-MM-DD' format
- `return_pandas` (bool, optional): Whether to return a pandas DataFrame. Defaults to False (returns polars DataFrame)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Pitch velocity and movement data

**Key Columns:**

- `pitcher_name`: Pitcher who threw the pitch
- `batter_name`: Batter who faced the pitch
- `pitch_type`: Type of pitch thrown
- `pitch_velocity_mph`: Velocity in MPH
- `spin_rate_rpm`: Spin rate in RPM
- `induced_vertical_break`: Induced vertical break
- `horizontal_break`: Horizontal break

**Note:** Uses Selenium for web scraping and may be slower than other functions.

### get_statcast_single_game_wp_table()

**Parameters:**

- `game_pk` (int): MLB game identifier
- `game_date` (str): Date in 'YYYY-MM-DD' format
- `return_pandas` (bool, optional): Whether to return a pandas DataFrame. Defaults to False (returns polars DataFrame)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Win probability data for key moments

**Key Columns:**

- `batter_name`: Player at bat
- `pitcher_name`: Pitcher facing the batter
- `win_probability_diff`: Change in win probability
- `Home WP%`: Home team win probability
- `Away WP%`: Away team win probability

**Note:** Uses Selenium for web scraping and may be slower than other functions.

## Usage Examples

### Finding Games for a Date

```python
# Option 1: Direct import
from pybaseballstats.statcast_single_game import get_available_game_pks_for_date

# Find all games on a specific date
games = get_available_game_pks_for_date("2023-07-15")
print(games)
# Output: {663469: {'home_team': 'NYY', 'away_team': 'LAA'}, ...}

# Option 2: Module import
import pybaseballstats as pyb
games = pyb.statcast_single_game.get_available_game_pks_for_date("2023-07-15")
```

### Complete Game Analysis

```python
from pybaseballstats.statcast_single_game import (
    get_available_game_pks_for_date,
    statcast_single_game_pitch_by_pitch,
    get_statcast_single_game_exit_velocity,
    get_statcast_single_game_pitch_velocity,
    get_statcast_single_game_wp_table
)

# Find games for a date
game_date = "2023-10-01"
games = get_available_game_pks_for_date(game_date)

# Select a specific game
game_pk = list(games.keys())[0]  # First game of the day

# Get comprehensive game data
pitch_data = statcast_single_game_pitch_by_pitch(game_pk)
exit_velo_data = get_statcast_single_game_exit_velocity(game_pk, game_date)
pitch_velo_data = get_statcast_single_game_pitch_velocity(game_pk, game_date)
win_prob_data = get_statcast_single_game_wp_table(game_pk, game_date)
```

### Working with Different Return Types

```python
# Get data as polars DataFrame (default)
polars_df = statcast_single_game_pitch_by_pitch(663469)

# Get data as pandas DataFrame
pandas_df = statcast_single_game_pitch_by_pitch(663469, return_pandas=True)

# Filter and analyze with polars
home_runs = polars_df.filter(pl.col("events") == "home_run")
```

### Analyzing Specific Game Aspects

```python
# Analyze exit velocity data
exit_velo = get_statcast_single_game_exit_velocity(663469, "2023-07-15")

# Find hardest hit balls
hardest_hits = exit_velo.filter(pl.col("exit_velo") > 100.0)

# Analyze pitch velocity data
pitch_velo = get_statcast_single_game_pitch_velocity(663469, "2023-07-15")

# Find fastest pitches
fastest_pitches = pitch_velo.sort("pitch_velocity_mph", descending=True).head(10)

# Analyze win probability swings
win_prob = get_statcast_single_game_wp_table(663469, "2023-07-15")

# Find biggest momentum shifts
big_swings = win_prob.filter(pl.col("win_probability_diff").abs() > 0.15)
```

### Multiple Games Analysis

```python
# Analyze multiple games from a date
game_date = "2023-09-15"
games = get_available_game_pks_for_date(game_date)

all_exit_velo = []
for game_pk in games.keys():
    try:
        exit_data = get_statcast_single_game_exit_velocity(game_pk, game_date)
        exit_data = exit_data.with_columns(pl.lit(game_pk).alias("game_pk"))
        all_exit_velo.append(exit_data)
    except Exception as e:
        print(f"Could not get data for game {game_pk}: {e}")

# Combine all games
if all_exit_velo:
    combined_data = pl.concat(all_exit_velo)
    
    # Analyze league-wide exit velocity for the day
    avg_exit_velo = combined_data.select(pl.col("exit_velo").mean())
```

### Filtering Game Data

```python
# Get complete pitch data
game_data = statcast_single_game_pitch_by_pitch(663469)

# Filter for specific situations
bases_loaded = game_data.filter(
    (pl.col("on_1b").is_not_null()) & 
    (pl.col("on_2b").is_not_null()) & 
    (pl.col("on_3b").is_not_null())
)

# Two-strike counts
two_strikes = game_data.filter(pl.col("strikes") == 2)

# Home runs
home_runs = game_data.filter(pl.col("events") == "home_run")
```

## Date and Game PK Requirements

### Date Format

- **Format**: Use 'YYYY-MM-DD' format (e.g., "2023-07-15")
- **Range**: Statcast data available from 2008 onward (full data from 2015+)
- **Validation**: Functions validate date format automatically

### Game PK

- **Source**: Use `get_available_game_pks_for_date()` to find valid game_pk values
- **Format**: Integer unique identifier for each MLB game
- **Persistence**: Game PKs remain consistent across all MLB data sources

```python
# Valid workflow
games = get_available_game_pks_for_date("2023-07-15")
for game_pk, teams in games.items():
    print(f"Game {game_pk}: {teams['away_team']} @ {teams['home_team']}")
    
    # Use game_pk for detailed analysis
    pitch_data = statcast_single_game_pitch_by_pitch(game_pk)
```

## Performance Notes

### Speed Comparison

- `statcast_single_game_pitch_by_pitch`: Fast (1-3 seconds) - direct CSV download
- `get_available_game_pks_for_date`: Moderate (3-5 seconds) - API call processing
- Selenium functions: Slower (10-30 seconds each) - web scraping with browser automation

### Memory Usage

- Complete game datasets can be large (2000+ rows for pitch data)
- Consider filtering data for specific analysis needs
- Use polars DataFrames for better memory efficiency with large datasets

## Data Coverage

### Historical Range

- **Pitch-by-pitch**: 2008+ (limited data), 2015+ (complete)
- **Exit velocity**: 2015+ (Statcast era)
- **Pitch movement**: 2008+ (PITCHf/x era)
- **Win probability**: All available games

### Data Quality

- Most complete data available from 2015 onward
- Some advanced metrics only available for recent seasons
- Weather delays or technical issues may affect data availability

## Error Handling

Common issues and solutions:

```python
# Handle missing games
games = get_available_game_pks_for_date("2023-12-25")  # No games on Christmas
if not games:
    print("No games found for this date")

# Handle data retrieval errors
try:
    game_data = statcast_single_game_pitch_by_pitch(999999)  # Invalid game_pk
except Exception as e:
    print(f"Error retrieving game data: {e}")

# Validate game existence before detailed analysis
games = get_available_game_pks_for_date("2023-07-15")
if games:
    game_pk = list(games.keys())[0]
    exit_data = get_statcast_single_game_exit_velocity(game_pk, "2023-07-15")
```

## Integration with Other Functions

These functions work well with other pybaseballstats modules:

```python
# Combine with team analysis
from pybaseballstats.fangraphs import fangraphs_batting_range

# Get team season stats
team_stats = fangraphs_batting_range(start_year=2023, end_year=2023)

# Compare to single game performance
game_data = statcast_single_game_pitch_by_pitch(663469)
team_game_performance = game_data.filter(pl.col("home_team") == "NYY")
```
