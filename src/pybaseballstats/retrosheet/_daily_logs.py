"""Daily Logs, including parsed play-by-play and player and team statistics."""

from datetime import datetime
from pathlib import Path
from typing import Literal, TypeAlias

import polars as pl

from .._consts.retrosheet_tables import PLAY_COLUMNS, PLAYER_LOG_COLUMNS, daily_type
from .._utils.retrosheet_archives import (
    DAILY,
    PLAYS,
    ROOT,
    ArchiveMemberAbsent,
    ArchiveNotFound,
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

StatType: TypeAlias = Literal["value", "official", "lower", "upper", "all"]
_COLLECTIONS = {
    "american_national_league": "American/National League",
    "federal_league": "Federal League",
    "negro_leagues": "Negro Leagues",
    "regular": "Regular Season Games",
    "all_star": "All-Star Games",
    "postseason": "Postseason Games",
    "tiebreakers": "Tiebreaker Playoff Games",
    "three_home_runs": "3+ Home Run Games (by an individual)",
    "fifteen_strikeouts": "15+ Strikeouts (by an individual)",
    "twenty_innings": "20+ Inning Games",
    "twenty_runs": "20+ Runs Scored (by one team)",
    "cycles": "(Batting) Cycles",
    "interracial_exhibition": "Interracial Exhibition Games",
    "no_hitters": "No-Hitters",
    "triple_plays": "Triple Plays",
}
_PLAYER_STATS = {"batting.csv": "b", "pitching.csv": "p", "fielding.csv": "f"}
_BULK_COLLECTIONS = {"american_national_league", "negro_leagues", "regular"}


def _daily_scan(
    path: Path, member: str, *, archive_season: int | None = None
) -> pl.LazyFrame:
    try:
        frame = pl.scan_csv(path, infer_schema=False, raise_if_empty=False)
        names = frame.collect_schema().names()
        required = {
            "allplayers.csv": {"id", "team"},
            "plays.csv": {"gid", "pn", "batter", "pitcher", "site"},
            "gameinfo.csv": {"gid", "visteam", "hometeam", "site"},
            "teamstats.csv": {"gid", "team", "stattype"},
            "manager.csv": {"gid", "mgr", "eject"},
            "umpire.csv": {"gid", "uid", "eject"},
        }.get(member, {"gid", "id", "team", "stattype"})
        if missing := required.difference(names):
            raise RuntimeError(
                f"Missing Retrosheet columns in {path.name}: {sorted(missing)}"
            )
        expressions = []
        for name in names:
            dtype = daily_type(member, name)
            if dtype is pl.Date:
                expressions.append(
                    pl.col(name)
                    .replace({"0": None, "00000000": None})
                    .str.to_date("%Y%m%d")
                )
            elif dtype is pl.Int64:
                expressions.append(pl.col(name).replace("?", None).cast(pl.Int64))
        if member in _PLAYER_STATS and "eject" not in names:
            expressions.append(pl.lit(None, dtype=pl.String).alias("eject"))
        frame = frame.with_columns(expressions)
        if member == "allplayers.csv" and "season" not in names:
            season = (
                pl.lit(archive_season, dtype=pl.Int64)
                if archive_season is not None
                else pl.col("first_g").dt.year().cast(pl.Int64)
            )
            frame = frame.with_columns(season.alias("season"))
        return frame
    except pl.exceptions.PolarsError as exc:
        raise RuntimeError(f"Cannot scan Retrosheet table {path.name}") from exc


def _career_seasons(player_id: str) -> set[int]:
    (path,) = archive_members(named_link(DAILY, "allplayers.csv"), ("allplayers.csv",))
    frame = _daily_scan(path, "allplayers.csv")
    try:
        return set(
            frame.filter(pl.col("id") == player_id)
            .select(pl.col("season").drop_nulls().unique())
            .collect()
            .get_column("season")
            .to_list()
        )
    except pl.exceptions.PolarsError as exc:
        raise RuntimeError("Cannot read Retrosheet player seasons") from exc


def _play_role(player_id: str, names: list[str]) -> pl.Expr:
    runner_columns = (
        "batter",
        "pitcher",
        "br1_pre",
        "br2_pre",
        "br3_pre",
        "br1_post",
        "br2_post",
        "br3_post",
        "run_b",
        "run1",
        "run2",
        "run3",
    )
    matches = [pl.col(name) == player_id for name in runner_columns if name in names]
    for position in range(2, 10):
        fielder = f"f{position}"
        if fielder not in names:
            continue
        actions = [
            pl.col(name) > 0
            for name in (f"po{position}", f"a{position}", f"e{position}")
            if name in names
        ]
        if position == 2 and "pb" in names:
            actions.append(pl.col("pb") > 0)
        actions.extend(
            pl.col(name) == position
            for name in (
                "firstf",
                "batout1",
                "batout2",
                "batout3",
                "brout_b",
                "brout1",
                "brout2",
                "brout3",
            )
            if name in names
        )
        if actions:
            matches.append((pl.col(fielder) == player_id) & pl.any_horizontal(actions))
    return pl.any_horizontal(matches)


def _daily_filter(
    frame: pl.LazyFrame,
    member: str,
    season: int | None,
    game_id: str | None,
    player_id: str | None,
    team_id: str | None,
    park_id: str | None,
    stattype: StatType | None,
) -> pl.LazyFrame:
    if season is not None:
        year = (
            pl.col("season")
            if member in {"allplayers.csv", "gameinfo.csv"}
            else pl.col("gid").str.slice(3, 4).cast(pl.Int64)
        )
        frame = frame.filter(year == season)
    if game_id is not None:
        frame = frame.filter(pl.col("gid") == game_id)
    if player_id is not None:
        frame = frame.filter(
            _play_role(player_id, frame.collect_schema().names())
            if member == "plays.csv"
            else pl.col("id") == player_id
        )
    if team_id is not None:
        teams = {
            "plays.csv": ("batteam", "pitteam"),
            "gameinfo.csv": ("visteam", "hometeam"),
        }.get(member, ("team",))
        frame = frame.filter(
            pl.any_horizontal(pl.col(name) == team_id for name in teams)
        )
    if park_id is not None:
        frame = frame.filter(pl.col("site") == park_id)
    if stattype is not None and stattype != "all":
        frame = frame.filter(pl.col("stattype") == stattype)
    return frame


def _season_daily(member: str, season: int) -> pl.LazyFrame:
    listing = PLAYS if member == "plays.csv" else DAILY
    try:
        urls = season_links(listing, season)
    except ValueError:
        if listing != PLAYS:
            raise
        listing = DAILY
        urls = season_links(DAILY, season)
    return _scan_season_archive(member, season, urls[season], keep_zip=listing == DAILY)


def _scan_season_archive(
    member: str, season: int, url: str, *, keep_zip: bool
) -> pl.LazyFrame:
    (path,) = archive_members(
        url,
        (f"{season}{member}",),
        keep_zip=keep_zip,
        alternatives=(member,),
    )
    return _daily_scan(path, member, archive_season=season)


def _bulk_daily(member: str, allow: bool) -> pl.LazyFrame:
    if not allow:
        raise ValueError(
            f"Retrosheet {member} requires a bulk archive for this query. "
            "Provide archive_path or set allow_bulk_download=True."
        )
    label = (
        "Download Parsed Play-by-Play for All Games"
        if member == "plays.csv"
        else member
    )
    (path,) = archive_members(
        named_link(PLAYS if member == "plays.csv" else DAILY, label),
        (member,),
        bulk=True,
    )
    return _daily_scan(path, member)


def _empty_plays() -> pl.LazyFrame:
    return pl.LazyFrame(
        schema={name: daily_type("plays.csv", name) for name in PLAY_COLUMNS}
    )


def _career_plays(player_id: str) -> pl.LazyFrame:
    seasons = _career_seasons(player_id)
    if not seasons:
        return _empty_plays()
    plays = season_links(PLAYS, expected_seasons=seasons)
    missing = seasons.difference(plays)
    daily = season_links(DAILY, expected_seasons=missing) if missing else {}
    available = daily | plays
    scans = [
        _scan_season_archive(
            "plays.csv", year, available[year], keep_zip=year not in plays
        )
        for year in sorted(seasons.intersection(available))
    ]
    return pl.concat(scans) if scans else _empty_plays()


def _player_daily(
    player_id: str, member: str, *, local: Path | None = None, season: int | None = None
) -> pl.LazyFrame:
    suffix = _PLAYER_STATS[member]
    player_member = f"{player_id}_{suffix}.csv"
    requested = player_member if local is None else f"{season or ''}{member}"
    try:
        (path,) = archive_members(
            local or ROOT + f"downloads/players/{player_id}.zip",
            (requested,),
            keep_zip=True,
            alternatives=(member, player_member) if local is not None else (),
            optional_with=tuple(
                f"{player_id}_{other}.csv"
                for other in _PLAYER_STATS.values()
                if other != suffix
            ),
        )
    except ArchiveMemberAbsent:
        return pl.LazyFrame(
            schema={
                name: daily_type(member, name) for name in PLAYER_LOG_COLUMNS[member]
            }
        )
    return _daily_scan(path, member)


def _local_daily(local: Path, member: str, season: int | None) -> pl.LazyFrame:
    if season is None:
        (path,) = archive_members(local, (member,))
        return _daily_scan(path, member)
    if member == "allplayers.csv":
        try:
            (path,) = archive_members(
                local, (f"{season}{member}",), optional_with=(member,)
            )
        except ArchiveMemberAbsent:
            (path,) = archive_members(local, (member,))
            return _daily_scan(path, member)
    else:
        (path,) = archive_members(local, (f"{season}{member}",), alternatives=(member,))
    return _daily_scan(path, member, archive_season=season)


def _team_daily(team_id: str, season: int | None, member: str) -> pl.LazyFrame:
    key = f"{season if season is not None else ''}{team_id}"
    try:
        (path,) = archive_members(
            ROOT + f"downloads/teams/{key}.zip",
            (member,),
            keep_zip=True,
        )
    except ArchiveNotFound:
        if season is None:
            raise
        return _season_daily(member, season)
    return _daily_scan(path, member, archive_season=season)


def _collection_daily(
    collection: str, member: str, season: int | None, detailed: bool, allow_bulk: bool
) -> pl.LazyFrame:
    broad = collection in _BULK_COLLECTIONS
    if broad and not allow_bulk:
        raise ValueError(
            "This Retrosheet collection requires archive_path or allow_bulk_download=True"
        )
    if detailed and season is None and not allow_bulk:
        raise ValueError(
            "Detailed collection rows require a season, archive_path, or bulk download"
        )
    (path,) = archive_members(
        named_link(DAILY, _COLLECTIONS[collection]),
        (member,),
        keep_zip=True,
        bulk=broad,
    )
    selected = _daily_scan(path, member)
    if not detailed:
        return selected
    full = (
        _bulk_daily(member, allow_bulk)
        if season is None
        else _season_daily(member, season)
    )
    return full.join(selected.select("gid"), on="gid", how="semi")


def _daily_query(
    member: str,
    *,
    season: int | None,
    game_id: str | None = None,
    player_id: str | None = None,
    team_id: str | None = None,
    park_id: str | None = None,
    stattype: StatType | None = None,
    collection: str | None,
    force_collect: bool,
    archive_path: ArchivePath | None,
    allow_bulk_download: bool,
) -> Result:
    local = _options(force_collect, archive_path, allow_bulk_download)
    _validate_season(season)
    _id("game_id", game_id, r"[A-Z0-9]{3}[0-9]{8}[0-9AB]")
    _id("player_id", player_id, r"[a-z0-9-]{5}[0-9]{3}")
    _id("team_id", team_id, r"[A-Z0-9]{3}")
    _id("park_id", park_id, r"[A-Z0-9]{5}")
    if member in _PLAYER_STATS or member == "teamstats.csv":
        _enum("stattype", stattype, ("value", "official", "lower", "upper", "all"))
    if collection is not None:
        _enum("collection", collection, _COLLECTIONS)
    if game_id is not None:
        year = datetime.strptime(game_id[3:11], "%Y%m%d").year
        if season is not None and season != year:
            raise ValueError("season must match the year in game_id")
        season = year
    if all(
        value is None for value in (season, player_id, team_id, park_id, collection)
    ):
        raise ValueError("Supply a Retrosheet season, ID, or collection")
    detailed = stattype not in {None, "value"}
    if local is not None:
        try:
            if player_id is not None and member in _PLAYER_STATS:
                frame = _player_daily(player_id, member, local=local, season=season)
            else:
                frame = _local_daily(local, member, season)
        except RuntimeError as exc:
            if season is None and isinstance(exc.__cause__, KeyError):
                raise RuntimeError(
                    f"{exc}. For a daily season ZIP, supply season or game_id."
                ) from exc
            raise
    elif collection is not None:
        frame = _collection_daily(
            collection, member, season, detailed, allow_bulk_download
        )
    elif player_id is not None and member in _PLAYER_STATS:
        frame = _player_daily(player_id, member)
    elif team_id is not None and not detailed and member != "plays.csv":
        frame = _team_daily(team_id, season, member)
    elif season is not None:
        frame = _season_daily(member, season)
    elif player_id is not None and member == "plays.csv":
        frame = _career_plays(player_id)
    elif member == "plays.csv":
        # Team and park ZIPs can omit older plays that are in season archives.
        raise ValueError(
            "For team or park plays, supply season, game_id, player_id, collection, "
            "or archive_path."
        )
    elif player_id is not None and member == "allplayers.csv":
        (path,) = archive_members(named_link(DAILY, member), (member,))
        frame = _daily_scan(path, member)
    elif park_id is not None and not detailed:
        (path,) = archive_members(
            ROOT + f"downloads/ballparks/{park_id}.zip",
            (member,),
            keep_zip=True,
        )
        frame = _daily_scan(path, member)
    else:
        frame = _bulk_daily(member, allow_bulk_download)
    return _result(
        _daily_filter(
            frame, member, season, game_id, player_id, team_id, park_id, stattype
        ),
        force_collect,
        member,
    )


def player_seasons(
    *,
    season: int | None = None,
    player_id: str | None = None,
    team_id: str | None = None,
    collection: str | None = None,
    force_collect: bool = False,
    archive_path: ArchivePath | None = None,
    allow_bulk_download: bool = False,
) -> Result:
    """Return one row per player, team, and season from Daily Logs."""
    return _daily_query(
        "allplayers.csv",
        season=season,
        player_id=player_id,
        team_id=team_id,
        collection=collection,
        force_collect=force_collect,
        archive_path=archive_path,
        allow_bulk_download=allow_bulk_download,
    )


def game_info(
    *,
    season: int | None = None,
    game_id: str | None = None,
    team_id: str | None = None,
    park_id: str | None = None,
    collection: str | None = None,
    force_collect: bool = False,
    archive_path: ArchivePath | None = None,
    allow_bulk_download: bool = False,
) -> Result:
    """Return game-level metadata from Daily Logs."""
    return _daily_query(
        "gameinfo.csv",
        season=season,
        game_id=game_id,
        team_id=team_id,
        park_id=park_id,
        collection=collection,
        force_collect=force_collect,
        archive_path=archive_path,
        allow_bulk_download=allow_bulk_download,
    )


def team_logs(
    *,
    season: int | None = None,
    game_id: str | None = None,
    team_id: str | None = None,
    park_id: str | None = None,
    stattype: StatType = "value",
    collection: str | None = None,
    force_collect: bool = False,
    archive_path: ArchivePath | None = None,
    allow_bulk_download: bool = False,
) -> Result:
    """Return team statistics, line scores, and starting lineups by game."""
    return _daily_query(
        "teamstats.csv",
        season=season,
        game_id=game_id,
        team_id=team_id,
        park_id=park_id,
        stattype=stattype,
        collection=collection,
        force_collect=force_collect,
        archive_path=archive_path,
        allow_bulk_download=allow_bulk_download,
    )


def batting_logs(
    *,
    season: int | None = None,
    game_id: str | None = None,
    player_id: str | None = None,
    team_id: str | None = None,
    stattype: StatType = "value",
    collection: str | None = None,
    force_collect: bool = False,
    archive_path: ArchivePath | None = None,
    allow_bulk_download: bool = False,
) -> Result:
    """Return player batting statistics by game."""
    return _daily_query(
        "batting.csv",
        season=season,
        game_id=game_id,
        player_id=player_id,
        team_id=team_id,
        stattype=stattype,
        collection=collection,
        force_collect=force_collect,
        archive_path=archive_path,
        allow_bulk_download=allow_bulk_download,
    )


def pitching_logs(
    *,
    season: int | None = None,
    game_id: str | None = None,
    player_id: str | None = None,
    team_id: str | None = None,
    stattype: StatType = "value",
    collection: str | None = None,
    force_collect: bool = False,
    archive_path: ArchivePath | None = None,
    allow_bulk_download: bool = False,
) -> Result:
    """Return player pitching statistics by game."""
    return _daily_query(
        "pitching.csv",
        season=season,
        game_id=game_id,
        player_id=player_id,
        team_id=team_id,
        stattype=stattype,
        collection=collection,
        force_collect=force_collect,
        archive_path=archive_path,
        allow_bulk_download=allow_bulk_download,
    )


def fielding_logs(
    *,
    season: int | None = None,
    game_id: str | None = None,
    player_id: str | None = None,
    team_id: str | None = None,
    stattype: StatType = "value",
    collection: str | None = None,
    force_collect: bool = False,
    archive_path: ArchivePath | None = None,
    allow_bulk_download: bool = False,
) -> Result:
    """Return player fielding statistics by game and position."""
    return _daily_query(
        "fielding.csv",
        season=season,
        game_id=game_id,
        player_id=player_id,
        team_id=team_id,
        stattype=stattype,
        collection=collection,
        force_collect=force_collect,
        archive_path=archive_path,
        allow_bulk_download=allow_bulk_download,
    )


def plays(
    *,
    season: int | None = None,
    game_id: str | None = None,
    player_id: str | None = None,
    team_id: str | None = None,
    park_id: str | None = None,
    collection: str | None = None,
    force_collect: bool = False,
    archive_path: ArchivePath | None = None,
    allow_bulk_download: bool = False,
) -> Result:
    """Return recorded plays that match the supplied game or player filters."""
    return _daily_query(
        "plays.csv",
        season=season,
        game_id=game_id,
        player_id=player_id,
        team_id=team_id,
        park_id=park_id,
        collection=collection,
        force_collect=force_collect,
        archive_path=archive_path,
        allow_bulk_download=allow_bulk_download,
    )
