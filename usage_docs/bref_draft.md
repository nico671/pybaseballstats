# Baseball Reference Draft Data Documentation

This module provides functionality to retrieve data from the [Baseball Reference Draft](https://www.baseball-reference.com/draft/) website. Specifically it mimics the functionality of the picks by Year/Round search as well as the Franchise/Year search.

## Available Functions

- `draft_picks_by_year_round(...)`: Fetches draft pick data for a specific year and round, with optional filters for team and position.
- `draft_picks_by_franchise_year(...)`: Fetches draft pick data for a specific franchise and year, with optional filters for round and position.
- `BREFTeams.show_options()`: Returns a list of all MLB teams that can be used as filters in other functions.

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

```python
import pybaseballstats.bref_draft as bd

# Fetch draft picks for a specific year and round
print(bd.draft_picks_by_year_round(2020, 1))  # will print all draft picks for the 2020 first round
```

### Fetching Draft Picks by Franchise and Year

```python
import pybaseballstats.bref_draft as bd

# Fetch draft picks for a specific franchise and year
print(bd.draft_picks_by_franchise_year(bd.BREFTeams.ANGELS, 2020))  # will print all draft picks for the 2020 Angels
```

## Final Notes

1. Please note that some of the restrictions you can enable through the parameters may result in no data being returned.
2. This package uses the `polars` library for data manipulation. If you wish to convert the returned DataFrame to a pandas DataFrame, you can use the `.to_pandas()` method on the returned DataFrame to convert it.
3. All functions will automatically handle Baseball Reference's rate limiting (max of 10 requests per minute) by waiting and retrying as needed, please be patient.
