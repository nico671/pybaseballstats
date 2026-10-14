# Baseball Reference Managers Data Documentation

This module provides functions for pulling MLB manager data from Baseball Reference.

## Available Functions

- `managers_basic_data(year, verbose=False)`: Returns manager-level season records (wins/losses, games managed, replay/challenge outcomes, and postseason summary fields).
- `managers_tendencies_data(year, verbose=False)`: Returns manager tendencies (steal attempts, bunting, IBB usage, and pitching usage tendencies).

## Function Parameters

Both functions accept these parameters:

- `year` (int): MLB season year.
- `verbose` (bool): Print request diagnostics. Defaults to `False`.

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

1. Both functions use the shared BREF session, which can use a browser fallback when it detects a Cloudflare challenge.
2. Both functions return Polars DataFrames.
3. The shared session limits requests within this Python process. Baseball Reference can still block a request; a failed request raises `RuntimeError`.
4. All functions take in a `verbose` parameter that, when set to True, will print debug information during the request process. This can be useful for troubleshooting Cloudflare blocks.
