# pybaseballstats

A Python package for scraping baseball statistics from the web. Inspired by the pybaseball package by James LeDoux.

---

[![PyPI Downloads](https://static.pepy.tech/badge/pybaseballstats)](https://pepy.tech/projects/pybaseballstats)  ![Pytest Status](https://github.com/nico671/pybaseballstats/actions/workflows/run_unit_tests.yml/badge.svg)  ![Mypy Status](https://github.com/nico671/pybaseballstats/actions/workflows/run_mypy.yml/badge.svg)

---

## Available Sources

1. [Baseball Savant](https://baseballsavant.mlb.com/)
    - This source provides high quality pitch-by-pitch data for all MLB games since 2015, grouped single-player season summaries, and interesting leaderboards for various categories.
2. [Umpire Scorecards](https://umpscorecards.com/home/)
    - This source provides umpire game logs and statistics for all MLB games since 2008.
3. [Baseball Reference](https://www.baseball-reference.com/)
    - This source provides comprehensive, high detail stats for all MLB players and teams since 1871.
4. [Retrosheet](https://retrosheet.org/)
    - This source provides play-by-play data for all MLB games since 1871. This data is primarily used for the player_lookup function as well as ejection data. I am considering adding support for the play by play data as well.

> [!NOTE]
> Although past versions had support for Fangraphs, I have decided to remove support for this source as they have recently implemented very aggressive anti-scraping measures that have made it very difficult to scrape data from their site. I may consider adding support for this source again in the future if they change their anti-scraping measures, but for now I have decided to focus on the other sources that are more reliable and easier to scrape data from.

**Temporary Baseball Reference outage (hotfix):** As of the latest hotfix release, Baseball Reference-backed modules are temporarily disabled due to upstream Cloudflare anti-crawling protections. This was done to avoid flaky behavior and hard-to-diagnose failures while a robust workaround is investigated. Other data sources (Baseball Savant, Umpire Scorecards, Retrosheet) remain available.

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

### General Documentation (Things of Note)

1. This project uses Polars internally. This means that all data returned from functions in this package will be in the form of a Polars DataFrame. If you want to convert the data to a Pandas DataFrame, you can do so by using the `.to_pandas()` method on the Polars DataFrame. For example:
2. The BREF functions use a singleton pattern to guarantee that you won't exceed rate limits and face a longer timeout. So: don't be surprised if when you are making multiple calls to BREF functions that these calls may be a little slower than expected. This is to be expected as the singleton pattern is used to ensure that only one instance of the BREF scraper is created and used throughout the lifetime of your program. This is done to avoid exceeding rate limits and being blocked by BREF.

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
