# Retrosheet Documentation

The Retrosheet module reads Daily Logs, Game Logs, original schedules, and reference tables. It also supports player lookup and ejection data.

## Logs and schedules

The archive functions download the required files before returning a Polars `LazyFrame`. Add row filters or select columns before calling `.collect()`. Set `force_collect=True` to return a `DataFrame` from the same query.

| Function | Filters |
| --- | --- |
| `player_seasons` | `season`, `player_id`, `team_id` |
| `game_info`, `team_logs` | `season`, `game_id`, `team_id`, `park_id` |
| `batting_logs`, `pitching_logs`, `fielding_logs` | `season`, `game_id`, `player_id`, `team_id` |
| `plays` | `season`, `game_id`, `player_id`, `team_id`, `park_id` |
| `manager_logs`, `umpire_logs` | Require `manager_id` or `umpire_id`, respectively |
| `game_logs` | Require `season`. Accept `team_id` and `game_type`. |
| `schedules` | Require `season`. Accept `team_id`. |

Supply at least one filter. Use Retrosheet IDs such as `LAN` for the Los Angeles Dodgers and `ohtas001` for Shohei Ohtani. A game ID supplies the season. Without a season, a player filter for `plays` uses the player's recorded seasons to select archives. The result includes plays in which the player batted, pitched, ran the bases, or had a recorded fielding action. Batting, pitching, and fielding logs from the player-specific archives include an `eject` flag. This column is null if the source table has no ejection field.

For `plays` queries with a team or park ID, supply `season` or `game_id` to read a season archive. Team and park archives can omit older plays. You can also supply `player_id`, `collection`, or `archive_path` to select a source for the query.

The seven Daily Logs functions accept `collection`. League and game-type values are `american_national_league`, `federal_league`, `negro_leagues`, `regular`, `all_star`, `postseason`, and `tiebreakers`. Curated values are `three_home_runs`, `fifteen_strikeouts`, `twenty_innings`, `twenty_runs`, `cycles`, `interracial_exhibition`, `no_hitters`, and `triple_plays`. The team and player statistics functions accept `stattype`. The default, `value`, selects Retrosheet's estimates. Use `official`, `lower`, `upper`, or `all` to request other rows where available. [Daily Logs and collections](https://www.retrosheet.org/downloads/csvdownloads.html) · [Statistical row types](https://www.retrosheet.org/downloads/csvoverview.html)

`game_logs` defaults to `game_type="regular"`. The other values are `world_series`, `all_star`, `wild_card`, `division_series`, `league_championship`, and `chronicle_telegraph_cup`. `schedules` returns planned games. For 2020, use `schedule_version` to select the `original` or `revised` schedule. `park_id` is available for seasons whose schedule includes a location. `makeup` retains the source text because a row can list multiple makeup dates. [Game Logs](https://www.retrosheet.org/gamelogs/index.html) · [Schedules](https://www.retrosheet.org/schedule/index.html)

```python
import pybaseballstats.retrosheet as rs

plays = rs.plays(player_id="ohtas001", season=2025)
events = plays.select("gid", "pn", "event").collect()

games = rs.game_logs(season=2025, team_id="LAN", force_collect=True)
schedule = rs.schedules(season=2020).filter(schedule_version="revised")
```

## Downloads and temporary storage

- The library checks the official download pages for archive links. If a requested season is missing from a listing held in memory, the library checks the page again.
- The library extracts only the files needed for the query. It reuses files within the same Python process and removes the temporary workspace at normal exit. Keep the process running until you finish collecting its lazy queries.
- The workspace limit is **2 GiB per process**. It includes compressed ZIPs, extracted files, and partial writes. Set the environment variable `PYBASEBALLSTATS_RETROSHEET_MAX_BYTES` to a positive integer in bytes before the first archive call. A request that exceeds the limit fails and reports the workspace path and current usage. The caller is responsible for choosing a limit that fits the machine and the intended queries.
- The workspace is a directory named `pybaseballstats-retrosheet-*` in the system temporary directory. Forced termination can leave it behind. Remove a leftover directory after its Python process has ended.
- Use `archive_path` to read a local Retrosheet ZIP. For a Daily Logs or play-by-play season ZIP, supply `season` or, where supported, a `game_id` from that season. For a collection query, supply the ZIP for that collection. The library leaves your ZIP in place, and the extracted files count toward the workspace limit.
- When a request needs a broad Daily Logs download, set `allow_bulk_download=True` or supply a local ZIP. The library warns before streaming a bulk download. Extraction can require much more disk space than the ZIP itself, and the normal workspace limit still applies.

## Reference tables

These functions return a `DataFrame`. Each accepts `archive_path` for a local ZIP.

| Daily Logs companion function | Required filter |
| --- | --- |
| `ballparks` | `park_id` |
| `people_bios`, `relatives` | `person_id` |
| `coaches`, `managers`, `teams`, `umpires` | `coach_id`, `manager_id`, `team_id`, `umpire_id`, respectively |

The Game Logs reference files are available through `people_ids(person_id=...)`, `coach_assignments(coach_id=...)`, `ballpark_codes(park_id=...)`, and `franchise_codes(team_id=...)`.

## Available Functions

- `player_lookup`: Look up players by first and/or last name.
- `ejections_data`: Retrieve ejection data for a specific date range, ejectee, umpire, or inning.

## Function Parameters

### `player_lookup(first_name=None, last_name=None, strip_accents=False)`

- `first_name` (str, optional): The first name of the player.
- `last_name` (str, optional): The last name of the player.
- `strip_accents` (bool, optional): Whether to normalize accents before matching. Defaults to `False`.

### `ejections_data(start_date=None, end_date=None, ejectee_name=None, umpire_name=None, inning=None)`

- `start_date` (str, optional): Start date in `MM/DD/YYYY` format.
- `end_date` (str, optional): End date in `MM/DD/YYYY` format.
- `ejectee_name` (str, optional): Case-sensitive substring filter on ejected person name.
- `umpire_name` (str, optional): Case-sensitive substring filter on umpire name.
- `inning` (int, optional): Inning filter from -1 to 20.

## Example Usage

### Player Lookup

This function is most commonly used to get a player's `key_bbref` value, which can then be passed into functions in `bref_single_player`.

```python
import pybaseballstats.retrosheet as rs
import pybaseballstats.bref_single_player as bsp
import polars as pl

# Lookup a player by first and last name
player_info = rs.player_lookup(first_name="Mike", last_name="Trout")
key_bbref = player_info.select(pl.col("key_bbref")).to_series()[0]  
# Use the player ID to get more detailed information from Baseball Reference
bsp.single_player_batting(player_code=key_bbref, metric_type="standard")
```

```python
# Lookup a player by last name only
import pybaseballstats.retrosheet as rs
player_info = rs.player_lookup(last_name="Rodriguez")
```

### Ejections Data

This function allows you to retrieve ejection data for a specific date range, ejectee, umpire, or inning. You can combine filters to narrow your search.

## Notes

- `start_date`/`end_date` must use `MM/DD/YYYY` format.
- If you omit `start_date` and/or `end_date`, the full available range is used for that side of the filter.

```python
import pybaseballstats.retrosheet as rs
rs.ejections_data(start_date="04/01/2010", end_date="04/30/2023", ejectee_name="Harper")
```

## Attribution

The information used here was obtained free of charge from and is copyrighted by Retrosheet. Interested parties may contact Retrosheet at 20 Sunset Rd., Newark, DE 19711.
