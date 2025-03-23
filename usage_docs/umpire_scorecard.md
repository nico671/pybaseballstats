# Umpire Scorecard Functions and Usage

## Available Functions

1. `umpire_games_date_range`
   - Per game umpire scorecard data for a given date range.
2. `umpire_stats_date_range`
   - Individual umpire stats for a given date range.
3. `team_umpire_stats_date_range`
   - Umpire stats for teams for a given date range.

## Usage

### `umpire_games_date_range`

#### Parameters

- `start_date`: Start date for the date range in the format 'YYYY-MM-DD'.
- `end_date`: End date for the date range in the format 'YYYY-MM-DD'.
- `season_type`: Restrict games to only regular season games ("R"), only postseason games ("P") or both ("\*"). Defaults to "\*".
- `home_team`: Restrict games to ones where the given team is the home team. Defaults to UmpireScorecardTeams.ALL.
- `away_team`: Restrict games to ones where the given team is the away team. Defaults to UmpireScorecardTeams.ALL.
- `umpire_name`: Restrict games to ones where the name of the umpire matches the parameter. If "" then all umpires are allowed. Defaults to "".
- `return_pandas`: If True, the function will return a pandas DataFrame. If False, the function will return a list of dictionaries. Defaults to False.

#### Examples

```python
# Import the function
from pybaseballstats import umpire_games_date_range

# Get the umpire scorecard data for all games in July 2021, with any umpire and any teams
df = umpire_games_date_range("2021-07-01", "2021-07-31", home_team=UmpireScorecardTeams.ALL, away_team=UmpireScorecardTeams.ALL, umpire_name="")

# Get the umpire scorecard data for all games in July 2021, with the umpire "Joe West" and any teams
df = umpire_games_date_range("2021-07-01", "2021-07-31", home_team=UmpireScorecardTeams.ALL, away_team=UmpireScorecardTeams.ALL, umpire_name="Joe West")

# Get the umpire scorecard data for all games in July 2021, with any umpire and the home team "BOS"
df = umpire_games_date_range("2021-07-01", "2021-07-31", home_team=UmpireScorecardTeams.BOS, away_team=UmpireScorecardTeams.ALL, umpire_name="")

# Get the umpire scorecard data for all postseason games between 2022 and 2024, with any umpire and any teams
df = umpire_games_date_range("2022-01-01", "2024-12-31", season_type="P", home_team=UmpireScorecardTeams.ALL, away_team=UmpireScorecardTeams.ALL, umpire_name="")
```
