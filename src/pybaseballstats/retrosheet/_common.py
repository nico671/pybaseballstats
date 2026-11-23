"""Shared argument checks and result handling for Retrosheet archives."""

import re
from os import PathLike
from pathlib import Path
from typing import TypeAlias

import polars as pl

ArchivePath: TypeAlias = str | PathLike[str]
Result: TypeAlias = pl.LazyFrame | pl.DataFrame


def _id(name: str, value: str | None, pattern: str) -> None:
    if value is None:
        return
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if re.fullmatch(pattern, value) is None:
        raise ValueError(f"Invalid Retrosheet {name}: {value!r}")


def _validate_season(season: int | None) -> None:
    if season is not None:
        if type(season) is not int:
            raise TypeError("season must be an integer")
        if not 1000 <= season <= 9999:
            raise ValueError("season must be a four-digit year")


def _options(
    force_collect: bool, archive_path: ArchivePath | None, allow_bulk_download: bool
) -> Path | None:
    for name, value in (
        ("force_collect", force_collect),
        ("allow_bulk_download", allow_bulk_download),
    ):
        if type(value) is not bool:
            raise TypeError(f"{name} must be a boolean")
    if archive_path is not None and not isinstance(archive_path, (str, PathLike)):
        raise TypeError("archive_path must be a path")
    return None if archive_path is None else Path(archive_path)


def _enum(name: str, value: object, choices: tuple[str, ...] | dict[str, str]) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if value not in choices:
        raise ValueError(f"{name} must be one of {', '.join(choices)}")


def _result(frame: pl.LazyFrame, force_collect: bool, label: str) -> Result:
    try:
        frame.collect_schema()
        return frame.collect() if force_collect else frame
    except pl.exceptions.PolarsError as exc:
        raise RuntimeError(f"{label}: invalid Retrosheet source data") from exc
