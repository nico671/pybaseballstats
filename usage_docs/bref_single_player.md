# Baseball Reference Single Player Data (`bref_single_player`)

This module provides single-player Baseball Reference tables, returned as Polars DataFrames.

## Function naming convention

Core APIs use a metric-selector convention:

- `single_player_batting(player_code, metric_type=...)`
- `single_player_pitching(player_code, metric_type=...)`

Other currently available helpers:

- `single_player_standard_fielding(player_code)`
- `single_player_sabermetric_fielding(player_code)`

## API reference

### Batting

- `single_player_batting(player_code, metric_type="standard")`

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

- `single_player_pitching(player_code, metric_type="standard")`

Allowed `metric_type` values:

- `"standard"`
- `"value"`
- `"advanced"`
- `"ratio"`
- `"win_probability"`
- `"basesituation"`
- `"batting_against"`
- `"pitches"`
- `"cumulative"`

## Parameters and validation

All functions use:

- `player_code` (`str`) — Baseball Reference player identifier (for example `"troutmi01"`).

`single_player_batting(...)` additionally uses:

- `metric_type` selector shown above

`single_player_pitching(...)` additionally uses:

- `metric_type` selector shown above

Validation behavior:

- If `metric_type` is invalid, `single_player_batting(...)` raises `ValueError`.
- If `metric_type` is invalid, `single_player_pitching(...)` raises `ValueError`.
- If the requested page/table cannot be loaded, an error is raised (`ValueError` for batting/pitching).

## Usage examples

### Basic import

```python
import pybaseballstats.bref_single_player as bsp
```

### Batting tables

```python
import pybaseballstats.bref_single_player as bsp

player_code = "troutmi01"

standard_bat_df = bsp.single_player_batting(player_code, metric_type="standard")
advanced_bat_df = bsp.single_player_batting(player_code, metric_type="advanced")
wpa_bat_df = bsp.single_player_batting(player_code, metric_type="win_probability")
cumulative_bat_df = bsp.single_player_batting(player_code, metric_type="cumulative")
```

### Pitching tables

```python
import pybaseballstats.bref_single_player as bsp

player_code = "troutmi01"

standard_pitch_df = bsp.single_player_pitching(player_code, metric_type="standard")
advanced_pitch_df = bsp.single_player_pitching(player_code, metric_type="advanced")
against_pitch_df = bsp.single_player_pitching(player_code, metric_type="batting_against")
cumulative_pitch_df = bsp.single_player_pitching(player_code, metric_type="cumulative")
```

## Notes

1. All functions return `polars.DataFrame`.
2. Several functions use Playwright-backed rendering and can be slower than direct HTTP table reads.
3. Batting table columns are normalized by removing Baseball Reference suffix/prefix patterns such as `b_` and `_abbr`.
4. Pitching table columns are normalized by removing Baseball Reference suffix/prefix patterns such as `_abbr` (and typically `p_`, depending on source table naming).
