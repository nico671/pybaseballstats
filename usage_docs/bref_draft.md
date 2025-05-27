# Baseball Reference Draft Docs

## Available Functions

- `draft_order_by_round`: Returns the draft order for a given round in a given year.
- `franchise_draft_order`: Returns the draft order for a given team in a given year.

## Quickstart

```python
from pybaseballstats.bref_draft import (
    BREFTeams,
    draft_order_by_round,
    franchise_draft_order,
)

# 1. List valid team codes:
print(BREFTeams.show_options())

# 2. Get round-1 draft order for 2024 as a Polars DataFrame:
df = draft_order_by_round(year=2024, draft_round=1)

# 3. Get the Yankees’ draft picks in 2023 as a Pandas DataFrame:
pd_df = franchise_draft_order(
    team=BREFTeams.YANKEES,
    year=2023,
    return_pandas=True
)
```

### BREFTeams Enum

Use this enum to specify team codes when calling `franchise_draft_order`. It includes all MLB teams with their respective codes.

```python
from pybaseballstats.bref_draft import BREFTeams
# Print all options:
print(BREFTeams.show_options())
# Example:
print(BREFTeams.DODGERS.value)  # "LAD"
```

### draft_order_by_round

This function retrieves the draft order for a specific round in a given year. It returns a Polars DataFrame by default, but you can specify `return_pandas=True` to get a Pandas DataFrame.

```python
draft_order_by_round(
    year: int,
    draft_round: int,
    return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame
```

- Args:
  - `year`: The year of the draft (1965-present).
  - `draft_round`: The round number (1-60). Note that not all rounds may be available for all years.
  - `return_pandas`: If True, returns a Pandas DataFrame instead of Polars.
- Raises:
  - `ValueError`: If the year is before 1965 or after the current year.
  - `ValueError`: If the draft round is not between 1 and 60.

### franchise_draft_order

This function retrieves the draft order for a specific team in a given year. It returns a Polars DataFrame by default, but you can specify `return_pandas=True` to get a Pandas DataFrame.

```python
franchise_draft_order(
    team: BREFTeams,
    year: int,
    return_pandas: bool = False
) -> pl.DataFrame | pd.DataFrame
```

- Args:
  - `team`: The team code from the `BREFTeams` enum.
  - `year`: The year of the draft (1965-present).
  - `return_pandas`: If True, returns a Pandas DataFrame instead of Polars.
- Raises:
  - `ValueError`: If the year is before 1965 or after the current year.
  - `ValueError`: If the team code is not valid.
- Returns:
  - A DataFrame containing the draft order for the specified team in the specified year.
  - One row per pick

## Tips and Troubleshooting

- Empty cells are filled with 0 in the DataFrame.
- Slower performance in this function due to usage of Selenium. Also note that there is a limit on Baseball Reference for how many requests you can make in a short period of time. This is automatically handled by the library, but if you encounter issues, try waiting a few seconds before making another request.
- If you encounter issues with the `BREFTeams` enum, ensure you are using the correct team code. You can always print `BREFTeams.show_options()` to see all valid codes.
- If you need to convert a Polars DataFrame to a Pandas DataFrame, you can use the `to_pandas()` method on the Polars DataFrame.
