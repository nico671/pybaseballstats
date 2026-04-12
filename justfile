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

build:
    uv build

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

    echo "Committing and pushing changes..."
    git add .
    git commit -m "{{ message }}"
    if test $status -ne 0
        echo "Commit aborted: no changes to commit or commit failed."
        exit 1
    end

    git push origin HEAD
    if test $status -ne 0
        echo "Commit failed: push was unsuccessful."
        exit 1
    end
    echo "Commit and push complete!"

release version commit_message:
    #!/usr/bin/env fish
    echo "Starting release prep for pybaseballstats v{{ version }}..."
    
    set current_branch (git branch --show-current)
    if test "$current_branch" != "main"
        echo "Release aborted: You must be on the 'main' branch to cut a release."
        exit 1
    end

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
    
    echo "Step 4: Committing version bump..."
    git add pyproject.toml
    git commit -m "Bump version to {{ version }}; Message: {{ commit_message }}"
    
    echo "Step 5: Creating and pushing tag..."
    git tag -a v{{ version }} -m "Release version {{ version }}"
    
    git push origin main
    if test $status -ne 0
        echo "Release aborted: push to main failed!"
        exit 1
    end
    
    git push origin v{{ version }}
    if test $status -ne 0
        echo "Release aborted: push tag failed!"
        exit 1
    end
    
    echo "Release v{{ version }} pushed! GitHub Actions will now build and publish to PyPI."