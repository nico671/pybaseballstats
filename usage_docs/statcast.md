# Statcast Documentation

This module provides functions to retrieve data from the [Statcast](https://baseballsavant.mlb.com/statcast_search) website, which allows the extraction of pitch-by-pitch level Statcast data for MLB games.

## Available Functions

- `pitch_by_pitch_data(...)`: Fetches Statcast data for a specific date range.
  - Use team abbreviation to filter by team. (AZ, ATL, KC, etc...)
  - Currently this function doesn't support filtering by player, but it can be extended in the future.

## Example Usage

```python
import pybaseballstats.statcast as sc

# Fetch Statcast data for a specific date range
data = sc.pitch_by_pitch_data(start_date="2022-05-01", end_date="2022-05-31")

# Fetch Statcast data for a specific date range + specific team"
data = sc.pitch_by_pitch_data(start_date="2022-05-01", end_date="2022-05-31", team="NYY")

#To print all available teams
print(sc.StatcastTeams.show_options())|
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
