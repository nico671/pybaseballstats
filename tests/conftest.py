from __future__ import annotations

import json
import socket
from pathlib import Path

import pytest

from pybaseballstats.utils.session_utils import PBSSessionManager


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "bref"


class FixtureResponse:
    """Minimal response object consumed by the BREF public functions."""

    def __init__(self, content: bytes) -> None:
        self.content = content
        self.text = content.decode("utf-8")
        self.status_code = 200

    def raise_for_status(self) -> None:
        return None


@pytest.fixture(autouse=True)
def block_network_for_offline_tests(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
):
    """Make accidental network access fail immediately in the default suite."""
    if request.node.get_closest_marker("live") is not None:
        return

    def blocked(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("Offline tests may not access the network")

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket.socket, "connect", blocked)


@pytest.fixture(autouse=True)
def replay_bref_pages(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    """Replay raw BREF pages for BREF tests and fail on unrecorded URLs."""
    if (
        not request.node.path.name.startswith("bref_")
        or request.node.get_closest_marker("live") is not None
    ):
        return

    index_path = FIXTURE_ROOT / "index.json"
    index: dict[str, dict[str, str]] = json.loads(
        index_path.read_text(encoding="utf-8")
    )

    def get_fixture(url: str, **_kwargs: object) -> FixtureResponse:
        try:
            relative_path = index[url]["path"]
        except KeyError as exc:
            raise AssertionError(f"No offline BREF fixture recorded for {url}") from exc
        return FixtureResponse((FIXTURE_ROOT / relative_path).read_bytes())

    session = PBSSessionManager.instance()  # type: ignore[attr-defined]
    monkeypatch.setattr(session, "get", get_fixture)
