# Public API migration

This guide describes the planned coordinated breaking release. No version number or publication date is set.

## Imports

Use a source module for fetch functions and `pybaseballstats.enums` for team filters:

```python
from pybaseballstats import bref_teams as bt
from pybaseballstats.enums import BREFTeams

df = bt.batting(team=BREFTeams.ORIOLES, year=2025)
```

`import pybaseballstats.bref_teams as bt` and direct imports such as `from pybaseballstats.bref_teams import batting` also work. The supported source modules are `bref_draft`, `bref_managers`, `bref_single_player`, `bref_teams`, `retrosheet`, `statcast`, `statcast_leaderboards`, `statcast_single_game`, `statcast_single_player`, and `umpire_scorecards`. Modules whose names start with `_` are implementation details. Their paths and function pickle locations can change.

| Old enum path | New enum path |
| --- | --- |
| `pybaseballstats.bref_draft.BREFTeams` | `pybaseballstats.enums.BREFTeams` |
| `pybaseballstats.bref_teams.BREFTeams` | `pybaseballstats.enums.BREFTeams` |
| `pybaseballstats.statcast.StatcastTeams` | `pybaseballstats.enums.StatcastTeams` |
| `pybaseballstats.statcast_leaderboards.StatcastLeaderboardsTeams` | `pybaseballstats.enums.StatcastLeaderboardsTeams` |
| `pybaseballstats.umpire_scorecards.UmpireScorecardTeams` | `pybaseballstats.enums.UmpireScorecardTeams` |

These enum objects keep their identity. `GUARDIANS` and `DIAMONDBACKS` are the preferred names; `GAURDIANS` and `D_BACKS` remain aliases where those spellings existed. The Umpire Scorecards enum also has `TIGERS` with source code `DET`.

`umpire_scorecards.game_type_options()` was removed because it did not fetch data. The accepted game type codes are `*` (all), `R` (regular), `A` (All-Star), `P` (all postseason), `F` (Wild Card), `D` (Division Series), `L` (League Championship Series), and `W` (World Series).

## Results and errors

A wrong argument type raises `TypeError`. A correct type with an invalid value raises `ValueError`. A request, browser, decoding, parsing, or required source structure failure inside a package call raises `RuntimeError`. Where an underlying exception exists, it is chained as the cause. A valid response with no matching rows returns an empty result of the documented type. An unknown umpire name returns zero rows; it does not remove the name filter.

Statcast pitch-by-pitch calls return a Polars `LazyFrame` by default and a `DataFrame` with `force_collect=True`. Downloads and basic source checks happen inside the call. With eager collection, parse errors inside the call become `RuntimeError`. With a native lazy frame, a later `.collect()` can raise a Polars exception. Header-only CSV responses keep their column names. A failed chunk or Retrosheet shard fails the full request; it does not produce partial data.

The default season is now resolved when called for arm strength, catcher pop time, pitch arsenals, and pitch movement. Pass an explicit `year` or `season` for repeatable results. Arm strength still accepts `year="All"`. Other season defaults and the January/February park factor and timer rules are unchanged. The single-player Statcast supported-season table currently ends at 2026; a later calendar year is not added without verified season dates. Baseball Reference team codes use a separate historical mapping and its nearest-known-code fallback.
