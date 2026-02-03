#!/usr/bin/env fish
# filepath: /Users/nicocarbone/Documents/dev/pybaseballstats/run_coverage.fish

# Clear previous coverage data
echo "Cleaning up previous coverage data..."
rm -f .coverage
rm -f .github/coverage/coverage.json

# Ensure the coverage directory exists
mkdir -p .github/coverage

# Run coverage with tests
echo "Running tests with coverage..."
uv run coverage run --source=src/pybaseballstats -m pytest tests/

# Check if tests passed
if test $status -eq 0
    echo "Tests passed! Generating coverage report..."
    
    # Generate coverage report to terminal
    echo "Coverage report:"
    uv run coverage report -m
    
    # Generate JSON coverage report
    echo "Generating JSON coverage report..."
    uv run coverage json -o .github/coverage/coverage.json
    
    echo "Coverage analysis complete!"
    echo "JSON report saved to: .github/coverage/coverage.json"
else
    echo "Tests failed! Coverage report not generated."
    exit 1
end

