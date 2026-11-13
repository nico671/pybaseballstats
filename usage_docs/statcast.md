# Statcast Documentation

This module provides functions to retrieve data from the [Statcast](https://baseballsavant.mlb.com/statcast_search) website, which allows the extraction of pitch-by-pitch level Statcast data for MLB games.

## Available Functions

- `pitch_by_pitch_data(...)`: Fetches pitch-by-pitch Statcast data for a specific date range.
  - Supports optional team filtering via `StatcastTeams`.
  - Supports chunking and concurrency controls for larger date ranges.
  - Returns a Polars `LazyFrame` by default (or `DataFrame` when `force_collect=True`).

## Function Parameters

`pitch_by_pitch_data(start_date, end_date, team=None, force_collect=False, *, chunk_size_days=3, show_progress=True, concurrency=None, verbose=False)`

- `start_date` (str): Start date in `YYYY-MM-DD` format.
- `end_date` (str): End date in `YYYY-MM-DD` format.
- `team` (StatcastTeams | None): Optional team filter. Must be a `StatcastTeams` enum value (not a raw string).
- `force_collect` (bool): If `True`, returns a Polars `DataFrame`; otherwise returns a Polars `LazyFrame`.
- `chunk_size_days` (int): Number of days per request chunk. Must be greater than 0.
- `show_progress` (bool): Show progress indicators while downloading/loading chunked responses.
- `concurrency` (int | None): Optional max concurrency override for HTTP requests.
- `verbose` (bool): Print additional runtime logs.

## Return Value

- `pl.LazyFrame` when `force_collect=False`
- `pl.DataFrame` when `force_collect=True`
- A valid response with no matching pitches returns an empty frame of the selected type. Header-only CSVs keep their columns.
- Download and header failures inside this call raise `RuntimeError`. With `force_collect=True`, parse failures also raise `RuntimeError` inside the call. With a `LazyFrame`, Polars can raise a parse error later when you call `.collect()`.

## Example Usage

### Basic usage

```python
import pybaseballstats.statcast as sc

# Fetch Statcast data for a specific date range (returns LazyFrame by default)
data = sc.pitch_by_pitch_data(start_date="2022-05-01", end_date="2022-05-31")
```

### Team filtering (enum-based)

```python
import pybaseballstats.statcast as sc
from pybaseballstats.enums import StatcastTeams

# Filter by a specific team using StatcastTeams
data = sc.pitch_by_pitch_data(
    start_date="2022-05-01",
    end_date="2022-05-31",
    team=StatcastTeams.YANKEES,
)
```

### Force eager collection (DataFrame)

```python
import pybaseballstats.statcast as sc

# Return a Polars DataFrame instead of a LazyFrame
data = sc.pitch_by_pitch_data(
    start_date="2022-05-01",
    end_date="2022-05-31",
    force_collect=True,
)
```

### Advanced download options

```python
import pybaseballstats.statcast as sc

data = sc.pitch_by_pitch_data(
    start_date="2022-05-01",
    end_date="2022-06-01",
    chunk_size_days=2,
    concurrency=8,
    show_progress=True,
    verbose=False,
)
```

### Show available teams

```python
import pybaseballstats.statcast as sc
from pybaseballstats.enums import StatcastTeams

# Print all available team enum options
print(StatcastTeams.show_options())
"""
DIAMONDBACKS: AZ
BRAVES: ATL
ORIOLES: BAL
RED_SOX: BOS
CUBS: CHC
REDS: CIN
GUARDIANS: CLE
ROCKIES: COL
WHITE_SOX: CWS
TIGERS: DET
ASTROS: HOU
ROYALS: KC
ANGELS: LAA
DODGERS: LAD
MARLINS: MIA
BREWERS: MIL
TWINS: MIN
METS: NYM
YANKEES: NYY
ATHLETICS: OAK
PHILLIES: PHI
PIRATES: PIT
PADRES: SD
MARINERS: SEA
GIANTS: SF
CARDINALS: STL
RAYS: TB
RANGERS: TEX
BLUE_JAYS: TOR
NATIONALS: WSH
"""
```

## Notes

1. The function internally uses async execution for performance, but exposes a synchronous API.
2. In notebook/active-event-loop environments, it applies `nest_asyncio` so the call still works.
3. If `team` is provided, it must be a valid `StatcastTeams` enum value or a `TypeError` is raised.
4. If `chunk_size_days <= 0`, a `TypeError` is raised.
