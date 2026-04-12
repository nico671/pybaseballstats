# Baseball Reference Team Data (`bref_teams`)

This module provides team-season data from Baseball Reference pages, returned as Polars DataFrames.

## Function naming convention

Functions are named consistently as:

- `<descriptor>_batting`
- `<descriptor>_pitching`

## API reference

### Example: team page tables

- `game_by_game_schedule_results(team, year)`
- `roster_and_appearances(team, year)`

### Batting tables

- `standard_batting(team, year)`
- `value_batting(team, year)`
- `advanced_batting(team, year)`
- `sabermetric_batting(team, year)`
- `ratio_batting(team, year)`
- `win_probability_batting(team, year)`
- `baserunning_batting(team, year)`
- `situational_batting(team, year)`
- `pitches_batting(team, year)`
- `career_cumulative_batting(team, year)`

### Pitching tables

- `standard_pitching(team, year)`
- `value_pitching(team, year)`
- `advanced_pitching(team, year)`
- `ratio_pitching(team, year)`
- `batting_against_pitching(team, year)`
- `win_probability_pitching(team, year)`
- `starting_pitching(team, year)`
- `relief_pitching(team, year)`
- `baserunning_situational_pitching(team, year)`
- `career_cumulative_pitching(team, year)`

## Parameters and validation

All functions use:

- `team` (`BREFTeams`) — team enum from `pybaseballstats.bref_teams.BREFTeams`
- `year` (`int`) — MLB season year

Validation behavior:

- If `team` is not a `BREFTeams` value, a `ValueError` is raised.
- If the underlying page/table cannot be loaded, an error is raised (`ValueError` in most functions).

## Usage examples

### Basic import

```python
import pybaseballstats.bref_teams as bt
```

### Show team enum options

```python
import pybaseballstats.bref_teams as bt

print(bt.BREFTeams.show_options())
```

### Team page tables

```python
import pybaseballstats.bref_teams as bt

team = bt.BREFTeams.YANKEES
year = 2025

schedule_df = bt.game_by_game_schedule_results(team, year)
roster_df = bt.roster_and_appearances(team, year)
```

### Batting + pitching tables

```python
import pybaseballstats.bref_teams as bt

team = bt.BREFTeams.YANKEES
year = 2025

standard_bat_df = bt.standard_batting(team, year)
ratio_bat_df = bt.ratio_batting(team, year)

standard_pitch_df = bt.standard_pitching(team, year)
against_pitch_df = bt.batting_against_pitching(team, year)
wpa_pitch_df = bt.win_probability_pitching(team, year)
```

## Notes

1. All functions return `polars.DataFrame`.
2. Several functions use Playwright-backed rendering and can be slower than direct HTTP table reads.
3. Most batting/pitching table functions normalize column names by removing Baseball Reference prefixes/suffixes such as `b_`, `p_`, and `_abbr`.
