# Baseball Reference Managers Data Documentation

This module provides functions for pulling MLB manager data from Baseball Reference.

## Available Functions

- `managers_basic_data(year)`: Returns manager-level season records (wins/losses, games managed, replay/challenge outcomes, and postseason summary fields).
- `managers_tendencies_data(year)`: Returns manager tendencies (steal attempts, bunting, IBB usage, and pitching usage tendencies).

## Function Parameters

Both functions use the same parameter:

- `year` (int): MLB season year.

Validation rules:

- `year` must be provided.
- `year` must be an integer.
- `year` must be greater than or equal to `1871`.

## Example Usage

### Basic manager data

```python
import pybaseballstats.bref_managers as bm

basic_df = bm.managers_basic_data(2023)
print(basic_df)
```

### Manager tendencies

```python
import pybaseballstats.bref_managers as bm

tendencies_df = bm.managers_tendencies_data(2023)
print(tendencies_df)
```

## Notes

1. `managers_basic_data` uses Playwright and can be slower than simple HTTP scraping.
2. Both functions return Polars DataFrames.
3. Baseball Reference rate limits are handled internally by the shared BREF session utilities.
4. All functions take in a `verbose` parameter that, when set to True, will print debug information during the request process. This can be useful for troubleshooting Cloudflare blocks.
