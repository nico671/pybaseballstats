import polars as pl
import pytest
from bs4 import BeautifulSoup

from pybaseballstats.consts.bref_consts import BREFTeams
from pybaseballstats.utils.bref_utils import _extract_table, resolve_bref_team_code

pytestmark = pytest.mark.unit


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


def test_resolve_team_code_switches():
    assert resolve_bref_team_code(BREFTeams.ANGELS, 2004) == "ANA"
    assert resolve_bref_team_code(BREFTeams.ANGELS, 2005) == "LAA"
    assert resolve_bref_team_code(BREFTeams.MARLINS, 2011) == "FLA"
    assert resolve_bref_team_code(BREFTeams.MARLINS, 2012) == "MIA"
    assert resolve_bref_team_code(BREFTeams.RAYS, 2007) == "TBD"
    assert resolve_bref_team_code(BREFTeams.RAYS, 2008) == "TBR"
    assert resolve_bref_team_code(BREFTeams.NATIONALS, 2004) == "MON"
    assert resolve_bref_team_code(BREFTeams.NATIONALS, 2005) == "WSN"
    assert resolve_bref_team_code(BREFTeams.ATHLETICS, 2024) == "OAK"
    assert resolve_bref_team_code(BREFTeams.ATHLETICS, 2025) == "ATH"
    assert resolve_bref_team_code(BREFTeams.BRAVES, 1952) == "BSN"
    assert resolve_bref_team_code(BREFTeams.BRAVES, 1953) == "MLN"
    assert resolve_bref_team_code(BREFTeams.BRAVES, 1966) == "ATL"
