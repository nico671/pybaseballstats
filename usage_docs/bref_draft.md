# Baseball Reference Draft Data Documentation

This module retrieves MLB draft data from [Baseball Reference Draft](https://www.baseball-reference.com/draft/).

## Available Functions

- `draft_order_by_year_round(year, draft_round)`: Fetches draft data for one year/round combination.
- `franchise_draft_order(team, year)`: Fetches draft data for one franchise/year combination.
- `BREFTeams.show_options()`: Shows valid enum values for franchise filtering.

## Function Parameters

### `draft_order_by_year_round(year, draft_round)`

- `year` (int): The year of the draft (e.g., 2020).
- `draft_round` (int): The draft round (must be 1 through 60).

### `franchise_draft_order(team, year)`

- `team` (BREFTeams): Team enum value from `BREFTeams`.
- `year` (int): The year of the draft (e.g., 2020).

## Example Usage

### Seeing Available Teams

This function doesn't return any data from the Baseball Reference Draft website. Instead, it prints the available teams that can be used as filters in other functions.

```python
import pybaseballstats.bref_draft as bd
print(bd.BREFTeams.show_options()) # will print all of the available teams
"""
ANGELS: ANA
DIAMONDBACKS: ARI
BRAVES: ATL
ORIOLES: BAL
RED_SOX: BOS
CUBS: CHC
WHITE_SOX: CHW
REDS: CIN
GUARDIANS: CLE
ROCKIES: COL
TIGERS: DET
MARLINS: FLA
ASTROS: HOU
ROYALS: KCR
DODGERS: LAD
BREWERS: MIL
TWINS: MIN
METS: NYM
YANKEES: NYY
ATHLETICS: OAK
PHILLIES: PHI
PIRATES: PIT
PADRES: SDP
MARINERS: SEA
GIANTS: SFG
CARDINALS: STL
RAYS: TBD
RANGERS: TEX
BLUE_JAYS: TOR
NATIONALS: WSN  
"""
```

### Fetching Draft Picks by Year and Round

To get draft picks for a specific year and round, use `draft_order_by_year_round`.

```python
import pybaseballstats.bref_draft as bd

# Fetch draft picks for a specific year and round
print(bd.draft_order_by_year_round(2020, 1))  # will print all draft picks for the 2020 first round
```

### Fetching Draft Picks by Franchise and Year

To get draft picks for a specific franchise and year, use `franchise_draft_order`.

```python
import pybaseballstats.bref_draft as bd

# Fetch draft picks for a specific franchise and year
print(bd.franchise_draft_order(bd.BREFTeams.ANGELS, 2020))  # will print all draft picks for the 2020 Angels
```

## Notes

1. Draft data is only available from 1965 onward.
2. `draft_order_by_year_round` requires `draft_round` between 1 and 60.
3. `franchise_draft_order` requires `team` to be a valid `BREFTeams` enum value.
4. This package uses the `polars` library for data manipulation. If you wish to convert the returned DataFrame to a pandas DataFrame, you can use the `.to_pandas()` method on the returned DataFrame to convert it.
5. All functions will automatically handle Baseball Reference rate limiting via shared session utilities.
6. All functions take in a `verbose` parameter that, when set to True, will print debug information during the request process. This can be useful for troubleshooting Cloudflare blocks.
