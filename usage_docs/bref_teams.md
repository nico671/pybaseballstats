# Baseball Reference Team Data (`bref_teams`)

This module provides team-season data from Baseball Reference pages, returned as Polars DataFrames.

## Function naming convention

Core APIs use a metric-selector convention:

- `batting(team, year, metric_type=...)`
- `pitching(team, year, metric_type=...)`
- `fielding(team, year, metric_type=..., position=...)`

## API reference

### Example: team page tables

- `game_by_game_schedule_results(team, year)`
- `roster_and_appearances(team, year)`

### Batting

- `batting(team, year, metric_type="standard")`

Allowed `metric_type` values:

- `"standard"`
- `"value"`
- `"advanced"`
- `"sabermetric"`
- `"ratio"`
- `"win_probability"`
- `"baserunning"`
- `"situational"`
- `"pitches"`
- `"cumulative"`

### Pitching

- `pitching(team, year, metric_type="standard")`

Allowed `metric_type` values:

- `"standard"`
- `"value"`
- `"advanced"`
- `"ratio"`
- `"batting_against"`
- `"win_probability"`
- `"starting"`
- `"relief"`
- `"baserunning_situational"`
- `"cumulative"`

### Fielding

- `fielding(team, year, metric_type, position="")`

## Parameters and validation

All functions use:

- `team` (`BREFTeams`) — team enum from `pybaseballstats.bref_teams.BREFTeams`
- `year` (`int`) — MLB season year

`batting(...)` additionally uses:

- `metric_type` selector shown above

`pitching(...)` additionally uses:

- `metric_type` selector shown above

`fielding(...)` additionally uses:

- `metric_type` (`Literal["standard", "advanced"]`)
- `position` (`Literal[...]`) selector

Allowed `position` values by metric type:

- `metric_type="standard"`
  - `""` or `"all"` (same table)
  - `"c"`, `"1b"`, `"2b"`, `"3b"`, `"ss"`, `"lf"`, `"cf"`, `"rf"`, `"of"`, `"p"`, `"dh"`
- `metric_type="advanced"`
  - `"c"`, `"c_baserunning"`, `"1b"`, `"2b"`, `"3b"`, `"ss"`, `"lf"`, `"cf"`, `"rf"`, `"p"`

Validation behavior:

- If `team` is not a `BREFTeams` value, a `ValueError` is raised.
- If the underlying page/table cannot be loaded, an error is raised (`ValueError` in most functions).
- For `fielding(...)`, invalid `metric_type` or invalid `position` for that `metric_type` raises `ValueError`.
- `position=""` or `position="all"` is only valid for `metric_type="standard"`.

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

standard_bat_df = bt.batting(team, year, metric_type="standard")
ratio_bat_df = bt.batting(team, year, metric_type="ratio")

standard_pitch_df = bt.pitching(team, year, metric_type="standard")
against_pitch_df = bt.pitching(team, year, metric_type="batting_against")
wpa_pitch_df = bt.pitching(team, year, metric_type="win_probability")
```

### Fielding tables

```python
import pybaseballstats.bref_teams as bt

team = bt.BREFTeams.YANKEES
year = 2025

# standard fielding (all players)
fielding_standard_all_df = bt.fielding(team, year, metric_type="standard", position="all")

# standard fielding by position
fielding_standard_c_df = bt.fielding(team, year, metric_type="standard", position="c")

# advanced fielding by position
fielding_advanced_ss_df = bt.fielding(team, year, metric_type="advanced", position="ss")

# advanced catcher baserunning
fielding_advanced_c_br_df = bt.fielding(
 team,
 year,
 metric_type="advanced",
 position="c_baserunning",
)
```

## Notes

1. All functions return `polars.DataFrame`.
2. Several functions use Playwright-backed rendering and can be slower than direct HTTP table reads.
3. Most batting/pitching/fielding table functions normalize column names by removing Baseball Reference prefixes/suffixes such as `b_`, `p_`, `f_`, and `_abbr`.
4. Batting and pitching normalize player identity columns to `player_name`.
