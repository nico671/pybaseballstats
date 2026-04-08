# Baseball Reference Teams Data Documentation

This module provides functions for pulling MLB team-level data from Baseball Reference team pages.

## Available Functions

- `game_by_game_schedule_results(team, year)`: Returns game-by-game schedule/results rows for one team season.
- `roster_and_appearances(team, year)`: Returns team roster/appearances rows for one team season.
- `standard_batting(team, year)`: Returns standard batting stats.
- `value_batting(team, year)`: Returns value batting stats.
- `advanced_batting(team, year)`: Returns advanced batting stats.
- `sabermetric_batting(team, year)`: Returns sabermetric batting stats.
- `ratio_batting(team, year)`: Returns ratio batting stats.
- `win_probability_batting(team, year)`: Returns win probability batting stats.
- `baserunning_batting(team, year)`: Returns baserunning batting stats.
- `situational_batting(team, year)`: Returns situational batting stats.
- `pitches_batting(team, year)`: Returns pitches/plate-discipline batting stats.
- `career_cumulative_batting(team, year)`: Returns cumulative career batting summaries for players on the team page.

## Function Parameters

All functions in this module use:

- `team` (`BREFTeams`): Team enum value from `pybaseballstats.consts.bref_consts.BREFTeams`.
- `year` (`int`): MLB season year.

Validation rules:

- `team` must be a `BREFTeams` enum value.
- If Baseball Reference content cannot be retrieved or the expected table is missing, the function raises an error.

## Example Usage

### Importing the module

```python
import pybaseballstats.bref_teams as bt
```

### See available teams

```python
import pybaseballstats.bref_teams as bt

print(bt.BREFTeams.show_options())
```

### Schedule/results and roster

```python
import pybaseballstats.bref_teams as bt

schedule_df = bt.game_by_game_schedule_results(bt.BREFTeams.YANKEES, 2023)
roster_df = bt.roster_and_appearances(bt.BREFTeams.YANKEES, 2023)

print(schedule_df)
print(roster_df)
```

### Batting tables

```python
import pybaseballstats.bref_teams as bt

team = bt.BREFTeams.DODGERS
year = 2023

standard_df = bt.standard_batting(team, year)
value_df = bt.value_batting(team, year)
advanced_df = bt.advanced_batting(team, year)
sabermetric_df = bt.sabermetric_batting(team, year)
ratio_df = bt.ratio_batting(team, year)
wpa_df = bt.win_probability_batting(team, year)
baserunning_df = bt.baserunning_batting(team, year)
situational_df = bt.situational_batting(team, year)
pitches_df = bt.pitches_batting(team, year)
cumulative_df = bt.career_cumulative_batting(team, year)

print(standard_df)
```

## Notes

1. All functions return Polars DataFrames.
2. Some functions use Playwright-backed page loading and may run slower than plain HTTP table reads.
3. Most batting functions strip `b_` and `_abbr` column name prefixes/suffixes and cast numeric/percentage fields to numeric dtypes.
4. `career_cumulative_batting` is defined in `bref_teams.py` and can be accessed as `pybaseballstats.bref_teams.career_cumulative_batting(...)`.
