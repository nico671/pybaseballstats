"""Game Logs and originally planned schedules."""

import csv
from typing import Literal, TypeAlias

import polars as pl

from .._consts.retrosheet_tables import (
    GAME_LOG_COLUMNS,
    GAME_LOG_NUMERIC,
    SCHEDULE_COLUMNS,
)
from .._utils.retrosheet_archives import (
    GAMES,
    SCHEDULES,
    archive_members,
    named_link,
    season_links,
)
from ._common import (
    ArchivePath,
    Result,
    _enum,
    _id,
    _options,
    _result,
    _validate_season,
)

GameType: TypeAlias = Literal[
    "regular",
    "world_series",
    "all_star",
    "wild_card",
    "division_series",
    "league_championship",
    "chronicle_telegraph_cup",
]
_EVENTS = {
    "world_series": ("World Series", "glws.txt"),
    "all_star": ("All-Star", "glas.txt"),
    "wild_card": ("WildCard Game", "glwc.txt"),
    "division_series": ("Division Series", "gldv.txt"),
    "league_championship": ("LCS", "gllc.txt"),
    "chronicle_telegraph_cup": ("Chronicle-Telegraph Cup", "glct.txt"),
}


def game_logs(
    *,
    season: int,
    team_id: str | None = None,
    game_type: GameType = "regular",
    force_collect: bool = False,
    archive_path: ArchivePath | None = None,
) -> Result:
    """Return Retrosheet's 161-field game logs for a season and game type."""
    _validate_season(season)
    if season is None:
        raise TypeError("season must be an integer")
    _id("team_id", team_id, r"[A-Z0-9]{3}")
    _enum("game_type", game_type, ("regular", *_EVENTS))
    local = _options(force_collect, archive_path, False)
    if game_type == "regular":
        source = local or season_links(GAMES, season)[season]
        member = f"gl{season}.txt"
    else:
        label, member = _EVENTS[game_type]
        source = local or named_link(GAMES, label)
    (path,) = archive_members(source, (member,))
    schema = {
        name: pl.Int64 if name in GAME_LOG_NUMERIC else pl.String
        for name in GAME_LOG_COLUMNS
    }
    frame = (
        pl.scan_csv(path, has_header=False, schema=schema, raise_if_empty=False)
        .with_columns(pl.col("date").str.to_date("%Y%m%d"))
        .filter(pl.col("date").dt.year() == season)
    )
    if team_id is not None:
        frame = frame.filter(
            (pl.col("home_team") == team_id) | (pl.col("visitor_team") == team_id)
        )
    return _result(frame, force_collect, "game_logs")


def schedules(
    *,
    season: int,
    team_id: str | None = None,
    force_collect: bool = False,
    archive_path: ArchivePath | None = None,
) -> Result:
    """Return originally planned games and known postponement details."""
    _validate_season(season)
    if season is None:
        raise TypeError("season must be an integer")
    _id("team_id", team_id, r"[A-Z0-9]{3}")
    local = _options(force_collect, archive_path, False)
    source = local or season_links(SCHEDULES, season)[season]
    members = (
        ("2020sched-orig.csv", "2020schedule.csv")
        if season == 2020
        else (f"{season}schedule.csv",)
    )
    versions = ("original", "revised") if season == 2020 else ("original",)
    paths = archive_members(source, members)
    scans = []
    for path, version in zip(paths, versions, strict=True):
        try:
            with path.open(encoding="utf-8-sig", newline="") as data:
                header = next(csv.reader(data), [])
        except (OSError, UnicodeError, csv.Error) as exc:
            raise RuntimeError(
                f"Cannot read Retrosheet schedule header in {path.name}"
            ) from exc
        expected = [
            "Date",
            "Num",
            "Day",
            "Visitor",
            "League",
            "Game",
            "Home",
            "League",
            "Game",
            "Day/Night",
            "Postponed",
            "Makeup",
        ]
        columns = SCHEDULE_COLUMNS
        has_park = header[10:11] == ["Location"]
        if has_park:
            expected.insert(10, "Location")
            columns = [*columns[:10], "park_id", *columns[10:]]
        if header != expected:
            raise RuntimeError(f"Unexpected Retrosheet schedule header in {path.name}")
        frame = pl.scan_csv(
            path,
            has_header=False,
            skip_rows=1,
            schema=dict.fromkeys(columns, pl.String),
        ).with_columns(
            pl.col("date").str.to_date("%Y%m%d"),
            pl.col("visitor_game_number", "home_game_number").cast(pl.Int64),
            pl.lit(version).alias("schedule_version"),
        )
        if not has_park:
            frame = frame.with_columns(pl.lit(None, dtype=pl.String).alias("park_id"))
        frame = frame.select(
            *SCHEDULE_COLUMNS[:10],
            "park_id",
            *SCHEDULE_COLUMNS[10:],
            "schedule_version",
        )
        scans.append(frame)
    result = pl.concat(scans)
    if team_id is not None:
        result = result.filter(
            (pl.col("home_team") == team_id) | (pl.col("visitor_team") == team_id)
        )
    return _result(result, force_collect, "schedules")
