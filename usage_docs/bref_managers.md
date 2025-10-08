# Baseball Reference Managers Data Documentation

This module provides functionality to retrieve data from [Baseball Reference's managers pages](https://www.baseball-reference.com/leagues/majors/2025-managers.shtml) (these are year by year but I've linked the 2025 season page). It includes functions to get basic manager statistics as well as manager tendencies.

## Available Functions

- `managers_basic_data(year)`: Fetches basic manager statistics for a specific year including wins, losses, games managed, and postseason performance.
- `manager_tendencies_data(year)`: Fetches manager tendencies data for a specific year including strategic decisions like stolen base attempts, sacrifice bunts, and pitching changes.

## Example Usage

Both of these functions take a single parameter, `year`, which is an integer representing the year for which you want to fetch data.

### Fetching Basic Manager Data

```python
import pybaseballstats.bref_managers as bm
# Fetch basic manager data for the year 2023
basic_data = bm.managers_basic_data(2023)
print(basic_data)
```

### Fetching Manager Tendencies Data

```python
import pybaseballstats.bref_managers as bm
# Fetch manager tendencies data for the year 2023
tendencies_data = bm.manager_tendencies_data(2023)
print(tendencies_data)
```

## Final Notes

1. These functions use Selenium so they may be slower than other data retrieval methods.
2. This package uses the `polars` library for data manipulation. If you wish to convert the returned DataFrame to a pandas DataFrame, you can use the `.to_pandas()` method on the returned DataFrame to convert it.
3. The functions handle missing data by filling empty strings and null values with appropriate defaults (typically 0).
4. All functions will automatically handle Baseball Reference's rate limiting (max of 10 requests per minute) by waiting and retrying as needed, please be patient.
