"""Capture the Baseball Reference pages used by offline tests.

This is a maintenance command, not part of the normal test suite. It deliberately
spaces requests to respect the same five-requests-per-minute policy as the
production BREF session manager.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urldefrag

from curl_cffi import requests

FIXTURE_ROOT = Path(__file__).parents[1] / "tests" / "fixtures" / "bref"
REQUEST_INTERVAL_SECONDS = 12.5

PAGES = {
    "https://www.baseball-reference.com/draft/index.fcgi?year_ID=2023&draft_round=1&draft_type=junreg&query_type=year_round&from_type_4y=0&from_type_jc=0&from_type_hs=0&from_type_unk=0": "draft/2023-round-1.html",
    "https://www.baseball-reference.com/draft/index.fcgi?team_ID=LAA&year_ID=2023&draft_type=junreg&query_type=franch_year&from_type_hs=0&from_type_4y=0&from_type_unk=0&from_type_jc=0": "draft/laa-2023.html",
    "https://www.baseball-reference.com/draft/index.fcgi?team_ID=ANA&year_ID=2023&draft_type=junreg&query_type=franch_year&from_type_hs=0&from_type_4y=0&from_type_unk=0&from_type_jc=0": "draft/ana-2023.html",
    "https://www.baseball-reference.com/leagues/majors/2023-managers.shtml": "managers/2023.html",
    "https://www.baseball-reference.com/leagues/majors/2024-managers.shtml#manager_tendencies": "managers/2024.html",
    "https://www.baseball-reference.com/players/s/suzukse01-bat.shtml": "players/suzukse01-batting.html",
    "https://www.baseball-reference.com/players/i/imanash01-pitch.shtml": "players/imanash01-pitching.html",
    "https://www.baseball-reference.com/players/s/sheldsc01-field.shtml": "players/sheldsc01-fielding.html",
    "https://www.baseball-reference.com/teams/LAA/2023-schedule-scores.shtml": "teams/laa-2023-schedule.html",
    "https://www.baseball-reference.com/teams/LAA/2023-roster.shtml#all_appearances": "teams/laa-2023-roster.html",
    "https://www.baseball-reference.com/teams/NYY/2025-batting-orders.shtml": "teams/nyy-2025-batting-orders.html",
    "https://www.baseball-reference.com/teams/NYY/2025-batting.shtml": "teams/nyy-2025-batting.html",
    "https://www.baseball-reference.com/teams/NYY/2025-pitching.shtml": "teams/nyy-2025-pitching.html",
    "https://www.baseball-reference.com/teams/NYY/2025-fielding.shtml": "teams/nyy-2025-fielding.html",
}


def main(force_regen: bool = False) -> None:
    session = requests.Session()
    index_path = FIXTURE_ROOT / "index.json"
    index: dict[str, dict[str, str]] = {}
    captured_count = 0

    for requested_url, relative_path in PAGES.items():
        print(f"Processing {requested_url} -> {relative_path}")
        fixture_path = FIXTURE_ROOT / relative_path
        if fixture_path.exists() and not force_regen:
            captured_at = datetime.fromtimestamp(
                fixture_path.stat().st_mtime, tz=UTC
            ).isoformat()
            index[requested_url] = {
                "captured_at": captured_at,
                "path": relative_path,
            }
            continue

        if captured_count:
            time.sleep(REQUEST_INTERVAL_SECONDS)

        network_url, _ = urldefrag(requested_url)
        response = session.get(
            network_url,
            impersonate="chrome120",
            timeout=60,
        )
        response.raise_for_status()

        fixture_path.parent.mkdir(parents=True, exist_ok=True)
        fixture_path.write_bytes(response.content)
        index[requested_url] = {
            "captured_at": datetime.now(tz=UTC).isoformat(),
            "path": relative_path,
        }
        captured_count += 1
        print(f"Captured {requested_url} -> {relative_path}")

    index_path.write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parse_args = argparse.ArgumentParser(
        description="Capture Baseball Reference pages for offline tests."
    )
    parse_args.add_argument(
        "--force-regen",
        action="store_true",
        help="Regenerate all fixtures, even if they already exist.",
    )
    args = parse_args.parse_args()
    main(force_regen=args.force_regen)
