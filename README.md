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

Improvements and bug fixes are welcome! This project follows a branch-based development workflow to keep releases stable and active development fast.

> [!NOTE]
> Currently, the development workflow is set up for Unix based systems. If you are developing on Windows, please use WSL or Docker to ensure compatibility with the development workflow. I am working on making the development workflow more cross-platform compatible, but for now I recommend using a Unix based environment for development.

### 1. Branching Strategy

We use a standard two-branch workflow:

- `main` (**release branch**)  
    Heavily protected and contains only code that is currently live on PyPI. Do **not** push or open pull requests directly against `main`.
- `dev` (**active development branch**)  
    This is the default branch. All ongoing development, experiments, and bug fixes happen here.
- **Feature branches**  
    Start new work from `dev` (for example: `feature/your-feature-name`).

### 2. Local Development & Committing

The default test suite is offline. Network responses are replayed from committed
fixtures, so local development and pull-request checks do not depend on external
websites:

```bash
just test
```

Live smoke tests use the `live` pytest mark. They fetch one representative
response for each distinct page or API contract and validate every table exposed
by that response. They run nightly and are required before a release, but they
do not block pull requests. Run them manually with:

```bash
just smoke
```

The smoke suite uses pytest-xdist to run independent live endpoint tests in parallel. All Baseball-Reference page tests are assigned to the same xdist worker so their shared session can enforce BREF's rate limit; keep `--dist loadgroup` when invoking the suite directly.

Run static checks before a commit with:

```bash
just lint
just mypy
```

Baseball Reference fixtures can be refreshed explicitly with
`uv run python scripts/capture_bref_fixtures.py`. Fixture capture is never part of
normal pytest execution.

Once the relevant offline tests pass, commit your changes with a descriptive message:

```bashbash
git add .
git commit -m "Add new feature/fix bug in bref module"
```

### 3. Submitting Your Changes

Once your feature or bug fix is complete and tested locally:

1. Open a pull request from your feature branch into `dev`.
2. GitHub Actions automatically runs CI (unit tests + `mypy`).
3. After checks pass and review is complete, your changes are merged into `dev`.

### 4. Release Pipeline (Maintainers Only)

Releases are automated for security and stability:

1. Open a pull request from `dev` to `main`.
2. Branch protections ensure nothing enters `main` unless all required checks pass.
3. After merge, run:

```bash
just release <version> "Release message"
```

This performs final validation, tags the release, and pushes it.

A GitHub Action then builds the `uv` package and deploys to PyPI using Trusted Publishers (tokenless publishing).

## Credit and Acknowledgement

This project was directly inspired by the pybaseball package by James LeDoux. The goal of this project is to provide a similar set of functionality with continual updates and improvements, as the original pybaseball package has lagged behind with updates and some key functionality has been broken.

All of the data scraped by this package is publicly available and free to use. All credit for the data goes to the organizations from which it was scraped.
