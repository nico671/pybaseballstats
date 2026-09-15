# Contributing

Improvements and bug fixes are welcome! This project follows a branch-based development workflow to keep releases stable and active development fast.

> [!NOTE]
> Currently, the development workflow is set up for Unix based systems. If you are developing on Windows, please use WSL or Docker to ensure compatibility with the development workflow. I am working on making the development workflow more cross-platform compatible, but for now I recommend using a Unix based environment for development.

## 1. Branching Strategy

We use a standard two-branch workflow:

- `main` (**release branch**)  
    Heavily protected and contains only code that is currently live on PyPI. Do **not** push or open pull requests directly against `main`.
- `dev` (**active development branch**)  
    This is the default branch. All ongoing development, experiments, and bug fixes happen here.
- **Feature branches**  
    Start new work from `dev` (for example: `feature/your-feature-name`).

## 2. Local Development & Committing

Create the locked project environment before opening the repository in an editor:

```bash
uv sync --locked
```

VS Code discovers the workspace `.venv` automatically. If it does not, run
**Python: Select Interpreter** and select the workspace environment.

The default test suite is offline. Network responses are replayed from committed
fixtures, so local development and pull-request checks do not depend on external
websites:

```bash
just test
```

Live smoke tests require Playwright's Chromium browser. Install it once after
setting up the development environment:

```bash
uv run playwright install chromium
```

On Linux, use the following command if system dependencies are also missing:

```bash
uv run playwright install --with-deps chromium
```

Live smoke tests use the `live` pytest mark. They fetch one representative
response for each distinct page or API contract and validate every table exposed
by that response. They run nightly and are required before a release, but they do
not block pull requests. Run them manually with:

```bash
just smoke
```

The smoke suite uses pytest-xdist to run independent live endpoint tests in parallel. All Baseball-Reference page tests are assigned to the same xdist worker so their shared session can enforce BREF's rate limit; keep `--dist loadgroup` when invoking the suite directly.

Run static checks before a commit with:

```bash
just format
just lint
just mypy
```

Git runs these checks and the offline test suite before every commit. Enable
the versioned hook once in each clone:

```bash
git config core.hooksPath .githooks
```

Baseball Reference fixtures can be refreshed explicitly with
`uv run python scripts/capture_bref_fixtures.py`. Fixture capture is never part of
normal pytest execution.

Once the relevant offline tests pass, commit your changes with a descriptive message:

```bash
git add .
git commit -m "Add new feature/fix bug in bref module"
```

## 3. Submitting Your Changes

Once your feature or bug fix is complete and tested locally:

1. Open a pull request from your feature branch into `dev`.
2. GitHub Actions automatically runs CI (unit tests + `mypy`).
3. After checks pass and review is complete, your changes are merged into `dev`.

## 4. Release Pipeline (Maintainers Only)

Releases are automated for security and stability:

1. Open a pull request from `dev` to `main`.
2. Branch protections ensure nothing enters `main` unless all required checks pass.
3. After merge, run:

```bash
just release <version> "Release message"
```

This performs final validation, tags the release, and pushes it.

A GitHub Action then builds the `uv` package and deploys to PyPI using Trusted Publishers (tokenless publishing).
