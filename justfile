set shell := ["fish"]

default:
    #!/usr/bin/env fish
    just --list

mypy:
    #!/usr/bin/env fish
    echo "Running mypy type checking..."
    uv run mypy src/pybaseballstats tests/
    if test $status -eq 0
        echo "Mypy type checking passed!"
    else
        echo "Mypy type checking failed!"
        exit 1
    end

set dotenv-load := true

release version:
    #!/usr/bin/env fish
    echo "Starting release process for version {{ version }}..."
    echo "Step 1: Running mypy type checking..."
    just mypy
    if test $status -ne 0
        echo "Release aborted: mypy type checking failed!"
        exit 1
    end
    echo "Step 2: Running tests..."
    just test
    if test $status -ne 0
        echo "Release aborted: tests failed!"
        exit 1
    end
    echo "Step 3: Committing changes..."
    git add .
    git commit -m "Bump version to {{ version }}"
    if test $status -ne 0
        echo "Note: No changes to commit or commit failed"
    end
    echo "Step 4: Creating and pushing tag..."
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
    echo "Step 5: Building package..."
    uv build
    if test $status -ne 0
        echo "Release aborted: build failed!"
        exit 1
    end
    echo "Step 6: Publishing to PyPI..."
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
    uv run coverage run --source=src/pybaseballstats -m pytest tests/
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
