import asyncio
from functools import wraps
from typing import Any, Callable, Coroutine, Dict, ParamSpec, TypeVar

import nest_asyncio  # type: ignore
import polars as pl
from bs4 import BeautifulSoup
from playwright.async_api import Error as PlaywrightError

from pybaseballstats._consts.statcast_consts import (
    STATCAST_SINGLE_GAME_EV_PV_WP_URL,
    STATCAST_SINGLE_GAME_URL,
)
from pybaseballstats._statcast import pitch_by_pitch_data
from pybaseballstats._utils.request_utils import get_csv
from pybaseballstats._utils.statcast_single_game_utils import (
    _handle_single_game_date,
    fetch_gamefeed_table_html,
    get_page_async,
)

__all__ = [
    "get_available_game_pks_for_date",
    "single_game_pitch_by_pitch",
    "single_game_exit_velocity",
    "single_game_pitch_velocity",
    "single_game_win_probability",
]

P = ParamSpec("P")
T = TypeVar("T")


def _game_errors(function: Callable[P, T]) -> Callable[P, T]:
    @wraps(function)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return function(*args, **kwargs)
        except (RuntimeError, pl.exceptions.PolarsError, PlaywrightError) as exc:
            raise RuntimeError(
                f"{function.__name__}: game data retrieval failed"
            ) from exc

    return wrapped


def _validate_game_pk(game_pk: int) -> None:
    if type(game_pk) is not int:
        raise TypeError("game_pk must be an integer")
    if game_pk < 1:
        raise ValueError("game_pk must be positive")


# helper for running async code in sync functions
def _run_in_loop(coro: Coroutine[Any, Any, Any]) -> Any:
    """Run an async coroutine in the current runtime context.

    If an event loop is already active (e.g. notebooks), this function applies
    ``nest_asyncio`` and reuses the running loop.

    Args:
        coro: Coroutine object to execute.

    Returns:
        Any: Result returned by ``coro``.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        nest_asyncio.apply()
        return loop.run_until_complete(coro)


@_game_errors
def get_available_game_pks_for_date(
    game_date: str,
) -> list[dict[str, int | str]]:
    """Return game IDs and teams for all games on a date.

    Args:
        game_date (str): Date in ``YYYY-MM-DD`` format.

    Returns:
        list[dict[str, str]]: One dictionary per game with ``game_pk``,
        ``home_team``, and ``away_team``.
    """
    available_games: list[dict[str, int | str]] = []
    df = pitch_by_pitch_data(
        game_date,
        game_date,
        force_collect=True,  # we force collect here bc we only have one day, dataframe shouldnt be too large
    )  # don't need game date string conversion here, the pitch_by_pitch_data function handles that
    if not isinstance(df, pl.DataFrame):
        raise RuntimeError("game discovery did not return a DataFrame")
    if df.is_empty():
        return available_games
    if not {"game_pk", "home_team", "away_team"}.issubset(df.columns):
        raise RuntimeError("game discovery response lacks required columns")

    for i, group in df.group_by("game_pk"):
        game_pk = group.select(pl.col("game_pk").first()).item()
        game_data = {}
        game_data["game_pk"] = game_pk
        game_data["home_team"] = group.select(pl.col("home_team").first()).item()
        game_data["away_team"] = group.select(pl.col("away_team").first()).item()
        available_games.append(game_data)
    return available_games


@_game_errors
def single_game_pitch_by_pitch(game_pk: int) -> pl.DataFrame:
    """Return Statcast pitch-by-pitch data for one game.

    Args:
        game_pk (int): Baseball Savant game identifier.

    Returns:
        pl.DataFrame: Pitch-level Statcast data for the requested game.
    """
    _validate_game_pk(game_pk)
    return get_csv(STATCAST_SINGLE_GAME_URL.format(game_pk=game_pk))


@_game_errors
def single_game_exit_velocity(game_pk: int, game_date: str) -> pl.DataFrame:
    """Return batted-ball exit velocity metrics for one game.

    Args:
        game_pk (int): Baseball Savant game identifier. You can discover valid
            values with :func:`get_available_game_pks_for_date`.
        game_date (str): Game date in ``YYYY-MM-DD`` format. Must match
            ``game_pk``.

    Returns:
        pl.DataFrame: Exit velocity table as a Polars DataFrame (one row per
        ball in play). A valid table with no rows returns an empty DataFrame.
        A missing table or fetch failure raises RuntimeError.
    """
    _validate_game_pk(game_pk)
    return _run_in_loop(_single_game_exit_velocity_async(game_pk, game_date))


async def _single_game_exit_velocity_async(
    game_pk: int,
    game_date: str,
) -> pl.DataFrame:
    game_date_str = _handle_single_game_date(game_date)
    url = STATCAST_SINGLE_GAME_EV_PV_WP_URL.format(
        game_date=game_date_str, game_pk=game_pk, stat_type="exitVelocity"
    )
    async with get_page_async() as page:
        ev_table_html = await fetch_gamefeed_table_html(
            page, url, f"#exitVelocityTable_{game_pk}"
        )
    soup = BeautifulSoup(ev_table_html, "html.parser")
    table = soup.find("table")
    if table is None:
        raise RuntimeError("gamefeed response is missing its table")

    # extract headers
    thead = table.find("thead")
    if thead is None:
        raise RuntimeError("gamefeed table is missing its header")
    headers_tr = thead.find("tr", {"class": "tr-component-row"})
    if headers_tr is None:
        raise RuntimeError("gamefeed table is missing its header row")
    dirty_headers = [
        th.text.strip() for th in headers_tr.find_all("th") if th.text.strip() != ""
    ]
    headers = []
    for header in dirty_headers:
        if "\n" in header:
            split_headers = header.split("\n")
            headers.append(split_headers[0].strip() + split_headers[1].strip())
        else:
            headers.append(header)
    # extract data
    tbody = table.find("tbody")
    if tbody is None:
        raise RuntimeError("gamefeed table is missing its body")
    row_data: Dict[str, list[str]] = {header: [] for header in headers}

    for tr in tbody.find_all("tr"):
        cells = tr.find_all("td")

        # Create a mapping of filtered cells to their corresponding headers
        cell_data = {}
        header_index = 0

        for cell in cells:
            if cell.find("img", {"class": "table-team-logo"}):
                # # Skip team logo cells but increment header index
                # header_index += 1
                continue
            else:
                # Only process if we have a valid header
                if header_index < len(headers):
                    # Special handling for player name cells
                    if "player-mug-wrapper" in str(cell):
                        # Find the div that contains the player name
                        name_div = cell.find("div", {"style": "margin-left: 2px;"})
                        if name_div:
                            cell_text = name_div.get_text(strip=True)
                        else:
                            cell_text = cell.get_text(strip=True)
                    else:
                        cell_text = cell.get_text(strip=True)
                        link = cell.find("a")
                        if link:
                            cell_text = link.get_text(strip=True)

                    header = headers[header_index]
                    cell_data[header] = cell_text

                header_index += 1

        # Now add all the data from this row to row_data
        for header, value in cell_data.items():
            row_data[header].append(value)
    # create df and clean df
    df = pl.DataFrame(row_data)
    df = df.drop("Rk.")
    df = df.rename(
        {
            "Batter": "batter_name",
            "PA": "num_pa",
            "Inning": "inning",
            "Result": "result",
            "Exit Velo": "exit_velo",
            "LA": "launch_angle",
            "Hit Dist.": "hit_distance",
            "BatSpeed": "bat_speed",
            "PitchVelocity": "pitch_velocity",
            "HR / Park": "hr_in_how_many_parks",
        }
    )
    df = df.with_columns(
        pl.all().replace("", None),
    )
    df = df.with_columns(
        [
            pl.col("num_pa").cast(pl.Int8),
            pl.col("inning").cast(pl.Int8),
            pl.col("exit_velo").cast(pl.Float32),
            pl.col("launch_angle").cast(pl.Float32),
            pl.col("hit_distance").cast(pl.Int16),
            pl.col("bat_speed").str.replace("⚡", "").cast(pl.Float32),
            pl.col("pitch_velocity").cast(pl.Float32),
            pl.col("xBA").cast(pl.Float32),
        ]
    )

    return df


@_game_errors
def single_game_pitch_velocity(game_pk: int, game_date: str) -> pl.DataFrame:
    """Return per-pitch velocity/spin movement metrics for one game.

    Args:
        game_pk (int): Baseball Savant game identifier. You can discover valid
            values with :func:`get_available_game_pks_for_date`.
        game_date (str): Game date in ``YYYY-MM-DD`` format. Must match
            ``game_pk``.

    Returns:
        pl.DataFrame: Pitch velocity table as a Polars DataFrame (one row per
        pitch). A valid table with no rows returns an empty DataFrame.
        A missing table or fetch failure raises RuntimeError.
    """
    _validate_game_pk(game_pk)
    return _run_in_loop(_single_game_pitch_velocity_async(game_pk, game_date))


async def _single_game_pitch_velocity_async(
    game_pk: int,
    game_date: str,
) -> pl.DataFrame:
    game_date_str = _handle_single_game_date(game_date)
    url = STATCAST_SINGLE_GAME_EV_PV_WP_URL.format(
        game_date=game_date_str, game_pk=game_pk, stat_type="pitchVelocity"
    )
    async with get_page_async() as page:
        pv_table_html = await fetch_gamefeed_table_html(
            page, url, f"#pitchVelocity_{game_pk}"
        )

    soup = BeautifulSoup(pv_table_html, "html.parser")
    table = soup.find("table")
    if table is None:
        raise RuntimeError("gamefeed response is missing its table")

    # extract headers
    thead = table.find("thead")
    if thead is None:
        raise RuntimeError("gamefeed table is missing its header")
    headers_tr = thead.find("tr", {"class": "tr-component-row"})
    if headers_tr is None:
        raise RuntimeError("gamefeed table is missing its header row")
    dirty_headers = [
        th.text.strip() for th in headers_tr.find_all("th") if th.text.strip() != ""
    ]
    dirty_headers = dirty_headers[:-1]
    headers = []
    for header in dirty_headers:
        if "\n" in header:
            split_headers = header.split("\n")
            headers.append(split_headers[0].strip() + split_headers[1].strip())
        else:
            headers.append(header)
    # extract data
    tbody = table.find("tbody")
    if tbody is None:
        raise RuntimeError("gamefeed table is missing its body")
    row_data: Dict[str, list[str]] = {header: [] for header in headers}

    for tr in tbody.find_all("tr"):
        cells = tr.find_all("td")

        # Create a mapping of filtered cells to their corresponding headers
        cell_data = {}
        header_index = 0

        for cell in cells:
            if cell.find("img", {"class": "table-team-logo"}):
                # # Skip team logo cells but increment header index
                # header_index += 1
                continue
            else:
                # Only process if we have a valid header
                if header_index < len(headers):
                    # Special handling for player name cells
                    if "player-mug-wrapper" in str(cell):
                        # Find the div that contains the player name
                        name_div = cell.find("div", {"style": "margin-left: 2px;"})
                        if name_div:
                            cell_text = name_div.get_text(strip=True)
                        else:
                            cell_text = cell.get_text(strip=True)
                    elif "→" in str(cell) or "↑" in str(cell) or "↓" in str(cell):
                        continue
                    else:
                        cell_text = cell.get_text(strip=True)
                        link = cell.find("a")
                        if link:
                            cell_text = link.get_text(strip=True)

                    header = headers[header_index]
                    cell_data[header] = cell_text

                header_index += 1

        # Now add all the data from this row to row_data
        for header, value in cell_data.items():
            row_data[header].append(value)

    # create df and clean df
    df = pl.DataFrame(row_data)
    df = df.drop(["Rk."])
    df = df.rename(
        {
            "Pitcher": "pitcher_name",
            "Batter": "batter_name",
            "GamePitch #": "game_pitch_number",
            "Pitch": "pitcher_pitch_number",
            "PA": "game_pa_number",
            "Pitch Type": "pitch_type",
            "MPHPitchVelo": "pitch_velocity_mph",
            "RPMSpin": "spin_rate_rpm",
            "IVB": "induced_vertical_break",
            "Drop": "drop_vertical_break",
            "HBreak": "horizontal_break",
            "Inn.": "inning",
        }
    )
    df = df.with_columns(
        pl.all().replace("", None),
    )
    df = df.with_columns(
        [
            pl.col("inning").cast(pl.Int8),
            pl.col("game_pitch_number").cast(pl.Int32),
            pl.col("pitcher_pitch_number").cast(pl.Int16),
            pl.col("game_pa_number").cast(pl.Int16),
            pl.col("pitch_velocity_mph").cast(pl.Float32),
            pl.col("spin_rate_rpm").cast(pl.Float32),
            pl.col("induced_vertical_break").cast(pl.Float32),
            pl.col("drop_vertical_break").cast(pl.Float32),
            pl.col("horizontal_break").cast(pl.Float32),
        ]
    )
    return df


@_game_errors
def single_game_win_probability(game_pk: int, game_date: str) -> pl.DataFrame:
    """Return win-probability snapshots across plate appearances for one game.

    Args:
        game_pk (int): Baseball Savant game identifier. You can discover valid
            values with :func:`get_available_game_pks_for_date`.
        game_date (str): Game date in ``YYYY-MM-DD`` format. Must match
            ``game_pk``.

    Returns:
        pl.DataFrame: Win probability table as a Polars DataFrame (one row per
        game state/plate appearance event). A valid table with no rows returns
        an empty DataFrame. A missing table or fetch failure raises RuntimeError.
    """
    _validate_game_pk(game_pk)
    return _run_in_loop(_single_game_win_probability_async(game_pk, game_date))


async def _single_game_win_probability_async(
    game_pk: int,
    game_date: str,
) -> pl.DataFrame:
    game_date_str = _handle_single_game_date(game_date)
    url = STATCAST_SINGLE_GAME_EV_PV_WP_URL.format(
        game_date=game_date_str, game_pk=game_pk, stat_type="winProbability"
    )
    async with get_page_async() as page:
        wp_table_html = await fetch_gamefeed_table_html(
            page, url, f"#tableWinProbability_{game_pk}"
        )

    soup = BeautifulSoup(wp_table_html, "html.parser")
    table = soup.find("table")
    if table is None:
        raise RuntimeError("gamefeed response is missing its table")

    thead = table.find("thead")
    if thead is None:
        raise RuntimeError("gamefeed table is missing its header")
    headers_tr = thead.find("tr", {"class": "tr-component-row"})
    if headers_tr is None:
        raise RuntimeError("gamefeed table is missing its header row")
    dirty_headers = [
        th.text.strip() for th in headers_tr.find_all("th") if th.text.strip() != ""
    ]
    headers = []
    for header in dirty_headers:
        if "\n" in header:
            split_headers = header.split("\n")
            headers.append(split_headers[0].strip() + split_headers[1].strip())
        else:
            headers.append(header)

    tbody = table.find("tbody")
    if tbody is None:
        raise RuntimeError("gamefeed table is missing its body")
    row_data: Dict[str, list[str]] = {header: [] for header in headers}

    for tr in tbody.find_all("tr"):
        cells = tr.find_all("td")

        # Create a mapping of filtered cells to their corresponding headers
        cell_data = {}
        header_index = 0

        for cell in cells:
            if cell.find("img", {"class": "table-team-logo"}):
                # # Skip team logo cells but increment header index
                # header_index += 1
                continue
            else:
                # Only process if we have a valid header
                if header_index < len(headers):
                    # Special handling for player name cells
                    if "player-mug-wrapper" in str(cell):
                        # Find the div that contains the player name
                        name_div = cell.find("div", {"style": "margin-left: 2px;"})
                        if name_div:
                            cell_text = name_div.get_text(strip=True)
                        else:
                            cell_text = cell.get_text(strip=True)
                    else:
                        cell_text = cell.get_text(strip=True)
                        link = cell.find("a")
                        if link:
                            cell_text = link.get_text(strip=True)

                    header = headers[header_index]
                    cell_data[header] = cell_text

                header_index += 1

        # Now add all the data from this row to row_data
        for header, value in cell_data.items():
            row_data[header].append(value)

    df = pl.DataFrame(row_data)
    df = df.rename(
        {
            "#": "game_pa_number",
            "Batter": "batter_name",
            "Pitcher": "pitcher_name",
            "Diff": "win_probability_diff",
            "Inning": "inning",
        }
    )
    df = df.with_columns(
        pl.all().replace("", None),
    )

    df = df.with_columns(
        [
            pl.col("game_pa_number").cast(pl.Int16),
            pl.col("win_probability_diff").cast(pl.Float32),
            pl.col("Home WP%").cast(pl.Float32),
            pl.col("Away WP%").cast(pl.Float32),
        ]
    )
    return df
