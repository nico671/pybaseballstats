import datetime as dt

from hypothesis import given
from hypothesis import strategies as st

from src.pybaseballstats.utils.statcast_utils import _create_date_ranges, _handle_dates


# _handle_dates
@given(
    st.dates(min_value=dt.date(2015, 4, 5), max_value=dt.date(2025, 10, 25)),
    st.dates(min_value=dt.date(2015, 4, 5), max_value=dt.date(2025, 10, 25)),
)
def test_handle_dates(start_dt, end_dt):
    start_dt_str = start_dt.strftime("%Y-%m-%d")
    end_dt_str = end_dt.strftime("%Y-%m-%d")
    try:
        start, end = _handle_dates(start_dt_str, end_dt_str)
        assert start <= end
    except ValueError:
        assert start_dt > end_dt


# _create_date_ranges
@given(
    st.dates(min_value=dt.date(2015, 4, 5), max_value=dt.date(2025, 10, 25)),
    st.dates(min_value=dt.date(2015, 4, 5), max_value=dt.date(2025, 10, 25)),
    st.integers(min_value=1, max_value=30),
)
def test_create_date_ranges(start_dt, end_dt, days):
    date_ranges = list(_create_date_ranges(start_dt, end_dt, days))
    if start_dt > end_dt:
        assert len(date_ranges) == 0
    else:
        # assert len(date_ranges) > 0
        for date_range in date_ranges:
            assert len(date_range) == 2
            assert date_range[0] <= date_range[1]
