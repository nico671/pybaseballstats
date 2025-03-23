# import polars as pl
# import pytest
# from polars.testing import assert_frame_equal

# import pybaseballstats as pyb


# def test_draft_order_by_round_badinputs():
#     with pytest.raises(ValueError):
#         pyb.draft_order_by_round(year=1964, draft_round=1)
#     with pytest.raises(ValueError):
#         pyb.draft_order_by_round(year=1965, draft_round=0)
#     with pytest.raises(ValueError):
#         pyb.draft_order_by_round(year=1965, draft_round=61)


# def test_draft_order_by_round_regular():
#     df = pyb.draft_order_by_round(year=2024, draft_round=1)
#     assert df.shape[0] == 39
#     assert df.shape[1] == 23
#     assert df.select(pl.col("year_ID").n_unique()).item() == 1
#     assert df.select(pl.col("draft_round").n_unique()).item() == 1
#     assert df.select(pl.col("overall_pick").n_unique()).item() == df.shape[0]
#     assert df.select(pl.col("round_pick").n_unique()).item() == df.shape[0]
#     assert df.select(pl.col("player").n_unique()).item() == df.shape[0]
#     df2 = pyb.draft_order_by_round(2024, 1, return_pandas=True)
#     assert df2.shape[0] == df.shape[0]
#     assert df2.shape[1] == df.shape[1]
#     assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))


# def test_franchise_draft_order_badinputs():
#     with pytest.raises(ValueError):
#         pyb.franchise_draft_order(year=1964, team="ATL")
#     with pytest.raises(ValueError):
#         pyb.franchise_draft_order(year=1965, team="FAKE")


# def test_franchise_draft_order_regular():
#     df = pyb.franchise_draft_order(year=2024, team="WSN")
#     assert df.shape[0] == 21
#     assert df.shape[1] == 23
#     assert df.select(pl.col("year_ID").n_unique()).item() == 1
#     assert df.select(pl.col("team_ID").n_unique()).item() == 1
#     assert df.select(pl.col("overall_pick").n_unique()).item() == df.shape[0]
#     assert (
#         df.filter(pl.col("signed") == "N").select(pl.col("bonus").n_unique()).item()
#         == 1
#     )
#     df2 = pyb.franchise_draft_order(year=2024, team="WSN", return_pandas=True)
#     assert df2.shape[0] == 21
#     assert df2.shape[1] == 23
#     assert_frame_equal(df, pl.DataFrame(df2, schema=df.schema))
