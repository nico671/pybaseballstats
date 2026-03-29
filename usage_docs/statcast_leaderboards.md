# Statcast Leaderboards Documentation

This module provides access to several Baseball Savant leaderboard endpoints.

## Available Functions

- `park_factor_dimensions_leaderboard(season, metric="distance")`
- `park_factor_yearly_leaderboard(season, bat_side="", conditions="All", rolling_years=3)`
- `park_factor_distance_leaderboard(season)`
- `timer_infractions_leaderboard(season, perspective="Pit", min_pitches=1)`
- `arm_strength_leaderboard(stat_type="player", year=2025, min_throws=50, pos="All", team=None)`

## Function Parameters

### `park_factor_dimensions_leaderboard`

- `season` (int): Season year.
- `metric` (`"distance" | "height"`): Which fence metric set to return.

Validation:

- `season` must be between `2015` and the current in-season year.
- `metric` must be `"distance"` or `"height"`.

### `park_factor_yearly_leaderboard`

- `season` (int): Season year.
- `bat_side` (`"L" | "R" | ""`): Batter-side filter.
- `conditions` (`"All" | "Day" | "Night" | "Open Air" | "Roof Closed"`): Game-condition filter.
- `rolling_years` (int): 1, 2, or 3-year rolling window.

Validation:

- `season` must be between `1999` and the current in-season year.
- `rolling_years` must be one of `1`, `2`, `3`.

### `park_factor_distance_leaderboard`

- `season` (int): Season year.

Validation:

- `season` must be between `2016` and the current in-season year.

### `timer_infractions_leaderboard`

- `season` (int): Season year.
- `perspective` (`"Pit" | "Bat" | "Cat" | "Team"`): Perspective for leaderboard rows.
- `min_pitches` (int): Minimum pitch count threshold.

Validation:

- `season` must be between `2023` and the current in-season year.
- `min_pitches` must be at least `1`.

### `arm_strength_leaderboard`

- `stat_type` (`"player" | "team"`): Output granularity.
- `year` (int | `"All"`): `2020`..current year, or `"All"`.
- `min_throws` (int): Minimum throws threshold.
- `pos` (`"All" | "2b_ss_3b" | "outfield" | "1b" | "2b" | "3b" | "shortstop" | "lf" | "cf" | "rf"`): Position filter.
- `team` (`StatcastLeaderboardsTeams | None`): Optional team filter.

Validation:

- `min_throws` must be at least `1`.
- `team` must be `None` or a `StatcastLeaderboardsTeams` enum value.

## Team Enum Helper

`StatcastLeaderboardsTeams.show_options()` returns all supported team options.

```python
import pybaseballstats.statcast_leaderboards as sl
print(sl.StatcastLeaderboardsTeams.show_options())
```

## Example Usage

### Park dimensions leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.park_factor_dimensions_leaderboard(season=2025, metric="distance")
print(df)
```

### Park yearly leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.park_factor_yearly_leaderboard(
    season=2025,
    bat_side="L",
    conditions="All",
    rolling_years=3,
)
print(df)
```

### Park factor distance leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.park_factor_distance_leaderboard(season=2025)
print(df)
```

### Pitch timer infractions leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.timer_infractions_leaderboard(
    season=2025,
    perspective="Pit",
    min_pitches=50,
)
print(df)
```

### Arm strength leaderboard

```python
import pybaseballstats.statcast_leaderboards as sl

df = sl.arm_strength_leaderboard(
    stat_type="player",
    year=2025,
    min_throws=100,
    pos="rf",
    team=sl.StatcastLeaderboardsTeams.YANKEES,
)
print(df)
```

## Notes

1. Some leaderboard functions use Playwright to render and parse table HTML, which can be slower than pure CSV/API endpoints.
2. Returned data is always a Polars DataFrame.
3. Column names can differ by endpoint because they mirror Baseball Savant output and then apply endpoint-specific renaming.
