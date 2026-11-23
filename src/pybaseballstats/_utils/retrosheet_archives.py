"""Read Retrosheet archive listings and prepare local scan sources."""

import atexit
import os
import re
import shutil
import warnings
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from tempfile import mkdtemp
from threading import RLock
from urllib.parse import urljoin, urlsplit
from zipfile import BadZipFile, ZipFile

import requests
from bs4 import BeautifulSoup

ROOT = "https://www.retrosheet.org/"
DAILY = ROOT + "downloads/csvdownloads.html"
PLAYS = ROOT + "downloads/plays.html"
GAMES = ROOT + "gamelogs/index.html"
SCHEDULES = ROOT + "schedule/index.html"
LIMIT_VARIABLE = "PYBASEBALLSTATS_RETROSHEET_MAX_BYTES"
DEFAULT_LIMIT = 2 * 1024**3
CHUNK_SIZE = 1024 * 1024
_lock = RLock()
_listings: dict[str, BeautifulSoup] = {}


class ArchiveNotFound(RuntimeError):
    """The official server has no file for this route."""


class ArchiveMemberAbsent(Exception):
    """A valid entity ZIP omits an optional table."""


def _official_url(base: str, link: str) -> str:
    url = urljoin(base, link)
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.netloc not in {
        "www.retrosheet.org",
        "retrosheet.org",
    }:
        raise RuntimeError(f"Retrosheet URL is outside its HTTPS site: {url}")
    return url


@contextmanager
def _response(url: str) -> Iterator[requests.Response]:
    try:
        for _ in range(6):
            with requests.get(
                url, timeout=30, stream=True, allow_redirects=False
            ) as response:
                if response.is_redirect:
                    url = _official_url(url, response.headers["Location"])
                    continue
                response.raise_for_status()
                yield response
                return
    except requests.RequestException as exc:
        if exc.response is not None and exc.response.status_code == 404:
            raise ArchiveNotFound(f"No Retrosheet archive at {url}") from exc
        raise RuntimeError(f"GET failed for {url}") from exc
    raise RuntimeError(f"Too many Retrosheet redirects: {url}")


def _listing(url: str) -> BeautifulSoup:
    if url not in _listings:
        with _response(url) as response:
            _listings[url] = BeautifulSoup(response.content, "html.parser")
    return _listings[url]


def _zip_links(url: str, page: BeautifulSoup) -> dict[str, str]:
    links = {}
    for anchor in page.find_all("a", href=True):
        href = str(anchor["href"])
        if urlsplit(href).path.lower().endswith(".zip"):
            label = " ".join(anchor.stripped_strings).casefold()
            # Pages can also link to non-Retrosheet resources.
            if urlsplit(urljoin(url, href)).hostname not in {
                "www.retrosheet.org",
                "retrosheet.org",
            }:
                continue
            links[label] = _official_url(url, href)
    return links


def season_links(
    url: str, season: int | None = None, *, expected_seasons: set[int] | None = None
) -> dict[int, str]:
    expected = {season} if season is not None else (expected_seasons or set())
    with _lock:
        for attempt in range(2):
            links = {
                int(label): link
                for label, link in _zip_links(url, _listing(url)).items()
                if re.fullmatch(r"[0-9]{4}", label)
            }
            if not links:
                raise RuntimeError(f"No season download links found at {url}")
            if expected.issubset(links):
                return links
            if attempt == 0:
                _listings.pop(url)
    if season is None:
        return links
    raise ValueError(f"Season {season} is not published at {url}")


def named_link(url: str, label: str) -> str:
    with _lock:
        links = _zip_links(url, _listing(url))
    if not links:
        raise RuntimeError(f"No archive download links found at {url}")
    for name, link in links.items():
        if re.sub(r" \(\d{4}(?:\s*-\s*\d{4})?\)$", "", name) == label.casefold():
            return link
    raise RuntimeError(f"Download link {label!r} missing from {url}")


class _Workspace:
    def __init__(self) -> None:
        raw_limit = os.environ.get(LIMIT_VARIABLE, str(DEFAULT_LIMIT))
        if not raw_limit.isascii() or not raw_limit.isdecimal() or int(raw_limit) <= 0:
            raise ValueError(f"{LIMIT_VARIABLE} must be a positive integer in bytes")
        self.limit = int(raw_limit)
        self.root = Path(mkdtemp(prefix="pybaseballstats-retrosheet-"))
        self._pid = os.getpid()
        atexit.register(self.cleanup)

    def cleanup(self) -> None:
        if os.getpid() == self._pid:
            shutil.rmtree(self.root, ignore_errors=True)

    def path(self, source: str, member: str) -> Path:
        digest = sha256(f"{source}\n{member}".encode()).hexdigest()
        return self.root / f"{digest}-{Path(member).name}"

    def _check_space(self, used: int, additional: int) -> None:
        if used + additional > self.limit:
            raise RuntimeError(
                f"Retrosheet workspace limit exceeded at {self.root}: "
                f"{used} bytes used, {additional} bytes needed, {self.limit} byte limit. "
                f"Restart Python to clear the workspace. If you need more space, set "
                f"{LIMIT_VARIABLE} to a limit that fits your available disk before restarting."
            )

    def write(self, target: Path, chunks: Iterable[bytes], size: int | None) -> None:
        staged = target.with_suffix(target.suffix + ".part")
        used = sum(path.stat().st_size for path in self.root.iterdir())
        if size is not None:
            self._check_space(used, size)
        try:
            with staged.open("wb") as output:
                for chunk in chunks:
                    self._check_space(used, len(chunk))
                    output.write(chunk)
                    used += len(chunk)
            staged.replace(target)
        finally:
            staged.unlink(missing_ok=True)


@lru_cache(maxsize=1)
def _workspace() -> _Workspace:
    return _Workspace()


def _reset_after_fork() -> None:
    global _lock
    _lock = RLock()
    _workspace.cache_clear()


if hasattr(os, "register_at_fork"):
    os.register_at_fork(after_in_child=_reset_after_fork)


def archive_members(
    source: str | Path,
    members: tuple[str, ...],
    *,
    keep_zip: bool = False,
    bulk: bool = False,
    alternatives: tuple[str, ...] = (),
    optional_with: tuple[str, ...] = (),
) -> tuple[Path, ...]:
    with _lock:
        workspace = _workspace()
        key = str(source)
        archive = (
            source if isinstance(source, Path) else workspace.path(key, "source.zip")
        )
        if isinstance(source, Path):
            try:
                stat = source.stat()
            except OSError as exc:
                raise RuntimeError(f"Cannot open Retrosheet archive {source}") from exc
            key = f"{source.resolve()}:{stat.st_size}:{stat.st_mtime_ns}"
        paths = tuple(workspace.path(key, member) for member in members)
        if all(path.is_file() for path in paths):
            return paths
        downloaded = False
        created = []
        try:
            if isinstance(source, str) and not archive.is_file():
                with _response(source) as response:
                    length = response.headers.get("Content-Length", "")
                    if bulk:
                        size = (
                            f" ({length} compressed bytes)"
                            if length.isdecimal()
                            else ""
                        )
                        warnings.warn(
                            f"Retrosheet bulk download: {source}{size}. Extraction "
                            f"requires additional disk space. The workspace limit is "
                            f"{workspace.limit} bytes and files can stay until process "
                            "exit. The caller is responsible for setting an appropriate limit.",
                            stacklevel=3,
                        )
                    workspace.write(
                        archive,
                        response.iter_content(CHUNK_SIZE),
                        int(length) if length.isdecimal() else None,
                    )
                downloaded = True
            with ZipFile(archive) as zipped:
                entries = {
                    Path(info.filename).name.casefold(): info
                    for info in zipped.infolist()
                    if not info.is_dir()
                }
                for member, path in zip(members, paths, strict=True):
                    if path.is_file():
                        continue
                    entry = next(
                        (
                            entries[name.casefold()]
                            for name in (member, *alternatives)
                            if name.casefold() in entries
                        ),
                        None,
                    )
                    if entry is None:
                        if any(name.casefold() in entries for name in optional_with):
                            raise ArchiveMemberAbsent(member)
                        raise KeyError(member)
                    with zipped.open(entry) as payload:
                        workspace.write(
                            path,
                            iter(lambda: payload.read(CHUNK_SIZE), b""),
                            entry.file_size,
                        )
                    created.append(path)
        except ArchiveNotFound:
            raise
        except (BadZipFile, KeyError, OSError, RuntimeError) as exc:
            for path in created:
                path.unlink(missing_ok=True)
            if downloaded:
                archive.unlink(missing_ok=True)
            raise RuntimeError(
                f"Cannot prepare Retrosheet archive {source}: {exc}"
            ) from exc
        if isinstance(source, str) and not keep_zip:
            archive.unlink()
        return paths
