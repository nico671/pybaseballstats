set shell := ["fish"]

default:
    #!/usr/bin/env fish
    just --list

mypy:
    #!/usr/bin/env fish
    echo "Running mypy type checking..."
    uv run mypy src/pybaseballstats/ --check-untyped-defs
    if test $status -eq 0
        echo "Mypy type checking passed!"
    else
        echo "Mypy type checking failed!"
        exit 1
    end

set dotenv-load := true

release version commit_message:
    #!/usr/bin/env fish
    echo "Starting release process for pybaseballstats v{{ version }}..."
    echo "Step 1: Validating release version..."
    if not test -f pyproject.toml
        echo "Release aborted: pyproject.toml was not found!"
        exit 1
    end
    set pyproject_version (awk -F '"' '/^version = "/ { print $2; exit }' pyproject.toml)
    if test -z "$pyproject_version"
        echo "Release aborted: unable to read version from pyproject.toml"
        exit 1
    end
    if test "$pyproject_version" != "{{ version }}"
        echo "Release aborted: pyproject.toml version ($pyproject_version) does not match release version ({{ version }})"
        exit 1
    end
    mkdir -p dist
    set existing_release_artifacts (find dist -maxdepth 1 -type f -name "pybaseballstats-{{ version }}*")
    if test (count $existing_release_artifacts) -gt 0
        echo "Release aborted: dist already contains artifacts for version {{ version }}"
        printf '%s\n' $existing_release_artifacts
        exit 1
    end
    echo "Step 2: Running mypy type checking..."
    just mypy
    if test $status -ne 0
        echo "Release aborted: mypy type checking failed!"
        exit 1
    end
    echo "Step 3: Running tests..."
    just test
    if test $status -ne 0
        echo "Release aborted: tests failed!"
        exit 1
    end
    echo "Step 4: Committing changes..."
    git add .
    git commit -m "Bump version to {{ version }}; Message: {{ commit_message }}"
    if test $status -ne 0
        echo "Note: No changes to commit or commit failed"
    end
    echo "Step 5: Creating and pushing tag..."
    git tag -a v{{ version }} -m "Release version {{ version }}"
    if test $status -ne 0
        echo "Release aborted: tag creation failed!"
        exit 1
    end
    git push origin main
    git push origin v{{ version }}
    if test $status -ne 0
        echo "Release aborted: push failed!"
        exit 1
    end
    echo "Step 6: Building package..."
    uv build
    if test $status -ne 0
        echo "Release aborted: build failed!"
        exit 1
    end
    echo "Step 7: Publishing to PyPI..."
    uv publish --token $PYPI_TOKEN
    if test $status -eq 0
        echo "Release v{{ version }} complete!"
    else
        echo "Release failed: publish failed!"
        exit 1
    end 

build:
    uv build

publish:
    uv publish --token $PYPI_TOKEN

test:
    #!/usr/bin/env fish
    echo "Cleaning up previous coverage data..."
    rm -f .coverage
    rm -f .github/coverage/coverage.json
    echo "Ensuring the coverage directory exists..."
    mkdir -p .github/coverage
    echo "Running tests with coverage..."
    uv run coverage run -m pytest tests/
    if test $status -eq 0
        echo "Tests passed! Generating coverage report..."
        echo "Coverage report:"
        uv run coverage report -m
        echo "Generating JSON coverage report..."
        uv run coverage json -o .github/coverage/coverage.json
        echo "Coverage analysis complete!"
        echo "JSON report saved to: .github/coverage/coverage.json"
    else
        echo "Tests failed! Coverage report not generated."
        exit 1
    end

commit message:
    #!/usr/bin/env fish
    echo "Running mypy checks before commit..."
    just mypy
    if test $status -ne 0
        echo "Commit aborted: mypy checks failed."
        exit 1
    end

    echo "Running unit tests before commit..."
    just test
    if test $status -ne 0
        echo "Commit aborted: tests failed."
        exit 1
    end

    echo "Generating local status badges..."
    mkdir -p badges

    set coverage_percent (uv run python -c "import json; from pathlib import Path; print(round(json.loads(Path('.github/coverage/coverage.json').read_text())['totals']['percent_covered']))")
    if test -z "$coverage_percent"
        echo "Commit aborted: unable to compute coverage percent."
        exit 1
    end

    set coverage_color red
    if test $coverage_percent -ge 80
        set coverage_color brightgreen
    else if test $coverage_percent -ge 60
        set coverage_color yellow
    end

    curl -fsSL -o badges/coverage.svg "https://img.shields.io/badge/coverage-$coverage_percent%25-$coverage_color"
    if test $status -ne 0
        echo "Commit aborted: failed to generate coverage badge."
        exit 1
    end

    curl -fsSL -o badges/pytest.svg "https://img.shields.io/badge/pytest-passing-brightgreen"
    if test $status -ne 0
        echo "Commit aborted: failed to generate pytest badge."
        exit 1
    end

    curl -fsSL -o badges/mypy.svg "https://img.shields.io/badge/mypy-passing-brightgreen"
    if test $status -ne 0
        echo "Commit aborted: failed to generate mypy badge."
        exit 1
    end

    echo "Committing and pushing changes..."
    git add .
    git commit -m "{{ message }}"
    if test $status -ne 0
        echo "Commit aborted: no changes to commit or commit failed."
        exit 1
    end

    git push origin main
    if test $status -ne 0
        echo "Commit failed: push to origin/main was unsuccessful."
        exit 1
    end

    echo "Commit and push complete with fresh local badges."
