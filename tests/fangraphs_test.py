import os
import sys

import pandas as pd
import polars as pl
import pytest

# Setup path to import pybaseballstats
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb


# Basic functionality tests for fangraphs_batting_range
def test_fangraphs_batting_range_output():
    # Test with Polars and Pandas output
    for return_pandas, df_type in [(False, pl.DataFrame), (True, pd.DataFrame)]:
        data = pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=None,
            return_pandas=return_pandas,
            pos="all",
            league="",
            min_at_bats="y",
            start_season=None,
            end_season=None,
        )
        assert data is not None
        assert data.shape[0] == 129
        assert data.shape[1] == 313
        assert isinstance(data, df_type)


# Test invalid inputs trigger ValueErrors
@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            start_date="2024-05-01",
            end_date="2024-04-01",
            stat_types=None,
            return_pandas=False,
            pos="all",
            league="",
            min_at_bats="y",
            start_season=None,
            end_season=None,
        ),
        dict(
            start_date=None,
            end_date=None,
            stat_types=None,
            return_pandas=False,
            pos="all",
            league="",
            min_at_bats="y",
            start_season=None,
            end_season=None,
        ),
        dict(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=[],
            return_pandas=False,
            pos="all",
            league="",
            min_at_bats="y",
            start_season=None,
            end_season=None,
        ),
    ],
)
def test_invalid_batting_range_inputs(kwargs):
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(**kwargs)


# Compare qualified vs. unqualified minimum at bats
def test_qual_vs_non_qual():
    data_qual = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        pos="all",
        league="",
        min_at_bats="y",
        start_season=None,
        end_season=None,
    )
    data_non_qual = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        pos="all",
        league="",
        min_at_bats="50",
        start_season=None,
        end_season=None,
    )
    assert data_qual is not None
    assert data_non_qual is not None
    # Typically, the qualified dataset is a subset
    assert data_qual.shape[0] < data_non_qual.shape[0]
    assert data_qual.shape[1] == data_non_qual.shape[1]


# # Test age input validation and output shape
# def test_age_inputs():
#     with pytest.raises(ValueError):
#         pyb.fangraphs_batting_range(
#             start_date="2024-04-01",
#             end_date="2024-05-01",
#             stat_types=None,
#             return_pandas=False,
#             pos="all",
#             league="",
#             min_at_bats="y",
#             start_season=20,
#             end_season=None,
#             start_age=20,
#         )
#     with pytest.raises(ValueError):
#         pyb.fangraphs_batting_range(
#             start_date="2024-04-01",
#             end_date="2024-05-01",
#             stat_types=None,
#             return_pandas=False,
#             pos="all",
#             league="",
#             min_at_bats="y",
#             start_season=20,
#             end_season=None,
#             start_age=24,
#             end_age=20,
#         )
#     data = pyb.fangraphs_batting_range(
#         start_date=None,
#         end_date=None,
#         stat_types=None,
#         return_pandas=False,
#         pos="all",
#         league="",
#         min_at_bats="y",
#         start_season=2024,
#         end_season=2024,
#         start_age=20,
#         end_age=24,
#         handedness="",
#         rost=0,
#     )
#     assert data is not None
#     assert data.shape[0] == 118
#     assert data.shape[1] == 313


# Test handedness filtering using parameterization
@pytest.mark.parametrize(
    "handedness,expected_rows",
    [
        ("R", 71),
        ("L", 44),
        ("S", 14),
    ],
)
def test_handedness_filter(handedness, expected_rows):
    data = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        pos="all",
        league="",
        min_at_bats="y",
        start_season=None,
        end_season=None,
        handedness=handedness,
    )
    assert data is not None
    assert data.shape[0] == expected_rows
    assert data.shape[1] == 313


def test_active_roster_filter():
    data = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=False,
        pos="all",
        league="",
        min_at_bats="y",
        start_season=None,
        end_season=None,
        rost=1,
    )
    assert data is not None
    assert data.shape[0] > 0
    assert isinstance(data, pl.DataFrame)


# ...additional tests can be added as needed...
