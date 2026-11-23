"""Manager and umpire game logs and ejection records."""

from datetime import datetime
from typing import Optional

import polars as pl

from .._consts.retrosheet_consts import EJECTIONS_URL
from .._utils.request_utils import get_bytes
from .._utils.retrosheet_archives import ROOT, archive_members
from ._common import ArchivePath, Result, _id, _options, _result
from ._daily_logs import _daily_scan


def manager_logs(
    *,
    manager_id: str,
    force_collect: bool = False,
    archive_path: ArchivePath | None = None,
) -> Result:
    """Return a manager's game logs and ejection flags."""
    _id("manager_id", manager_id, r"[a-z0-9-]{5}[0-9]{3}")
    if manager_id is None:
        raise TypeError("manager_id must be a string")
    local = _options(force_collect, archive_path, False)
    source = local or ROOT + f"downloads/managers/{manager_id}_mgr.zip"
    (path,) = archive_members(source, (f"{manager_id}_mlog.csv",))
    frame = _daily_scan(path, "manager.csv").filter(pl.col("mgr") == manager_id)
    return _result(frame, force_collect, "manager_logs")


def umpire_logs(
    *,
    umpire_id: str,
    force_collect: bool = False,
    archive_path: ArchivePath | None = None,
) -> Result:
    """Return an umpire's game logs and per-game ejection counts."""
    _id("umpire_id", umpire_id, r"[a-z0-9-]{5}[0-9]{3}")
    if umpire_id is None:
        raise TypeError("umpire_id must be a string")
    local = _options(force_collect, archive_path, False)
    source = local or ROOT + f"downloads/umpires/{umpire_id}_ump.zip"
    (path,) = archive_members(source, (f"{umpire_id}_ulog.csv",))
    frame = _daily_scan(path, "umpire.csv").filter(pl.col("uid") == umpire_id)
    return _result(frame, force_collect, "umpire_logs")


def ejections_data(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    ejectee_name: Optional[str] = None,
    umpire_name: Optional[str] = None,
    inning: Optional[int] = None,
) -> pl.DataFrame:
    """Return MLB ejections from Retrosheet with optional filters.

    Args:
        start_date (str | None, optional): Inclusive start date in ``MM/DD/YYYY``.
        end_date (str | None, optional): Inclusive end date in ``MM/DD/YYYY``.
        ejectee_name (str | None, optional): Substring filter on ``EJECTEENAME``.
        umpire_name (str | None, optional): Substring filter on ``UMPIRENAME``.
        inning (int | None, optional): Inning filter from -1 to 20.

    Raises:
        ValueError: If ``start_date`` is not in ``MM/DD/YYYY`` format.
        ValueError: If ``end_date`` is not in ``MM/DD/YYYY`` format.
        ValueError: If ``start_date`` is after ``end_date``.
        ValueError: If ``inning`` is outside -1 to 20.

    Returns:
        pl.DataFrame: Ejection rows matching the provided filters.
    """
    start_dt = None
    if start_date is not None and not isinstance(start_date, str):
        raise TypeError("start_date must be a string or None")
    if end_date is not None and not isinstance(end_date, str):
        raise TypeError("end_date must be a string or None")
    if ejectee_name is not None and not isinstance(ejectee_name, str):
        raise TypeError("ejectee_name must be a string or None")
    if umpire_name is not None and not isinstance(umpire_name, str):
        raise TypeError("umpire_name must be a string or None")
    if inning is not None and type(inning) is not int:
        raise TypeError("inning must be an integer or None")
    if inning is not None and not -1 <= inning <= 20:
        raise ValueError("inning must be between -1 and 20")

    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%m/%d/%Y")
        except ValueError:
            raise ValueError("start_date must be in 'MM/DD/YYYY' format")

    end_dt = None
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%m/%d/%Y")
        except ValueError:
            raise ValueError("end_date must be in 'MM/DD/YYYY' format")

    if start_dt and end_dt and start_dt > end_dt:
        raise ValueError("start_date must be before end_date")

    try:
        scan = pl.scan_csv(
            get_bytes(EJECTIONS_URL),
            infer_schema_length=None,
            truncate_ragged_lines=True,
            schema_overrides={"INNING": pl.String},
        )
        required = {"DATE", "INNING", "EJECTEENAME", "UMPIRENAME"}
        if not required.issubset(scan.collect_schema().names()):
            raise RuntimeError("ejections_data: missing Retrosheet columns")
        scan = scan.with_columns(pl.col("DATE").str.to_date("%m/%d/%Y"))
        scan = scan.filter(pl.col("INNING") != "Cy Rigler")
        scan = scan.with_columns(pl.col("INNING").cast(pl.Int8))
        df = scan.collect()
    except (pl.exceptions.PolarsError, RuntimeError) as exc:
        raise RuntimeError(
            "ejections_data: could not retrieve or parse Retrosheet CSV"
        ) from exc

    if start_dt:
        df = df.filter(pl.col("DATE") >= start_dt)
    if end_dt:
        df = df.filter(pl.col("DATE") <= end_dt)

    if df.is_empty():
        print("Warning: No ejections found for the given date range.")
        return df

    if ejectee_name:
        df = df.filter(pl.col("EJECTEENAME").str.contains(ejectee_name, literal=True))
        if df.shape[0] == 0:
            print("Warning: No ejections found for the given ejectee name.")
            return df

    if umpire_name:
        df = df.filter(pl.col("UMPIRENAME").str.contains(umpire_name, literal=True))
        if df.shape[0] == 0:
            print("Warning: No ejections found for the given umpire name.")
            return df

    if inning is not None:
        df = df.filter(pl.col("INNING") == inning)
        if df.shape[0] == 0:
            print("Warning: No ejections found for the given inning.")
            return df

    return df
