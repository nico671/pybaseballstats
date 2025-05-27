# Retrosheet Documentation

## Source

The data is pulled from Retrosheet's online databases:

- Player Data: Retrosheet People files (biographical data)
- Ejections Data: Retrosheet ejections database

## Available Functions

- `player_lookup`: Search for players by name to find their codes and biographical information
- `retrosheet_ejections_data`: Retrieve MLB ejection data with filtering options

## Function Details

### player_lookup()

**Parameters:**

- `first_name` (str, optional): Player's first name (case-insensitive)
- `last_name` (str, optional): Player's last name (case-insensitive)
- `strip_accents` (bool): Remove accents from names for broader matching. Defaults to False
- `return_pandas` (bool): Return pandas DataFrame. Defaults to False (returns polars DataFrame)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Player biographical data

**Raises:**

- `ValueError`: If neither first_name nor last_name is provided

**Key Columns:**

- `key_person`: Unique player identifier
- `name_last`: Last name
- `name_first`: First name
- `key_bbref`: Baseball Reference player code
- `key_retro`: Retrosheet player code
- `name_given`: Full given name
- `debut`: MLB debut date
- `death_year`: Year of death (if applicable)

### retrosheet_ejections_data()

**Parameters:**

- `start_date` (str, optional): Start date in 'MM/DD/YYYY' format
- `end_date` (str, optional): End date in 'MM/DD/YYYY' format
- `ejectee_name` (str, optional): Name of ejected person (partial matches allowed)
- `umpire_name` (str, optional): Name of ejecting umpire (partial matches allowed)
- `inning` (int, optional): Inning of ejection (-1 to 20, where -1 = before game)
- `ejectee_job` (str, optional): Job of ejected person (e.g., "Manager", "Player")
- `return_pandas` (bool): Return pandas DataFrame. Defaults to False (returns polars DataFrame)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Ejection data

**Raises:**

- `ValueError`: If date format is invalid or inning is out of range

**Key Columns:**

- `DATE`: Date of ejection
- `EJECTEENAME`: Name of ejected person
- `UMPIRENAME`: Name of ejecting umpire
- `INNING`: Inning of ejection
- `JOB`: Role of ejected person
- `REASON`: Reason for ejection
- `TEAM`: Team of ejected person

## Usage Examples

### Player Lookup

```python
# Option 1: Direct import
from pybaseballstats.retrosheet import player_lookup

# Search by full name
mike_trout = player_lookup(first_name="Mike", last_name="Trout")
print(mike_trout)

# Search by last name only
smiths = player_lookup(last_name="Smith")

# Search by first name only
mikes = player_lookup(first_name="Mike")

# Option 2: Module import
import pybaseballstats as pyb
players = pyb.retrosheet.player_lookup(first_name="Babe", last_name="Ruth")
```

### Advanced Player Search

```python
# Search with accent handling for international players
# This will match "José" when searching for "Jose"
jose_players = player_lookup(
    first_name="Jose", 
    last_name="Altuve", 
    strip_accents=True
)

# Get results as pandas DataFrame
pandas_results = player_lookup(
    first_name="Derek", 
    last_name="Jeter", 
    return_pandas=True
)

# Find player codes for use in other functions
player_data = player_lookup(first_name="Mike", last_name="Trout")
bbref_code = player_data["key_bbref"][0]  # Use in Baseball Reference functions
print(f"Mike Trout's Baseball Reference code: {bbref_code}")
```

### Ejections Data

```python
from pybaseballstats.retrosheet import retrosheet_ejections_data

# Get all ejections (warning: large dataset)
all_ejections = retrosheet_ejections_data()

# Filter by date range
recent_ejections = retrosheet_ejections_data(
    start_date="01/01/2020",
    end_date="12/31/2023"
)

# Search for specific manager ejections
manager_ejections = retrosheet_ejections_data(
    ejectee_name="Joe Girardi",
    ejectee_job="Manager"
)
```

### Advanced Ejections Analysis

```python
# Late-inning ejections
late_ejections = retrosheet_ejections_data(
    start_date="01/01/2020",
    end_date="12/31/2023",
    inning=9
)

# Ejections by specific umpire
angel_hernandez_ejections = retrosheet_ejections_data(
    umpire_name="Angel Hernandez"
)

# Player ejections in extra innings
extra_inning_ejections = retrosheet_ejections_data(
    ejectee_job="Player",
    inning=10  # Can go up to 20
)

# Pre-game ejections (rare but they happen)
pregame_ejections = retrosheet_ejections_data(inning=-1)
```

### Combining Functions

```python
# Find a player's code, then look up their ejections
player_data = player_lookup(first_name="Bryce", last_name="Harper")
if not player_data.is_empty():
    player_name = f"{player_data['name_first'][0]} {player_data['name_last'][0]}"
    
    # Search for ejections
    player_ejections = retrosheet_ejections_data(
        ejectee_name=player_name,
        ejectee_job="Player"
    )
    
    print(f"Found {len(player_ejections)} ejections for {player_name}")
```

### Working with Different Return Types

```python
# Get data as polars DataFrame (default)
polars_df = player_lookup(last_name="Rodriguez")

# Get data as pandas DataFrame
pandas_df = player_lookup(last_name="Rodriguez", return_pandas=True)

# Filter and analyze with polars
active_players = polars_df.filter(pl.col("debut").is_not_null())

# Filter and analyze with pandas
recent_debuts = pandas_df[pandas_df["debut"] > "2020-01-01"]
```

## Date Format Requirements

For ejections data:

- **Format**: Use 'MM/DD/YYYY' format (e.g., "07/15/2023")
- **Range**: Data available from early 1900s to present
- **Validation**: Function validates date format and will raise ValueError for invalid formats

```python
# Valid date formats
valid_dates = [
    "01/01/2023",
    "12/31/2022", 
    "07/04/2021"
]

# Invalid dates will raise ValueError
try:
    ejections = retrosheet_ejections_data(
        start_date="2023-01-01"  # Wrong format - will fail
    )
except ValueError as e:
    print(f"Error: {e}")
```

## Data Coverage

### Player Data

- **Historical Range**: Complete MLB history from 1871 to present
- **International Players**: Includes players from all countries
- **Biographical Info**: Birth/death dates, debut dates, various player codes

### Ejections Data

- **Historical Range**: Early 1900s to present (exact start date varies)
- **Coverage**: All documented MLB ejections
- **Detail Level**: Includes reason, inning, umpire, and context

## Performance Notes

- `player_lookup`: Downloads player data on each call (1-3 seconds)
- `retrosheet_ejections_data`: Downloads ejection data once per call (2-5 seconds)
- Both functions use direct HTTP requests, making them faster than Selenium-based functions

## Error Handling and Warnings

Functions provide helpful warnings for common scenarios:

```python
# No results found
ejections = retrosheet_ejections_data(
    ejectee_name="Nonexistent Player"
)
# Output: "Warning: No ejections found for the given ejectee name."

# Empty date range
ejections = retrosheet_ejections_data(
    start_date="01/01/2025",
    end_date="12/31/2025"
)
# Output: "Warning: No ejections found for the given date range."
```

## Common Use Cases

### Finding Player Codes

```python
# Get Baseball Reference code for other pybaseballstats functions
player = player_lookup(first_name="Aaron", last_name="Judge")
bbref_code = player["key_bbref"][0]  # Use with bref_single_player functions
```

### Ejection Analysis

```python
# Analyze ejection trends by year
ejections_2020s = retrosheet_ejections_data(start_date="01/01/2020")
yearly_counts = ejections_2020s.group_by(
    pl.col("DATE").dt.year().alias("year")
).count()
```

### Manager vs Player Ejections

```python
manager_ejections = retrosheet_ejections_data(ejectee_job="Manager")
player_ejections = retrosheet_ejections_data(ejectee_job="Player")

print(f"Manager ejections: {len(manager_ejections)}")
print(f"Player ejections: {len(player_ejections)}")
```
