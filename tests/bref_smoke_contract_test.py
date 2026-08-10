from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from bref_pages_live_test import (
    PAGE_CONTRACTS,
    PageContract,
    assert_batting_orders_page,
    assert_page_contract,
)


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "bref"
FIXTURE_INDEX: dict[str, dict[str, str]] = json.loads(
    (FIXTURE_ROOT / "index.json").read_text(encoding="utf-8")
)


def fixture_response(url: str) -> SimpleNamespace:
    content = (FIXTURE_ROOT / FIXTURE_INDEX[url]["path"]).read_bytes()
    return SimpleNamespace(content=content, text=content.decode("utf-8"))


@pytest.mark.parametrize("contract", PAGE_CONTRACTS, ids=lambda case: case.name)
def test_saved_page_satisfies_live_contract(contract: PageContract):
    assert_page_contract(fixture_response(contract.url), contract)


def test_saved_batting_orders_page_satisfies_live_contract():
    url = "https://www.baseball-reference.com/teams/NYY/2025-batting-orders.shtml"
    assert_batting_orders_page(fixture_response(url))
