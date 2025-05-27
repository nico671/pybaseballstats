# Baseball Reference Managers Documentation

## Source

The data is pulled from Baseball Reference manager pages:

- Basic Data: [Manager Records](https://www.baseball-reference.com/leagues/majors/2025-managers.shtml)
- Tendencies Data: [Manager Tendencies](https://www.baseball-reference.com/leagues/majors/2025-manager-tendencies.shtml)

Note: There is one page per year, the given links are for the 2025 season.

## Available Functions

- `managers_basic_data`: Returns basic information about all MLB managers for a given year including wins, losses, win percentage, and postseason performance.
- `manager_tendencies_data`: Returns strategic tendencies data for all MLB managers including stealing rates, bunting patterns, and substitution usage.

## Function Details

### managers_basic_data()

**Parameters:**

- `year` (int): The year to retrieve manager data for (must be 1871 or later)
- `return_pandas` (bool, optional): Whether to return a pandas DataFrame. Defaults to False (returns polars DataFrame)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Manager basic statistics

**Raises:**

- `ValueError`: If year is None or less than 1871
- `TypeError`: If year is not an integer

**Columns Returned:**

- `manager`: Manager name
- `team_ID`: Team identifier
- `W`: Wins
- `L`: Losses
- `ties`: Tied games
- `G`: Games managed
- `win_loss_perc`: Win-loss percentage
- `finish`: Team finish position
- `mgr_challenge_count`: Number of challenges made
- `mgr_overturn_count`: Number of successful challenges
- `mgr_replay_success_rate`: Challenge success rate percentage
- `mgr_ejections`: Number of ejections
- `postseason_wins`: Postseason wins
- `postseason_losses`: Postseason losses
- `win_loss_perc_post`: Postseason win-loss percentage

### manager_tendencies_data()

**Parameters:**

- `year` (int): The year to retrieve manager tendencies data for (must be 1871 or later)
- `return_pandas` (bool, optional): Whether to return a pandas DataFrame. Defaults to False (returns polars DataFrame)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Manager tendencies data

**Raises:**

- `ValueError`: If year is None or less than 1871
- `TypeError`: If year is not an integer

**Columns Returned:**

- `manager`: Manager name
- `team_ID`: Team identifier
- `age`: Manager age
- `manager_games`: Games managed
- `steal_2b_chances`: Opportunities for stealing second base
- `steal_2b_attempts`: Actual steal attempts for second base
- `steal_2b_rate`: Rate of stealing second base
- `steal_2b_rate_plus`: Stealing rate compared to league average
- `steal_3b_chances`: Opportunities for stealing third base
- `steal_3b_attempts`: Actual steal attempts for third base
- `steal_3b_rate`: Rate of stealing third base
- `steal_3b_rate_plus`: Stealing rate compared to league average
- `sac_bunt_chances`: Sacrifice bunt opportunities
- `sac_bunts`: Actual sacrifice bunts
- `sac_bunt_rate`: Sacrifice bunt rate
- `sac_bunt_rate_plus`: Sacrifice bunt rate compared to league average
- `ibb_chances`: Intentional walk opportunities
- `ibb`: Intentional walks issued
- `ibb_rate`: Intentional walk rate
- `ibb_rate_plus`: Intentional walk rate compared to league average
- `pinch_hitters`: Pinch hitters used per game
- `pinch_hitters_plus`: Pinch hitter usage compared to league average
- `pinch_runners`: Pinch runners used per game
- `pinch_runners_plus`: Pinch runner usage compared to league average
- `pitchers_used_per_game`: Average pitchers used per game
- `pitchers_used_per_game_plus`: Pitcher usage compared to league average

## Usage

### Managers Basic Data

#### Accessing the Function

```python
# Option 1: Direct import
from pybaseballstats.bref_managers import managers_basic_data
managers_data = managers_basic_data(year)

# Option 2: Module import
import pybaseballstats as pyb   
managers_data = pyb.bref_managers.managers_basic_data(year)
```

#### Examples

```python
# Get basic data for all MLB managers in 2023 (returns polars DataFrame)
managers_data = managers_basic_data(2023)
print(managers_data)

# Get the same data as a pandas DataFrame
managers_pandas = managers_basic_data(2023, return_pandas=True)
print(managers_pandas)

# Filter for specific managers
dodgers_manager = managers_data.filter(pl.col("team_ID") == "LAD")
```

### Manager Tendencies Data

#### Accessing the Function

```python
# Option 1: Direct import
from pybaseballstats.bref_managers import manager_tendencies_data
tendencies_data = manager_tendencies_data(year)

# Option 2: Module import
import pybaseballstats as pyb
tendencies_data = pyb.bref_managers.manager_tendencies_data(year)
```

#### Examples

```python
# Get tendencies data for all MLB managers in 2023 (returns polars DataFrame)
manager_tendencies = manager_tendencies_data(2023)
print(manager_tendencies)

# Get the same data as a pandas DataFrame
tendencies_pandas = manager_tendencies_data(2023, return_pandas=True)
print(tendencies_pandas)

# Analyze stealing tendencies
high_steal_managers = manager_tendencies.filter(pl.col("steal_2b_rate") > 0.75)
```

## Performance Notes

**Important:** Both functions use Selenium WebDriver to scrape data from Baseball Reference, which makes them slower than other functions in the package that use direct HTTP requests. The functions include appropriate wait conditions to ensure data is fully loaded before extraction.

## Error Handling

Both functions include comprehensive validation:

- Year must be provided (not None)
- Year must be an integer
- Year must be 1871 or later (start of professional baseball)

If data retrieval fails, the function will print an error message and return `None`.
