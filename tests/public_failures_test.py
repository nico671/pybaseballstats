"""Public failure and valid-empty behavior without network access."""

from types import SimpleNamespace

import polars as pl
import pytest

from pybaseballstats import (
    _bref_managers,
    _umpire_scorecards,
    statcast_single_game,
    umpire_scorecards,
)
from pybaseballstats._utils import (
    bref_utils,
    retrosheet_utils,
    statcast_single_game_utils,
)
from pybaseballstats.statcast_leaderboards import _fielding, _park

DATES = {"start_date": "2025-07-01", "end_date": "2025-07-07"}


@pytest.mark.parametrize(
    ("function", "extra"),
    [
        (umpire_scorecards.game_data, {}),
        (umpire_scorecards.umpire_data, {}),
        (umpire_scorecards.team_data, {}),
        (umpire_scorecards.player_data, {"player_type": "C"}),
    ],
)
def test_umpire_response_structure_and_empty(monkeypatch, function, extra):
    monkeypatch.setattr(_umpire_scorecards, "get_json", lambda url: {"rows": []})
    result = function(**DATES, **extra)
    assert isinstance(result, pl.DataFrame)
    assert result.is_empty()

    monkeypatch.setattr(_umpire_scorecards, "get_json", lambda url: {"wrong": []})
    with pytest.raises(RuntimeError, match=function.__name__):
        function(**DATES, **extra)

    cause = RuntimeError("network down")

    def fail(url):
        raise cause

    monkeypatch.setattr(_umpire_scorecards, "get_json", fail)
    with pytest.raises(RuntimeError, match=function.__name__) as caught:
        function(**DATES, **extra)
    assert caught.value.__cause__ is cause


def test_umpire_name_uses_exact_match(monkeypatch):
    monkeypatch.setattr(
        _umpire_scorecards,
        "get_json",
        lambda url: {"rows": [{"date": "2025-07-01", "umpire": "A. Smith"}]},
    )
    assert umpire_scorecards.game_data(**DATES, umpire_name="A. Smith").height == 1
    assert umpire_scorecards.game_data(**DATES, umpire_name="A.*Smith").is_empty()
    assert umpire_scorecards.game_data(**DATES, umpire_name="Missing").is_empty()


@pytest.mark.parametrize(
    "function",
    [
        statcast_single_game.single_game_pitch_by_pitch,
        statcast_single_game.single_game_exit_velocity,
        statcast_single_game.single_game_pitch_velocity,
        statcast_single_game.single_game_win_probability,
    ],
)
def test_game_pk_is_checked_before_retrieval(function):
    for value, expected in [(None, TypeError), (True, TypeError), (0, ValueError)]:
        with pytest.raises(expected):
            function(
                game_pk=value,
                **(
                    {}
                    if function is statcast_single_game.single_game_pitch_by_pitch
                    else {"game_date": "2025-08-13"}
                ),
            )


def test_retrosheet_failed_shard_does_not_fill_cache(monkeypatch):
    retrosheet_utils._clear_people_cache()
    calls = []

    def fail_second(url):
        calls.append(url)
        if len(calls) == 2:
            raise RuntimeError("network down")
        return b"key_fangraphs,key_mlbam,key_retro,key_bbref,name_last,name_first,name_given,name_nick,name_matrilineal,name_suffix\n"

    monkeypatch.setattr(retrosheet_utils, "get_bytes", fail_second)
    with pytest.raises(RuntimeError, match="player_lookup") as caught:
        retrosheet_utils._get_people_data()
    assert isinstance(caught.value.__cause__, RuntimeError)
    assert retrosheet_utils._get_people_data.cache_info().currsize == 0


def test_leaderboard_missing_source_columns_has_operation_and_cause(monkeypatch):
    monkeypatch.setattr(
        _fielding, "get_csv", lambda url, **kwargs: pl.DataFrame({"x": [1]})
    )
    with pytest.raises(RuntimeError, match="arm_strength_leaderboard") as caught:
        _fielding.arm_strength_leaderboard(year=2025)
    assert isinstance(caught.value.__cause__, pl.exceptions.PolarsError)


def test_bref_missing_table_is_failure_and_empty_table_keeps_columns(monkeypatch):
    monkeypatch.setattr(
        _bref_managers.session,
        "get",
        lambda *args, **kwargs: SimpleNamespace(
            text="<html><body>challenge</body></html>"
        ),
    )
    with pytest.raises(RuntimeError, match="managers_basic_data: missing"):
        _bref_managers.managers_basic_data(2025)

    html = (
        '<table id="test"><thead><tr><th data-stat="name">Name</th></tr></thead>'
        "<tbody></tbody></table>"
    )
    frame = bref_utils._required_table(html, "test", "test_operation")
    assert frame.is_empty() and frame.columns == ["name"]


@pytest.mark.parametrize("failure_at", ["new_page", "selector"])
def test_park_browser_closes_on_failure(monkeypatch, failure_at):
    from playwright.sync_api import Error as PlaywrightError

    closed = []

    class Page:
        def goto(self, *args, **kwargs):
            pass

        def wait_for_selector(self, *args):
            raise PlaywrightError("selector timeout")

        def close(self):
            closed.append("page")

    class Browser:
        def new_page(self):
            if failure_at == "new_page":
                raise PlaywrightError("new page failed")
            return Page()

        def close(self):
            closed.append("browser")

    class Playwright:
        chromium = type("Chromium", (), {"launch": lambda self: Browser()})()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(_park, "sync_playwright", Playwright)
    with pytest.raises(
        RuntimeError, match="park_factor_distance_leaderboard"
    ) as caught:
        _park.park_factor_distance_leaderboard(2025)
    assert isinstance(caught.value.__cause__, PlaywrightError)
    assert closed == (["browser"] if failure_at == "new_page" else ["page", "browser"])


@pytest.mark.asyncio
@pytest.mark.parametrize("failure_at", ["new_context", "new_page"])
async def test_single_game_browser_closes_on_setup_failure(monkeypatch, failure_at):
    from playwright.async_api import Error as PlaywrightError

    closed = []

    class Context:
        async def route(self, *args):
            pass

        async def new_page(self):
            raise PlaywrightError("new page failed")

        async def close(self):
            closed.append("context")

    class Browser:
        async def new_context(self, **kwargs):
            if failure_at == "new_context":
                raise PlaywrightError("new context failed")
            return Context()

        async def close(self):
            closed.append("browser")

    class Chromium:
        async def launch(self, **kwargs):
            return Browser()

    class Playwright:
        chromium = Chromium()

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

    monkeypatch.setattr(statcast_single_game_utils, "async_playwright", Playwright)
    with pytest.raises(PlaywrightError):
        async with statcast_single_game_utils.get_page_async():
            pytest.fail("page setup should fail")
    assert closed == (
        ["browser"] if failure_at == "new_context" else ["context", "browser"]
    )
