from importlib import import_module
from types import SimpleNamespace

import pytest

from pybaseballstats._utils import session_utils


def test_bref_modules_share_one_session():
    for name in ("bref_teams", "bref_managers", "bref_single_player"):
        assert (
            import_module(f"pybaseballstats.{name}").session
            is session_utils.BREF_SESSION
        )
    assert (
        import_module("pybaseballstats._utils.bref_utils").BREF_SESSION
        is session_utils.BREF_SESSION
    )


@pytest.mark.parametrize("limit", [5, 7])
def test_rate_limiter_keeps_full_minute_history(monkeypatch, limit):
    now = [0.0]
    sleeps = []

    def sleep(seconds):
        sleeps.append(seconds)
        now[0] += seconds

    monkeypatch.setattr(session_utils.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(session_utils.time, "sleep", sleep)
    monkeypatch.setattr(session_utils.random, "uniform", lambda _a, _b: 0.0)

    limiter = session_utils.RateLimiter(limit)
    for _ in range(limit):
        limiter.wait()

    assert list(limiter.request_timestamps) == [5.0 * i for i in range(limit)]
    limiter.wait()
    assert now[0] == 60.0
    assert sleeps[-1] == 60 - 5 * (limit - 1)
    assert list(limiter.request_timestamps)[-1] == 60.0


def test_rate_limiter_can_be_disabled(monkeypatch):
    monkeypatch.setattr(
        session_utils.time,
        "sleep",
        lambda _seconds: pytest.fail("disabled limiter must not sleep"),
    )
    limiter = session_utils.RateLimiter(None)
    limiter.wait()
    assert not limiter.request_timestamps


def test_cloudflare_fallback_reserves_a_second_request(monkeypatch):
    manager = session_utils.PBSSessionManager()
    reservations = []
    monkeypatch.setattr(manager.rate_limiter, "wait", reservations.append)
    monkeypatch.setattr(
        manager.session,
        "get",
        lambda *_args, **_kwargs: SimpleNamespace(
            status_code=403, url="https://example.com", text=""
        ),
    )
    fallback_response = object()
    monkeypatch.setattr(
        manager, "_solve_cloudflare_challenge", lambda *_args: fallback_response
    )

    assert manager.get("https://example.com") is fallback_response
    assert reservations == [False, False]
