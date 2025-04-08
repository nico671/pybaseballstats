# pybaseballstats

A Python package for scraping baseball statistics from the web. Inspired by the pybaseball package by James LeDoux.

## Available Sources

1. [Baseball Savant](https://baseballsavant.mlb.com/)
    - This source provides high quality pitch-by-pitch data for all MLB games since 2015 as well as interesting leaderboards for various categories.
2. [Fangraphs](https://www.fangraphs.com/)
    - This source provides leaderboards for pitching, batting and fielding statistics for all MLB players since 1871.
3. [Umpire Scorecard](https://umpscorecards.com/home/)
    - This source provides umpire game logs and statistics for all MLB games since 2008.
4. [Baseball Reference](https://www.baseball-reference.com/)
    - This source is currently only used for draft order data but usage will expand to more interesting statistics they have available in the future.
5. [Retrosheet](https://retrosheet.org/)
    - This source provides play-by-play data for all MLB games since 1871. This data is primarily used for the player_lookup function as well as ejection data. I am considering adding support for the play by play data as well.

## Installation

pybaseballstats can be installed using pip or any other package manager (I use [uv](https://docs.astral.sh/uv/)).

Examples:

```bash
pip install pybaseballstats
```

or:

```bash
uv add pybaseballstats
```

## Documentation

Usage documentation can be found in this [folder](usage_docs/). This documentation is a work in progress and will be updated as I add more functionality to the package.

## Contributing

Improvements and bug fixes are welcome! Please open an issue or submit a pull request. If you are opening an issue please keep in mind that I am enrolled in university full-time and may not be able to respond immediately. I work on this in my free time, but I will do my best to fix any issues that are opened. To submit a pull request, please fork the repository and make your changes on a new branch. Make your changes and please create new tests if you are adding new functionality (updates to my own tests are more than welcome as well). Make sure all tests pass and once you are finished, submit a pull request and I will review your changes. Please include a detailed description of the changes you made and why you made them as a part of your pull request.

## Credit and Acknowledgement

This project was heavily inspired by the pybaseball package by James LeDoux. The goal of this project is to provide a similar set of functionality with continual updates and improvements, as the original pybaseball package has lagged behind with updates and key functionality has been broken (hence my decision to create this new package).

All of the data scraped by this package is publicly available and free to use. All credit for the data goes to the organizations from which it was scraped.
