import os
import sys

import pandas as pd
import polars as pl
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pybaseballstats as pyb


def test_fangraphs_batting_range():
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
    )
    assert data is not None
    assert data.shape[0] == 129
    assert data.shape[1] == 244
    assert type(data) is pl.DataFrame
    data = pyb.fangraphs_batting_range(
        start_date="2024-04-01",
        end_date="2024-05-01",
        stat_types=None,
        return_pandas=True,
        pos="all",
        league="",
        min_at_bats="y",
        start_season=None,
        end_season=None,
    )
    assert data is not None
    assert data.shape[0] == 129
    assert data.shape[1] == 244
    assert type(data) is pd.DataFrame


def test_fangraphs_batting_range_bad_inputs():
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-05-01",
            end_date="2024-04-01",
            stat_types=None,
            return_pandas=False,
            pos="all",
            league="",
            min_at_bats="y",
            start_season=None,
            end_season=None,
        )
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date=None,
            end_date=None,
            stat_types=None,
            return_pandas=False,
            pos="all",
            league="",
            min_at_bats="y",
            start_season=None,
            end_season=None,
        )
    # empty list for stat_types
    with pytest.raises(ValueError):
        pyb.fangraphs_batting_range(
            start_date="2024-04-01",
            end_date="2024-05-01",
            stat_types=[],
            return_pandas=False,
            pos="all",
            league="",
            min_at_bats="y",
            start_season=None,
            end_season=None,
        )


def test_fangraphs_batting_range_yes_and_no_qual():
    data1 = pyb.fangraphs_batting_range(
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
    data2 = pyb.fangraphs_batting_range(
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
    assert data1 is not None
    assert data2 is not None
    assert data1.shape[0] < data2.shape[0]
    assert data1.shape[1] == data2.shape[1]


# # # print(pyb.show_fangraphs_batting_stat_types())
# # # print(pyb.show_batting_pos_options())
# # #     # stat type
# # #     stat_types[stat_type],
# # #     # position
# # #     "all",
# # #     # league
# # #     "",
# # #     # start date
# # #     "2024-04-01",
# # #     # end date
# # #     "2024-05-01",
# # #     # qual
# # #     "y",
# # #     # start season
# # #     "",
# # #     # end season
# # #     "",
# # data = pyb.fangraphs_batting_range(
# #     start_date="2024-04-01",
# #     end_date="2024-05-01",
# #     stat_types=None,
# #     return_pandas=False,
# #     pos="all",
# #     league="",
# #     min_at_bats="y",
# #     start_season=None,
# #     end_season=None,
# # )
