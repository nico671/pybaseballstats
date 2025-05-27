# Baseball Reference Single Player Documentation

## Source

The data is pulled from individual player pages on Baseball Reference:

- Standard/Value/Advanced Stats: `https://www.baseball-reference.com/players/{initial}/{player_code}.shtml`
- Sabermetric Fielding: `https://www.baseball-reference.com/players/{initial}/{player_code}-field.shtml`

## Available Functions

The `bref_single_player` module provides comprehensive player statistics across multiple categories:

### Batting Functions

- `single_player_standard_batting`: Standard batting statistics (AVG, HR, RBI, etc.)
- `single_player_value_batting`: Value-based batting metrics (WAR, RAR, etc.)
- `single_player_advanced_batting`: Advanced batting analytics (wOBA, ISO, exit velocity, etc.)

### Pitching Functions

- `single_player_standard_pitching`: Standard pitching statistics (ERA, WHIP, strikeouts, etc.)
- `single_player_value_pitching`: Value-based pitching metrics (WAR, RAA, etc.)
- `single_player_advanced_pitching`: Advanced pitching analytics (BABIP, FIP, pitch percentages, etc.)

### Fielding Functions

- `single_player_standard_fielding`: Standard fielding statistics (fielding percentage, errors, etc.)
- `single_player_sabermetric_fielding`: Advanced fielding metrics (DRS, UZR, etc.)

### Other Functions

- `single_player_salaries`: Player salary history

## Finding Player Codes

Player codes are required for all functions. You can find them using:

```python
from pybaseballstats.retrosheet import player_lookup

# Search for a player
results = player_lookup("Mike", "Trout")
print(results)  # Will show available player codes
```

The player code format is typically: `{last_name_first5}{first_name_first2}{number}`
Example: Mike Trout = "troutmi01"

## Function Details

### Batting Functions

#### single_player_standard_batting()

**Parameters:**

- `player_code` (str): The player's Baseball Reference code (can be found using `pybaseballstats.retrosheet.player_lookup`)
- `return_pandas` (bool, optional): Whether to return a pandas DataFrame. Defaults to False (returns polars DataFrame)

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Standard batting statistics

**Key Columns:**

- `age`: Player age for each season
- `games`, `pa`, `ab`: Games played, plate appearances, at-bats
- `r`, `h`, `doubles`, `triples`, `hr`: Runs, hits, doubles, triples, home runs
- `rbi`, `sb`, `cs`: RBIs, stolen bases, caught stealing
- `bb`, `so`: Walks, strikeouts
- `batting_avg`, `onbase_perc`, `slugging_perc`: Traditional rate stats
- `onbase_plus_slugging`: OPS
- `war`: Wins Above Replacement
- `key_bbref`: Player's Baseball Reference code

#### single_player_value_batting()

**Parameters:**

- `player_code` (str): Player's Baseball Reference code
- `return_pandas` (bool, optional): Return format preference

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Value-based batting metrics

**Key Columns:**

- `runs_batting`, `runs_baserunning`, `runs_fielding`: Component run values
- `runs_position`, `runs_replacement`: Positional and replacement level adjustments
- `raa`, `rar`: Runs Above Average/Replacement
- `waa`, `war`: Wins Above Average/Replacement
- `war_off`, `war_def`: Offensive and defensive WAR components

#### single_player_advanced_batting()

**Parameters:**

- `player_code` (str): Player's Baseball Reference code
- `return_pandas` (bool, optional): Return format preference

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Advanced batting analytics

**Key Columns:**

- `stolen_base_perc`: Stolen base success percentage
- `extra_bases_taken_perc`: Percentage of extra bases taken on hits
- `batting_avg_bip`: Batting average on balls in play
- `iso_slugging`: Isolated power (SLG - AVG)
- `home_run_perc`, `strikeout_perc`, `base_on_balls_perc`: Rate statistics
- `avg_exit_velo`, `hard_hit_perc`: Statcast metrics
- `pull_perc`, `center_perc`, `oppo_perc`: Directional hitting percentages

### Pitching Functions

#### single_player_standard_pitching()

**Parameters:**

- `player_code` (str): Player's Baseball Reference code
- `return_pandas` (bool, optional): Return format preference

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Standard pitching statistics

**Key Columns:**

- `w`, `l`: Wins and losses
- `g`, `gs`, `gf`: Games, games started, games finished
- `cg`, `sho`, `sv`: Complete games, shutouts, saves
- `ip`: Innings pitched
- `h`, `r`, `er`: Hits, runs, earned runs allowed
- `hr`, `bb`, `so`: Home runs, walks, strikeouts allowed
- `earned_run_avg`: ERA
- `whip`: Walks + hits per inning pitched
- `war`: Wins Above Replacement

#### single_player_value_pitching()

**Parameters:**

- `player_code` (str): Player's Baseball Reference code
- `return_pandas` (bool, optional): Return format preference

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Value-based pitching metrics

**Key Columns:**

- `ra9`: Runs allowed per 9 innings
- `ra9_opp`, `ra9_role`: Opposition and role adjustments
- `raa`, `rar`: Runs Above Average/Replacement
- `waa`, `war`: Wins Above Average/Replacement
- `leverage_index_avg_rp`: Average leverage index for relief pitchers

#### single_player_advanced_pitching()

**Parameters:**

- `player_code` (str): Player's Baseball Reference code
- `return_pandas` (bool, optional): Return format preference

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Advanced pitching analytics

**Key Columns:**

- `batting_avg_bip`: BABIP allowed
- `home_run_perc`, `strikeout_perc`, `base_on_balls_perc`: Rate statistics
- `avg_exit_velo`, `hard_hit_perc`: Statcast metrics against
- `ld_perc`, `gb_perc`, `fb_perc`: Line drive, ground ball, fly ball percentages
- `gb_fb_ratio`: Ground ball to fly ball ratio

### Fielding Functions

#### single_player_standard_fielding()

**Parameters:**

- `player_code` (str): Player's Baseball Reference code
- `return_pandas` (bool, optional): Return format preference

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Standard fielding statistics

**Key Columns:**

- `pos`: Position played
- `games`, `games_started`: Games and games started at position
- `innings`: Innings played at position
- `chances`, `po`, `assists`, `errors`: Total chances, putouts, assists, errors
- `fielding_perc`: Fielding percentage
- `dp`: Double plays participated in
- `range_factor_per_nine`, `range_factor_per_game`: Range factor metrics

#### single_player_sabermetric_fielding()

**Parameters:**

- `player_code` (str): Player's Baseball Reference code
- `return_pandas` (bool, optional): Return format preference

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Advanced fielding metrics

**Note:** This function accesses a separate fielding-specific page for more detailed defensive analytics.

### Other Functions

#### single_player_salaries()

**Parameters:**

- `player_code` (str): Player's Baseball Reference code
- `return_pandas` (bool, optional): Return format preference

**Returns:**

- `pl.DataFrame | pd.DataFrame`: Player salary history

**Key Columns:**

- `Year`: Season year
- `Team`: Team abbreviation
- `Lg`: League
- `salary ($)`: Annual salary in dollars

## Usage Examples

### Basic Usage

```python
# Option 1: Direct import
from pybaseballstats.bref_single_player import single_player_standard_batting
batting_stats = single_player_standard_batting("troutmi01")

# Option 2: Module import
import pybaseballstats as pyb
batting_stats = pyb.bref_single_player.single_player_standard_batting("troutmi01")
```

## Finding Player Codes

Player codes are required for all functions. You can find them using:

```python
from pybaseballstats.retrosheet import player_lookup

# Search for a player
results = player_lookup("Mike", "Trout")
print(results)  # Will show available player codes
```

The player code format is typically: `{last_name_first5}{first_name_first2}{number}`
Example: Mike Trout = "troutmi01"

## Performance Notes

**Important:** All functions use Selenium WebDriver to scrape data from Baseball Reference, which makes them slower than functions using direct HTTP requests. The functions include appropriate wait conditions to ensure data is fully loaded before extraction. Large career datasets may take longer to process.

## Data Coverage

- **Historical Range**: Data availability varies by statistic type, generally from early 1900s to present
- **Advanced Metrics**: Some advanced statistics (like Statcast data) are only available from 2015 onward
- **Salary Data**: Generally available from 1985 onward with some earlier data
- **Fielding Metrics**: Advanced fielding statistics have varying start dates depending on the metric

## Error Handling

Functions will return empty DataFrames or raise exceptions if:

- Player code is invalid or not found
- Player has no statistics in the requested category
- Network issues prevent data retrieval
- Baseball Reference page structure changes

Always verify that the returned DataFrame contains data before proceeding with analysis.
