"""Retrosheet's biographical tables and legacy Game Logs reference files."""

from pathlib import Path

import polars as pl

from ._retrosheet_logs import ArchivePath, _id, _options
from ._utils.retrosheet_archives import DAILY, GAMES, archive_members, named_link

_LEGACY_PEOPLE = "Player, Manager, Coach, Umpire IDs"


def _reference(
    member: str,
    columns: tuple[str, ...],
    value: str,
    archive_path: ArchivePath | None,
    *,
    label: str = "Biographical Files",
) -> pl.DataFrame:
    if value is None:
        raise TypeError("A Retrosheet ID is required")
    local = _options(False, archive_path, False)
    source = local or named_link(
        DAILY if label == "Biographical Files" else GAMES, label
    )
    (path,) = archive_members(
        source, (member,), keep_zip=label in {"Biographical Files", _LEGACY_PEOPLE}
    )
    return _read_reference(path, columns, value)


def _read_reference(path: Path, columns: tuple[str, ...], value: str) -> pl.DataFrame:
    try:
        frame = pl.scan_csv(path, infer_schema=False)
        return frame.filter(
            pl.any_horizontal(pl.col(name) == value for name in columns)
        ).collect()
    except pl.exceptions.PolarsError as exc:
        raise RuntimeError(
            f"Cannot parse Retrosheet reference table {path.name}"
        ) from exc


def ballparks(*, park_id: str, archive_path: ArchivePath | None = None) -> pl.DataFrame:
    """Look up a ballpark in the Daily Logs companion tables."""
    _id("park_id", park_id, r"[A-Z0-9]{5}")
    return _reference("ballparks0.csv", ("site",), park_id, archive_path)


def people_bios(
    *, person_id: str, archive_path: ArchivePath | None = None
) -> pl.DataFrame:
    """Look up a person's biography and role dates by Retrosheet ID."""
    _id("person_id", person_id, r"[a-z0-9-]{5}[0-9]{3}")
    return _reference("biofile0.csv", ("id",), person_id, archive_path)


def coaches(*, coach_id: str, archive_path: ArchivePath | None = None) -> pl.DataFrame:
    """Return a coach's Daily Logs team-season assignments."""
    _id("coach_id", coach_id, r"[a-z0-9-]{5}[0-9]{3}")
    return _reference("coaches0.csv", ("id",), coach_id, archive_path)


def managers(
    *, manager_id: str, archive_path: ArchivePath | None = None
) -> pl.DataFrame:
    """Look up an in-game manager's name and first and last game."""
    _id("manager_id", manager_id, r"[a-z0-9-]{5}[0-9]{3}")
    return _reference("managers0.csv", ("id",), manager_id, archive_path)


def relatives(
    *, person_id: str, archive_path: ArchivePath | None = None
) -> pl.DataFrame:
    """Return biographical relationships with the person on either side."""
    _id("person_id", person_id, r"[a-z0-9-]{5}[0-9]{3}")
    return _reference("relatives.csv", ("id1", "id2"), person_id, archive_path)


def teams(*, team_id: str, archive_path: ArchivePath | None = None) -> pl.DataFrame:
    """Look up a team in the Daily Logs companion tables."""
    _id("team_id", team_id, r"[A-Z0-9]{3}")
    return _reference("teams0.csv", ("team",), team_id, archive_path)


def umpires(*, umpire_id: str, archive_path: ArchivePath | None = None) -> pl.DataFrame:
    """Look up an umpire's name and first and last game."""
    _id("umpire_id", umpire_id, r"[a-z0-9-]{5}[0-9]{3}")
    return _reference("umpires0.csv", ("id",), umpire_id, archive_path)


def people_ids(
    *, person_id: str, archive_path: ArchivePath | None = None
) -> pl.DataFrame:
    """Look up a person in the Game Logs biographical register."""
    _id("person_id", person_id, r"[a-z0-9-]{5}[0-9]{3}")
    return _reference(
        "biofile.csv", ("PLAYERID",), person_id, archive_path, label=_LEGACY_PEOPLE
    )


def coach_assignments(
    *, coach_id: str, archive_path: ArchivePath | None = None
) -> pl.DataFrame:
    """Return the Game Logs reference dates for a coach's assignments."""
    _id("coach_id", coach_id, r"[a-z0-9-]{5}[0-9]{3}")
    return _reference(
        "coaches.csv", ("id",), coach_id, archive_path, label=_LEGACY_PEOPLE
    )


def ballpark_codes(
    *, park_id: str, archive_path: ArchivePath | None = None
) -> pl.DataFrame:
    """Look up a Game Logs ballpark code, including aliases and notes."""
    _id("park_id", park_id, r"[A-Z0-9]{5}")
    return _reference(
        "ballparks.csv",
        ("PARKID",),
        park_id,
        archive_path,
        label="Ballpark Codes (for field 17 in game logs)",
    )


def franchise_codes(
    *, team_id: str, archive_path: ArchivePath | None = None
) -> pl.DataFrame:
    """Return the Game Logs franchise history for a team code."""
    _id("team_id", team_id, r"[A-Z0-9]{3}")
    return _reference(
        "teams.csv", ("TEAM",), team_id, archive_path, label="Franchise/Team IDs"
    )
