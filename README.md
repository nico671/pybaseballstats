# pybaseballstats

A Python package for scraping baseball statistics from the web. Inspired by the pybaseball package by James LeDoux.

---

[![PyPI Downloads](https://static.pepy.tech/badge/pybaseballstats)](https://pepy.tech/projects/pybaseballstats)  ![Pytest Status](https://github.com/nico671/pybaseballstats/actions/workflows/run_unit_tests.yml/badge.svg)  ![Type Check Status](https://github.com/nico671/pybaseballstats/actions/workflows/run_type_checks.yml/badge.svg)

---

## Available Sources

1. [Baseball Savant](https://baseballsavant.mlb.com/)
    - This source provides high quality pitch-by-pitch data for all MLB games since 2015, grouped single-player season summaries, and interesting leaderboards for various categories.
2. [Umpire Scorecards](https://umpscorecards.com/home/)
    - This source has umpire game logs that start in 2008. This package accepts date ranges from 2015 onward.
3. [Baseball Reference](https://www.baseball-reference.com/)
    - This source provides comprehensive, high detail stats for all MLB players and teams since 1871.
4. [Retrosheet](https://retrosheet.org/)
    - This source provides play-by-play data for all MLB games since 1871. This data is primarily used for the player_lookup function as well as ejection data. I am considering adding support for the play by play data as well.

> [!NOTE]
> Although past versions had support for Fangraphs, I have decided to remove support for this source as they have recently implemented very aggressive anti-scraping measures that have made it very difficult to scrape data from their site. I may consider adding support for this source again in the future if they change their anti-scraping measures, but for now I have decided to focus on the other sources that are more reliable and easier to scrape data from.

## Installation

pybaseballstats can be installed using pip or any other package manager (I use [uv](https://docs.astral.sh/uv/)).

Examples:

```bash
uv add pybaseballstats
```

or:

```bash
pip install pybaseballstats
```

Some functions use Playwright and require its Chromium browser. Install it
after installing `pybaseballstats`:

```bash
# uv
uv run playwright install chromium

# pip or another Python environment
python -m playwright install chromium
```

On Linux, use `--with-deps` if the required system dependencies are missing:

```bash
python -m playwright install --with-deps chromium
```

## Documentation

Usage documentation can be found in this [folder](usage_docs/). This documentation is a work in progress and will be updated as I add more functionality to the package.
For changes to enum imports, empty results, and errors, see the [public API migration guide](docs/public-api-migration.md).

### General Documentation (Things of Note)

Use `from pybaseballstats import statcast as sc` for a source module and
`from pybaseballstats.enums import StatcastTeams` for its team filter. The same
source modules also support qualified imports and direct function imports.
Modules with an initial underscore are private implementation details.

Most functions return a Polars `DataFrame`. Statcast pitch-by-pitch functions
return a `LazyFrame` by default; call `.collect()` to get a `DataFrame`, or pass
`force_collect=True`. A valid response with no matching rows returns an empty
result of the documented type. Wrong argument types raise `TypeError`; invalid
values raise `ValueError`; request and source-data failures inside a call raise
`RuntimeError`. A lazy query can raise a Polars error later at `.collect()`.

Baseball Reference functions use a shared session and a process-local request
limiter. The source can still block requests. A failed request raises an error.
The package does not verify that every upstream page is available now.

To convert an eager Polars `DataFrame` to pandas, call `.to_pandas()`:

```python
import pybaseballstats.umpire_scorecards as us
df_polars = us.game_data(start_date="2023-04-01", end_date="2023-04-30")
# Convert to Pandas DataFrame
df_pandas = df_polars.to_pandas()
```

## Contributing

See the [contributing guide](contributing.md) for development setup, testing,
branching, pull requests, and release instructions.

## Credit and Acknowledgement

This project was directly inspired by the pybaseball package by James LeDoux. The goal of this project is to provide a similar set of functionality with continual updates and improvements, as the original pybaseball package has lagged behind with updates and some key functionality has been broken.

All of the data scraped by this package is publicly available and free to use. All credit for the data goes to the organizations from which it was scraped.
