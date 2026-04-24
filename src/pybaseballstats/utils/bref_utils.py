import re
from typing import Any

import polars as pl
from bs4 import BeautifulSoup, Comment

from pybaseballstats.consts.bref_consts import BREF_TEAM_CODE_SWITCHES, BREFTeams


def get_bref_table_html(html_content: str, table_id: str) -> str | None:
    """
    Extracts a specific table from Baseball Reference HTML.
    Checks the standard DOM first, then searches inside HTML comments
    for lazy-loaded tables.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Check if the table is normally rendered in the DOM
    target_table = soup.find("table", id=table_id)
    if target_table:
        return str(target_table)

    # 2. If not found, it is likely hidden inside an HTML comment
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if f'id="{table_id}"' in comment or f"id='{table_id}'" in comment:
            # Parse the hidden HTML
            hidden_soup = BeautifulSoup(comment, "html.parser")
            hidden_table = hidden_soup.find("table", id=table_id)
            if hidden_table:
                return str(hidden_table)

    print(f"Table with id '{table_id}' not found in DOM or comments.")
    return None


_INT_PATTERN = re.compile(r"^[+-]?\d+$")
_FLOAT_PATTERN = re.compile(r"^[+-]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][+-]?\d+)?$")
_PERCENT_PATTERN = re.compile(r"^[+-]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][+-]?\d+)?%$")


def _safe_parse_cell_value(value: str | None) -> str | int | float | None:
    """Parse a table cell value into int/float/string/None when safe.

    - Handles thousands separators in numeric strings (for example ``"12,345"``).
    - Handles percentages (for example ``"12.3%"`` and ``"-4%"``) as numeric values
      without the percent sign.
    - Preserves non-numeric content as strings.
    """
    if value is None:
        return None

    text = value.strip()
    if text == "":
        return None

    normalized = text.replace("−", "-")

    # Common non-values used in tables.
    if normalized in {"-", "--", "—", "N/A", "n/a", "NA", "na", "null", "NULL"}:
        return None

    # Accounting style negatives, e.g. "(1.2)" -> -1.2
    is_accounting_negative = normalized.startswith("(") and normalized.endswith(")")
    if is_accounting_negative:
        normalized = f"-{normalized[1:-1].strip()}"

    numeric_candidate = normalized.replace(",", "")

    if _PERCENT_PATTERN.match(numeric_candidate):
        try:
            return float(numeric_candidate[:-1])
        except ValueError:
            return text

    if _INT_PATTERN.match(numeric_candidate):
        try:
            return int(numeric_candidate)
        except ValueError:
            return text

    if _FLOAT_PATTERN.match(numeric_candidate):
        try:
            return float(numeric_candidate)
        except ValueError:
            return text

    return text


def _infer_series_dtype(values: list[str | int | float | None]) -> Any:
    """Infer a stable Polars dtype for parsed values."""
    non_null_values = [value for value in values if value is not None]
    if not non_null_values:
        return pl.Utf8

    if all(isinstance(value, int) for value in non_null_values):
        return pl.Int32

    if all(isinstance(value, (int, float)) for value in non_null_values):
        return pl.Float32

    return pl.Utf8


def _extract_table(table):
    """Extracts data from an HTML table into a dictionary of lists.

    Works specifically for Baseball Reference Tables
    """
    trs = table.tbody.find_all("tr")
    row_data: dict[str, list[str | int | float | None]] = {}

    for tr in trs:
        if tr.has_attr("class") and "thead" in tr["class"]:
            continue
        tds = tr.find_all("th")
        tds.extend(tr.find_all("td"))
        if len(tds) == 0:
            continue
        used_data_stats: set[str] = set()
        for td in tds:
            data_stat = td.attrs["data-stat"]
            if data_stat in used_data_stats:
                continue
            if data_stat not in row_data:
                row_data[data_stat] = []
            if td.find("a") and data_stat != "player":  # special case for bref_draft
                raw_value = td.find("a").text
            elif td.find("a") and data_stat == "player":
                raw_value = td.text
            elif td.find("span"):
                raw_value = td.find("span").string
            elif td.find("strong"):
                raw_value = td.find("strong").string
            elif (
                data_stat == "homeORvis"
            ):  # special case for schedule/results table to determine home vs away
                if td.text.strip() == "@":
                    row_data[data_stat].append("away")
                else:
                    row_data[data_stat].append("home")
                continue
            else:
                raw_value = td.string
            used_data_stats.add(data_stat)
            row_data[data_stat].append(_safe_parse_cell_value(raw_value))

    typed_row_data: dict[str, pl.Series] = {}
    for column_name, values in row_data.items():
        dtype = _infer_series_dtype(values)
        if dtype == pl.Utf8:
            normalized_values: list[str | None] = [
                None if value is None else str(value) for value in values
            ]
            typed_row_data[column_name] = pl.Series(
                column_name, normalized_values, dtype=dtype
            )
        else:
            typed_row_data[column_name] = pl.Series(column_name, values, dtype=dtype)

    return typed_row_data


def resolve_bref_team_code(team: BREFTeams, year: int) -> str:
    """Resolve the Baseball Reference team code for a franchise/year.

    Args:
        team (BREFTeams): Stable franchise enum value.
        year (int): Season year.

    Raises:
        ValueError: If no code mapping is available for ``team``/``year``.

    Returns:
        str: Baseball Reference team code for URL usage.
    """
    ranges = BREF_TEAM_CODE_SWITCHES.get(team.value)
    if ranges is None:
        return team.value

    for start_year, end_year, team_code in ranges:
        if start_year <= year <= end_year:
            return team_code

    # If outside known bounds (e.g., a future year), use nearest known code.
    if year < ranges[0][0]:
        return ranges[0][2]
    if year > ranges[-1][1]:
        return ranges[-1][2]

    raise ValueError(
        f"No Baseball Reference team code mapping found for {team.name} in {year}."
    )
