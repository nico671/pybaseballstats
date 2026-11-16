# Project guide

## Purpose and tools

`pybaseballstats` is a Python library that retrieves baseball data from Baseball Savant, Baseball Reference, Retrosheet, and Umpire Scorecards. Most functions return Polars data frames. Fangraphs is no longer supported.

The package requires Python 3.11 or later. `.python-version` selects Python 3.13 for development. Use `uv` and the committed `uv.lock` for the environment. Setuptools builds the package. Use Ruff for lint and format checks, `ty` for type checks, and pytest for tests. The `justfile` uses Fish, so install Fish to run `just` commands.

## File structure

| Path | Purpose |
| --- | --- |
| `src/pybaseballstats/` | Package code in a `src` layout. |
| Public modules, such as `statcast.py` and `bref_teams.py` | Small modules that export supported functions from private modules. |
| Private modules, such as `_statcast.py` and `_bref_teams.py` | Input checks, data retrieval, parsing, and result construction. |
| `src/pybaseballstats/statcast_leaderboards/` | Public exports in `__init__.py`; private modules grouped by leaderboard category. |
| `src/pybaseballstats/enums.py` | Public team filters. Their definitions and source mappings are in `_consts/`. |
| `src/pybaseballstats/_consts/` | Source URLs, valid values, team codes, and season dates. |
| `src/pybaseballstats/_utils/` | Shared HTTP, browser, session, parsing, and asynchronous download helpers. |
| `*.pyi` and `py.typed` in the package | Public type information included in distributions. |
| `tests/` | Offline tests and tests marked `live`. Test files use the `*_test.py` suffix. |
| `tests/fixtures/bref/` | Recorded Baseball Reference HTML and its URL index. |
| `usage_docs/` | Source-specific usage guides. |
| `docs/` | Public API migration and release notes. |
| `scripts/capture_bref_fixtures.py` | Explicit maintenance command to capture Baseball Reference fixtures. |
| `.github/workflows/`, `.githooks/`, `justfile` | CI, commit checks, and local development commands. |

Start with `README.md` for package use and `CONTRIBUTING.md` for the full contribution process. Use `pyproject.toml`, `justfile`, and workflow files to verify current commands.

## Setup and checks

Run these commands from the repository root:

```sh
uv sync --locked
git config core.hooksPath .githooks
```

The second command enables the versioned commit hook. The hook runs format, lint, type, and offline test checks.

| Command | Effect |
| --- | --- |
| `just test` | Run offline tests. Equivalent to `uv run pytest tests/`. |
| `uv run pytest tests/statcast_test.py -k chunk` | Example of a focused offline check. Select the file and cases affected by the change. |
| `just lint` | Run `uv run ruff check .`. |
| `just format-check` | Check Python formatting without changing files. |
| `just format` | Apply Ruff formatting. Check the diff for unrelated changes. |
| `just typecheck` | Run `uv run ty check`. `ty` is the current checker, even though older mypy files remain. |
| `just build` | Build package distributions with `uv build`. |
| `just smoke` | Run live tests with parallel workers and `--dist loadgroup`. |

For live tests that use a browser, first run `uv run playwright install chromium`. On Linux, use `uv run playwright install --with-deps chromium` if system dependencies are missing.

## Implementation rules

- Trace the public export, private implementation, shared helpers, tests, and usage guide before an API change. Reuse the existing helper that owns the affected behavior.
- Keep public exports, `__all__`, `__dir__`, and `.pyi` files consistent. Update API tests and usage guides when supported names or signatures change. Keep team enum imports under `pybaseballstats.enums`.
- Preserve documented result types and columns. Statcast pitch-by-pitch calls return a `LazyFrame` by default and a `DataFrame` with `force_collect=True`. Downloads occur before return. Keep temporary CSV files available for later lazy collection.
- Use `TypeError` for wrong argument types and `ValueError` for invalid values. Source or request failures inside a call use `RuntimeError`; preserve the original exception as its cause. Later lazy collection can raise a Polars error.
- Return an empty result of the documented type for a valid response with no matching rows. A failed download chunk or Retrosheet shard must fail the full request to prevent incomplete results.
- Use the shared `BREF_SESSION` for Baseball Reference requests. It applies a process-local request limit. Keep live Baseball Reference tests in the same xdist group and retain `--dist loadgroup` so parallel workers do not bypass that limit.

## Test rules

Pytest excludes `live` tests by default. `tests/conftest.py` blocks network connections in offline tests and replays recorded pages for offline Baseball Reference tests. Mock other request paths in the private module or shared helper used by the function.

Mark tests that contact external sources with `pytest.mark.live`. Use `tests/live_assertions.py` where applicable. Check required columns, identities, filters, date ranges, and unique keys. Avoid fixed live row counts because source data can change. Fixed counts can be appropriate for committed fixtures.

Capture fixtures only as an explicit maintenance task. Normal pytest execution must not retrieve or replace them. The capture script supports `--force-regen` to replace existing HTML.

Run focused tests first, then the applicable project checks. Report exactly what ran. An offline pass does not verify current source availability; a local pass does not verify GitHub Actions. For documentation-only changes, inspect the content and run `git diff --check`.

## Branches and releases

Start feature branches from `dev` and target `dev` with contribution pull requests. `main` is the release branch. The maintainer release process uses a pull request from `dev` to `main`.

CI runs offline tests, Ruff checks, and type checks for applicable changes. Scheduled live tests check both `dev` and `main`; they do not block contribution pull requests. Releases require live tests.

Do not run `just release` without explicit release authorization. It updates the lockfile, runs checks, builds, commits, tags, and pushes. A pushed `v*` tag starts the workflow that publishes to PyPI and creates a GitHub release. Obtain explicit user authorization before commits, pushes, or publication.
