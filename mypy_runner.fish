# run mypy type checking
echo "Running mypy type checking..."
uv run mypy src/pybaseballstats tests/
if test $status -eq 0
    echo "Mypy type checking passed!"
else
    echo "Mypy type checking failed!"
    exit 1
end