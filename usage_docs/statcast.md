# Statcast Documentation

## Source

The data is pulled from Baseball Savant's Statcast database:

- URL: Baseball Savant CSV exports for date ranges
- Data: Complete pitch-by-pitch Statcast data including advanced metrics

## Available Functions

- `statcast_date_range_pitch_by_pitch`: Retrieve comprehensive Statcast pitch-by-pitch data for a specified date range

## Function Details

### statcast_date_range_pitch_by_pitch()

**Parameters:**

- `start_date` (str): Start date in 'YYYY-MM-DD' format
- `end_date` (str): End date in 'YYYY-MM-DD' format  
- `return_pandas` (bool, optional): Whether to return a pandas DataFrame. Defaults to False (returns polars LazyFrame)

**Returns:**

- `pl.LazyFrame | pd.DataFrame`: Complete Statcast pitch-by-pitch data for the specified date range

**Description:**
Downloads comprehensive Statcast data for all MLB games within the specified date range. This includes every pitch thrown with detailed metrics such as velocity, spin rate, exit velocity, launch angle, and much more.

**Key Data Columns:**

- **Pitch Metrics**: `release_speed`, `release_spin_rate`, `release_extension`
- **Pitch Location**: `plate_x`, `plate_z`, `pfx_x`, `pfx_z`
- **Batted Ball Data**: `launch_speed`, `launch_angle`, `hit_distance_sc`
- **Game Context**: `inning`, `outs_when_up`, `balls`, `strikes`
- **Players**: `pitcher`, `batter`, `pitcher_1`, `fielder_2`, etc.
- **Situational**: `on_3b`, `on_2b`, `on_1b`, `score_diff`, `game_date`
- **Advanced Metrics**: `estimated_ba_using_speedangle`, `estimated_woba_using_speedangle`

## Usage Examples

### Basic Usage

```python
# Option 1: Direct import
from pybaseballstats.statcast import statcast_date_range_pitch_by_pitch

# Get data for a single day (returns polars LazyFrame)
daily_data = statcast_date_range_pitch_by_pitch("2023-07-15", "2023-07-15")

# Collect the lazy frame to get actual data
daily_df = daily_data.collect()

# Option 2: Module import
import pybaseballstats as pyb
data = pyb.statcast.statcast_date_range_pitch_by_pitch("2023-07-15", "2023-07-15")
```

### Working with Different Return Types

```python
# Get data as polars LazyFrame (default - more memory efficient)
lazy_df = statcast_date_range_pitch_by_pitch("2023-08-01", "2023-08-07")

# Get data as pandas DataFrame
pandas_df = statcast_date_range_pitch_by_pitch(
    "2023-08-01", 
    "2023-08-07", 
    return_pandas=True
)

# Work with lazy evaluation for large datasets
filtered_data = lazy_df.filter(
    pl.col("events") == "home_run"
).collect()  # Only collect after filtering
```

### Date Range Queries

```python
# Single game day
single_day = statcast_date_range_pitch_by_pitch("2023-10-01", "2023-10-01")

# One week of data
week_data = statcast_date_range_pitch_by_pitch("2023-07-01", "2023-07-07")

# Full month (warning: large dataset)
month_data = statcast_date_range_pitch_by_pitch("2023-09-01", "2023-09-30")

# Specific series dates
series_data = statcast_date_range_pitch_by_pitch("2023-10-28", "2023-10-30")
```

### Advanced Data Analysis

```python
# Get data and perform analysis
data = statcast_date_range_pitch_by_pitch("2023-08-15", "2023-08-21")

# Filter for home runs with high exit velocity
big_homers = data.filter(
    (pl.col("events") == "home_run") & 
    (pl.col("launch_speed") > 110.0)
).collect()

# Analyze pitch types by velocity
pitch_analysis = data.group_by("pitch_type").agg([
    pl.col("release_speed").mean().alias("avg_velocity"),
    pl.col("release_speed").count().alias("pitch_count")
]).collect()

# Strike zone analysis
strikes = data.filter(
    (pl.col("plate_x").abs() <= 8.5/12) &  # Within strike zone width
    (pl.col("plate_z") >= pl.col("sz_bot")) &
    (pl.col("plate_z") <= pl.col("sz_top"))
).collect()
```

### Team-Specific Analysis

```python
# Analyze specific team's performance
team_data = data.filter(
    pl.col("home_team") == "LAD"  # Dodgers home games
).collect()

# Pitcher analysis for a team
dodgers_pitching = data.filter(
    pl.col("home_team") == "LAD"
).group_by("pitcher").agg([
    pl.col("release_speed").mean().alias("avg_fastball_velo"),
    pl.col("events").filter(pl.col("events") == "strikeout").count().alias("strikeouts")
]).collect()
```

### Performance Optimization with LazyFrames

```python
# Efficient processing of large datasets
large_dataset = statcast_date_range_pitch_by_pitch("2023-04-01", "2023-09-30")

# Chain operations before collecting (more efficient)
analysis = large_dataset.filter(
    pl.col("pitch_type").is_in(["FF", "SI"])  # Fastballs only
).group_by(["pitcher", "pitch_type"]).agg([
    pl.col("release_speed").mean().alias("avg_velocity"),
    pl.col("release_spin_rate").mean().alias("avg_spin_rate")
]).sort("avg_velocity", descending=True)

# Only collect final results
results = analysis.collect()
```

### Combining with Other Data

```python
# Get Statcast data
statcast_data = statcast_date_range_pitch_by_pitch("2023-07-15", "2023-07-15")

# Filter for specific players (use with player lookup from other modules)
mike_trout_abs = statcast_data.filter(
    pl.col("batter") == "Mike Trout"
).collect()

# Analyze against specific pitchers
verlander_pitches = statcast_data.filter(
    pl.col("pitcher") == "Justin Verlander"
).collect()
```

## Date Format Requirements

- **Format**: Use 'YYYY-MM-DD' format (e.g., "2023-07-15")
- **Range**: Statcast data available from 2008 onward (limited data), complete from 2015+
- **Validation**: Function validates date format automatically

```python
# Valid date formats
valid_queries = [
    ("2023-07-15", "2023-07-15"),  # Single day
    ("2023-07-01", "2023-07-31"),  # Full month
    ("2015-04-06", "2015-04-12")   # Season opening week
]

# Invalid formats will raise errors
try:
    data = statcast_date_range_pitch_by_pitch("07/15/2023", "07/16/2023")  # Wrong format
except Exception as e:
    print(f"Error: {e}")
```

## Performance Notes

### Speed and Memory

- Uses **asynchronous processing** for faster data retrieval
- **LazyFrame return type** (default) provides memory efficiency for large datasets
- Typical execution time: 5-30 seconds depending on date range size
- Large date ranges (>1 month) may take several minutes

### Best Practices

```python
# For large datasets, use lazy evaluation
large_data = statcast_date_range_pitch_by_pitch("2023-04-01", "2023-09-30")

# Filter before collecting to save memory
home_runs_only = large_data.filter(pl.col("events") == "home_run").collect()

# For small datasets, pandas may be more familiar
small_data = statcast_date_range_pitch_by_pitch(
    "2023-07-15", "2023-07-15", 
    return_pandas=True
)
```

## Data Coverage

### Historical Range

- **2008-2014**: Limited pitch tracking data (PITCHf/x era)
- **2015+**: Complete Statcast data with batted ball metrics
- **2020+**: Enhanced data quality and additional metrics

### Metrics Available

- **All Years**: Basic pitch data (velocity, location, type)
- **2015+**: Exit velocity, launch angle, hit distance, expected stats
- **2020+**: Additional spin metrics and refined measurements

## Error Handling

Common issues and solutions:

```python
# Handle date range validation
try:
    data = statcast_date_range_pitch_by_pitch("2023-07-15", "2023-07-14")  # End before start
except ValueError as e:
    print(f"Date range error: {e}")

# Handle large data requests
try:
    # Very large range - may timeout or fail
    huge_data = statcast_date_range_pitch_by_pitch("2015-01-01", "2023-12-31")
except Exception as e:
    print(f"Data retrieval error: {e}")
    # Consider breaking into smaller chunks
```

## Integration with Other Functions

This function works well with other pybaseballstats modules:

```python
# Combine with player lookup
from pybaseballstats.retrosheet import player_lookup

# Find player code
player_info = player_lookup("Shohei", "Ohtani")
player_name = f"{player_info['name_first'][0]} {player_info['name_last'][0]}"

# Get their Statcast data
ohtani_data = statcast_date_range_pitch_by_pitch("2023-04-01", "2023-09-30").filter(
    pl.col("pitcher") == player_name
).collect()
```

## Memory Management

For very large datasets:

```python
# Process data in chunks for memory efficiency
import datetime

start = datetime.date(2023, 4, 1)
end = datetime.date(2023, 9, 30)
chunk_size = 7  # One week at a time

all_home_runs = []
current = start

while current <= end:
    chunk_end = min(current + datetime.timedelta(days=chunk_size), end)
    
    chunk_data = statcast_date_range_pitch_by_pitch(
        current.strftime("%Y-%m-%d"),
        chunk_end.strftime("%Y-%m-%d")
    ).filter(pl.col("events") == "home_run").collect()
    
    all_home_runs.append(chunk_data)
    current = chunk_end + datetime.timedelta(days=1)

# Combine all chunks
season_home_runs = pl.concat(all_home_runs)
```
