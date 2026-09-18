# Baseball Reference Single Player Data (`bref_single_player`)

This module provides single-player Baseball Reference tables, returned as Polars DataFrames.

## Function naming convention

Core APIs use a metric-selector convention:

- `single_player_batting(player_code, metric_type=...)`
- `single_player_pitching(player_code, metric_type=...)`
- `single_player_fielding(player_code, metric_type=..., position=...)`

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

### Fielding

- `single_player_fielding(player_code, metric_type, position=None)`

Allowed `metric_type` values:

- `"standard"`
- `"appearances"`
- `"sabermetric"`
- `"advanced_at_position"`

Allowed `position` values:

- `"3b"`, `"ss"`, `"2b"`, `"1b"`, `"c"`, `"c_baserunning"`, `"lf"`, `"rf"`, `"cf"`, `"p"`

`position` rules:

- required when `metric_type="advanced_at_position"`
- must be omitted for all other `metric_type` values

## Parameters and validation

All functions use:

- `player_code` (`str`) — Baseball Reference player identifier (for example `"troutmi01"`).

`single_player_batting(...)` additionally uses:

- `metric_type` selector shown above

`single_player_pitching(...)` additionally uses:

- `metric_type` selector shown above

`single_player_fielding(...)` additionally uses:

- `metric_type` selector shown above
- `position` selector/rules shown above

Validation behavior:

- If `metric_type` is invalid, `single_player_batting(...)` raises `ValueError`.
- If `metric_type` is invalid, `single_player_pitching(...)` raises `ValueError`.
- If `metric_type` is invalid, `single_player_fielding(...)` raises `ValueError`.
- If `position` is missing/invalid/misused for `single_player_fielding(...)`, a `ValueError` is raised.
- If the requested page/table cannot be loaded, an error is raised (`ValueError` for batting/pitching/fielding).

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

### Fielding tables

```python
import pybaseballstats.bref_single_player as bsp

player_code = "sheldsc01"

standard_field_df = bsp.single_player_fielding(player_code, metric_type="standard")
appearances_field_df = bsp.single_player_fielding(player_code, metric_type="appearances")
sabermetric_field_df = bsp.single_player_fielding(player_code, metric_type="sabermetric")
advanced_lf_field_df = bsp.single_player_fielding(
  player_code,
  metric_type="advanced_at_position",
  position="lf",
)
```

## Notes

1. All functions return `polars.DataFrame`.
2. Several functions use Playwright-backed rendering and can be slower than direct HTTP table reads.
3. Batting table columns are normalized by removing Baseball Reference suffix/prefix patterns such as `b_` and `_abbr`.
4. Pitching table columns are normalized by removing Baseball Reference suffix/prefix patterns such as `_abbr` (and typically `p_`, depending on source table naming).
5. Fielding table columns are normalized by removing Baseball Reference suffix/prefix patterns such as `f_` and `_abbr`.
6. All functions take in a `verbose` parameter that, when set to True, will print debug information during the request process. This can be useful for troubleshooting Cloudflare blocks.
