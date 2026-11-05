"""Checks for live data whose values can change upstream."""

from datetime import date

import polars as pl


def assert_numeric(series, *, minimum=None, maximum=None, count=False):
    assert series.dtype.is_numeric(), (
        f"{series.name}: expected numeric type, got {series.dtype}"
    )
    if count:
        assert series.dtype.is_integer(), f"{series.name}: expected integer counts"
        assert series.null_count() == 0, f"{series.name}: null counts"
    values = series.drop_nulls()
    assert len(values) > 0, f"{series.name}: no numeric values"
    assert values.is_finite().all(), f"{series.name}: non-finite values"
    if minimum is not None:
        assert (values >= minimum).all(), f"{series.name}: values below {minimum}"
    if maximum is not None:
        assert (values <= maximum).all(), f"{series.name}: values above {maximum}"


def assert_live_frame(df, *, columns=(), numeric=(), counts=(), unique_by=()):
    assert isinstance(df, pl.DataFrame)
    assert not df.is_empty(), "Expected live data"
    required = set(columns) | set(numeric) | set(counts) | set(unique_by)
    assert required <= set(df.columns), f"Missing columns: {required - set(df.columns)}"
    for name in numeric:
        assert_numeric(df[name])
    for name in counts:
        assert_numeric(df[name], minimum=0, count=True)
    if unique_by:
        keys = df.select(list(unique_by))
        assert keys.null_count().row(0) == (0,) * len(unique_by), (
            f"Null grouping keys: {unique_by}"
        )
        assert keys.unique().height == df.height, (
            f"Duplicate grouping keys: {unique_by}"
        )


def assert_date_range(series, start, end):
    assert series.null_count() == 0, f"{series.name}: null dates"
    dates = series.str.to_date() if series.dtype == pl.String else series
    assert dates.dtype == pl.Date, f"{series.name}: expected dates"
    assert dates.is_between(date.fromisoformat(start), date.fromisoformat(end)).all()
