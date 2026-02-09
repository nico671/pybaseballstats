default:
    @just --list

set shell := ["fish"]

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

release:
    uv build && uv publish --token $PYPI_TOKEN 

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
