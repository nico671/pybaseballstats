# Baseball Reference Single Player Documentation

This module provides functions to retrieve data from the [Baseball Reference](https://www.baseball-reference.com/) website, specifically for single player statistics.

## Available Functions

- `single_player_standard_batting(...)`: Fetches standard batting statistics for a single player.
- `single_player_advanced_batting(...)`: Fetches advanced batting statistics for a single player.
- `single_player_value_batting(...)`: Fetches value batting statistics for a single player.
- `single_player_standard_fielding(...)`: Fetches standard fielding statistics for a single player.
- `single_player_sabermetric_fielding(...)`: Fetches advanced fielding statistics for a single player.
- `single_player_standard_pitching(...)`: Fetches standard pitching statistics for a single player.
- `single_player_advanced_pitching(...)`: Fetches advanced pitching statistics for a single player.
- `single_player_value_pitching(...)`: Fetches value pitching statistics for a single player.

## Example Usage

Note that all functions require a `player_id` parameter, which is the unique identifier for a player on Baseball Reference. This ID can either be found from the player's URL on Baseball Reference or by using the `player_lookup` function
from the `retrosheet` module. Information on how to use the `player_lookup` function can be found in the [Retrosheet Documentation](./retrosheet.md).

Since all of these functions are so similar, we will only show an example of one of them here. The usage for the other functions is analogous.

```python
# Assuming you have already looked up the player ID using the retrosheet player_lookup functions and it is stored in the variable `player_id`
import pybaseballstats.bref_single_player as bsp
bsp.single_player_standard_batting(player_code=player_id)
```
