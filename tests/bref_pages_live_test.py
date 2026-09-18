from __future__ import annotations

from dataclasses import dataclass

import pytest
from bs4 import BeautifulSoup

from pybaseballstats._consts.bref_consts import (
    BREF_DRAFT_YEAR_ROUND_URL,
    BREF_MANAGER_TENDENCIES_URL,
    BREF_SINGLE_PLAYER_BATTING_URL,
    BREF_SINGLE_PLAYER_FIELDING_URL,
    BREF_SINGLE_PLAYER_PITCHING_URL,
    BREF_TEAMS_BATTING_BASE_URL,
    BREF_TEAMS_FIELDING_BASE_URL,
    BREF_TEAMS_PITCHING_BASE_URL,
    BREF_TEAMS_ROSTER_URL,
    BREF_TEAMS_SCHEDULE_RESULTS_URL,
    TEAM_YEAR_DRAFT_URL,
)
from pybaseballstats._utils.bref_utils import _extract_table, get_bref_table_html
from pybaseballstats._utils.session_utils import PBSSessionManager

pytestmark = [pytest.mark.live, pytest.mark.xdist_group("bref")]


@dataclass(frozen=True)
class PageContract:
    name: str
    url: str
    table_ids: tuple[str, ...]


PAGE_CONTRACTS = (
    PageContract(
        "draft-year-round",
        BREF_DRAFT_YEAR_ROUND_URL.format(year=2023, round=1),
        ("draft_stats",),
    ),
    PageContract(
        "draft-franchise",
        TEAM_YEAR_DRAFT_URL.format(team="ANA", year=2023),
        ("draft_stats",),
    ),
    PageContract(
        "managers",
        BREF_MANAGER_TENDENCIES_URL.format(year=2024),
        ("manager_record", "manager_tendencies"),
    ),
    PageContract(
        "player-batting",
        BREF_SINGLE_PLAYER_BATTING_URL.format(initial="s", player_code="suzukse01"),
        (
            "players_standard_batting",
            "players_value_batting",
            "players_advanced_batting",
            "batting_sabermetric",
            "batting_ratio",
            "batting_win_probability",
            "batting_baserunning",
            "batting_situational",
            "batting_pitches",
            "cumulative_batting",
        ),
    ),
    PageContract(
        "player-pitching",
        BREF_SINGLE_PLAYER_PITCHING_URL.format(initial="i", player_code="imanash01"),
        (
            "players_standard_pitching",
            "players_value_pitching",
            "players_advanced_pitching",
            "pitching_ratio",
            "pitching_win_probability",
            "pitching_basesituation",
            "pitching_batting",
            "pitching_pitches",
            "cumulative_pitching",
        ),
    ),
    PageContract(
        "player-fielding",
        BREF_SINGLE_PLAYER_FIELDING_URL.format(initial="s", player_code="sheldsc01"),
        (
            "players_standard_fielding",
            "advanced_fielding",
            "appearances",
            "advanced_fielding_3b",
            "advanced_fielding_ss",
            "advanced_fielding_2b",
            "advanced_fielding_1b",
            "advanced_fielding_c",
            "advanced_fielding_c_baserunning",
            "advanced_fielding_lf",
            "advanced_fielding_rf",
            "advanced_fielding_cf",
            "advanced_fielding_p",
        ),
    ),
    PageContract(
        "team-schedule",
        BREF_TEAMS_SCHEDULE_RESULTS_URL.format(team_code="LAA", year=2023),
        ("team_schedule",),
    ),
    PageContract(
        "team-roster",
        BREF_TEAMS_ROSTER_URL.format(team_code="LAA", year=2023),
        ("appearances",),
    ),
    PageContract(
        "team-batting",
        BREF_TEAMS_BATTING_BASE_URL.format(team_code="NYY", year=2025),
        tuple(
            f"players_{metric}_batting"
            for metric in (
                "standard",
                "value",
                "advanced",
                "sabermetric",
                "ratio",
                "win_probability",
                "baserunning",
                "situational",
                "pitches",
                "cumulative",
            )
        ),
    ),
    PageContract(
        "team-pitching",
        BREF_TEAMS_PITCHING_BASE_URL.format(team_code="NYY", year=2025),
        (
            "players_standard_pitching",
            "players_value_pitching",
            "players_advanced_pitching",
            "players_ratio_pitching",
            "players_batting_pitching",
            "players_win_probability_pitching",
            "players_starter_pitching",
            "players_reliever_pitching",
            "players_basesituation_pitching",
            "players_cumulative_pitching",
        ),
    ),
    PageContract(
        "team-fielding",
        BREF_TEAMS_FIELDING_BASE_URL.format(team_code="NYY", year=2025),
        (
            "players_standard_fielding",
            "players_standard_fielding_c",
            "players_standard_fielding_1b",
            "players_standard_fielding_2b",
            "players_standard_fielding_3b",
            "players_standard_fielding_ss",
            "players_standard_fielding_lf",
            "players_standard_fielding_cf",
            "players_standard_fielding_rf",
            "players_standard_fielding_of",
            "players_standard_fielding_p",
            "players_DH_games",
            "players_advanced_fielding_c",
            "players_advanced_fielding_c_baserunning",
            "players_advanced_fielding_1b",
            "players_advanced_fielding_2b",
            "players_advanced_fielding_3b",
            "players_advanced_fielding_ss",
            "players_advanced_fielding_lf",
            "players_advanced_fielding_cf",
            "players_advanced_fielding_rf",
            "players_advanced_fielding_p",
        ),
    ),
)


@pytest.fixture(scope="module")
def bref_session():
    session = PBSSessionManager.instance(max_req_per_minute=5)  # type: ignore[attr-defined]
    session.request_timestamps.clear()
    return session


@pytest.mark.parametrize("contract", PAGE_CONTRACTS, ids=lambda case: case.name)
def test_bref_page_contract(bref_session, contract: PageContract):
    response = bref_session.get(contract.url, timeout=60)
    assert response is not None, f"Failed to fetch {contract.url}"
    assert_page_contract(response, contract)


def assert_page_contract(response, contract: PageContract) -> None:
    for table_id in contract.table_ids:
        table_html = get_bref_table_html(response.text, table_id)
        assert table_html is not None, f"Missing {table_id} at {contract.url}"

        table = BeautifulSoup(table_html, "html.parser").find("table")
        assert table is not None and table.tbody is not None
        parsed_columns = _extract_table(table)
        assert parsed_columns, f"Could not parse {table_id} at {contract.url}"


def test_bref_batting_orders_page(bref_session):
    url = "https://www.baseball-reference.com/teams/NYY/2025-batting-orders.shtml"
    response = bref_session.get(url, timeout=60)
    assert response is not None, f"Failed to fetch {url}"
    assert_batting_orders_page(response)


def assert_batting_orders_page(response) -> None:
    soup = BeautifulSoup(response.content, "html.parser")
    batting_orders = [
        table
        for table in soup.find_all("table", class_="grid_table")
        if (caption := table.find("caption"))
        and "Batting Orders" in caption.get_text(strip=True)
    ]
    assert len(batting_orders) == 1
    assert batting_orders[0].tbody is not None
    assert batting_orders[0].tbody.find("tr") is not None
