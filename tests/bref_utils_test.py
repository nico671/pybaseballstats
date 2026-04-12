import polars as pl
import pytest
from bs4 import BeautifulSoup

from pybaseballstats.utils.bref_utils import _extract_table


def test_extract_table_parses_numeric_types_and_percentages():
    soup = BeautifulSoup(
        """
        <table>
          <tbody>
            <tr>
              <td data-stat="int_col">1,234</td>
              <td data-stat="float_col">3.14</td>
              <td data-stat="perc_col">45%</td>
              <td data-stat="neg_perc_col">-12.5%</td>
              <td data-stat="accounting_col">(1.25)</td>
              <td data-stat="text_col">Yankees</td>
            </tr>
          </tbody>
        </table>
        """,
        "html.parser",
    )

    data = _extract_table(soup.find("table"))

    assert isinstance(data["int_col"], pl.Series)
    assert data["int_col"].dtype == pl.Int32
    assert data["int_col"].to_list() == [1234]

    assert data["float_col"].dtype == pl.Float32
    assert data["float_col"].to_list()[0] == pytest.approx(3.14)

    assert data["perc_col"].dtype == pl.Float32
    assert data["perc_col"].to_list() == [45.0]

    assert data["neg_perc_col"].dtype == pl.Float32
    assert data["neg_perc_col"].to_list() == [-12.5]

    assert data["accounting_col"].dtype == pl.Float32
    assert data["accounting_col"].to_list() == [-1.25]

    assert data["text_col"].dtype == pl.Utf8
    assert data["text_col"].to_list() == ["Yankees"]


def test_extract_table_handles_home_or_vis_and_missing_values():
    soup = BeautifulSoup(
        """
        <table>
          <tbody>
            <tr>
              <td data-stat="homeORvis">@</td>
              <td data-stat="optional">-</td>
            </tr>
            <tr>
              <td data-stat="homeORvis"></td>
              <td data-stat="optional"></td>
            </tr>
          </tbody>
        </table>
        """,
        "html.parser",
    )

    data = _extract_table(soup.find("table"))

    assert data["homeORvis"].dtype == pl.Utf8
    assert data["homeORvis"].to_list() == ["away", "home"]

    assert data["optional"].to_list() == [None, None]
