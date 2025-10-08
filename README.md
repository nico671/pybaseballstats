# pybaseballstats

A Python package for scraping baseball statistics from the web. Inspired by the pybaseball package by James LeDoux.

---

[![PyPI Downloads](https://static.pepy.tech/badge/pybaseballstats)](https://pepy.tech/projects/pybaseballstats)

![Coverage](https://github.com/nico671/pybaseballstats/blob/coverage-badge/badges/coverage.svg)

---

## Available Sources

1. [Baseball Savant](https://baseballsavant.mlb.com/)
    - This source provides high quality pitch-by-pitch data for all MLB games since 2015 as well as interesting leaderboards for various categories.
2. [Fangraphs](https://www.fangraphs.com/)
    - This source provides leaderboards for pitching, batting and fielding statistics for all MLB players since 1871.
3. [Umpire Scorecards](https://umpscorecards.com/home/)
    - This source provides umpire game logs and statistics for all MLB games since 2008.
4. [Baseball Reference](https://www.baseball-reference.com/)
    - This source provides comprehensive, high detail stats for all MLB players and teams since 1871.
5. [Retrosheet](https://retrosheet.org/)
    - This source provides play-by-play data for all MLB games since 1871. This data is primarily used for the player_lookup function as well as ejection data. I am considering adding support for the play by play data as well.

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

Improvements and bug fixes are welcome! Please open an issue or submit a pull request. If you are opening an issue please keep in mind that I am enrolled in university full-time and may not be able to respond immediately. I work on this in my free time, but I will do my best to fix any issues that are opened. To submit a pull request, please fork the repository and make your changes on a new branch. Make your changes and please create new tests if you are adding new functionality (updates to my own tests are more than welcome as well). Make sure all tests pass and once you are finished, submit a pull request and I will review your changes. Please include a detailed description of the changes you made and why you made them as a part of your pull request.

## Credit and Acknowledgement

This project was directly inspired by the pybaseball package by James LeDoux. The goal of this project is to provide a similar set of functionality with continual updates and improvements, as the original pybaseball package has lagged behind with updates and some key functionality has been broken.

All of the data scraped by this package is publicly available and free to use. All credit for the data goes to the organizations from which it was scraped.
