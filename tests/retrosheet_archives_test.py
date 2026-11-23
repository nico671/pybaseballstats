"""Archive routing, storage, and live Retrosheet format checks."""

import csv
from contextlib import contextmanager
from io import BytesIO, StringIO
from zipfile import ZipFile

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from pybaseballstats import retrosheet as rs
from pybaseballstats._consts.retrosheet_tables import GAME_LOG_COLUMNS
from pybaseballstats._utils import retrosheet_archives as archives

_PLAYER = "ohtas001"
_GAME = "LAN202503270"


def _zip(members: dict[str, str | bytes]) -> bytes:
    output = BytesIO()
    with ZipFile(output, "w") as zipped:
        for name, payload in members.items():
            zipped.writestr(name, payload)
    return output.getvalue()


@pytest.fixture(autouse=True)
def workspace(monkeypatch):
    monkeypatch.delenv(archives.LIMIT_VARIABLE, raising=False)
    archives._workspace.cache_clear()
    archives._listings.clear()
    yield
    if archives._workspace.cache_info().currsize:
        archives._workspace().cleanup()
    archives._workspace.cache_clear()
    archives._listings.clear()


@pytest.fixture
def sources(monkeypatch):
    responses = {}
    fetched = []
    streamed = []

    @contextmanager
    def response(url):
        fetched.append(url)
        data = responses[url]
        if isinstance(data, list):
            data = data.pop(0)

        class Response:
            content = data
            headers = {"Content-Length": str(len(data))}

            def iter_content(self, _chunk_size):
                streamed.append(url)
                yield data

        yield Response()

    monkeypatch.setattr(archives, "_response", response)
    return responses, fetched, streamed


def test_refresh_season_catalog_and_reuse_download(sources):
    responses, fetched, _ = sources
    url = archives.ROOT + "downloads/2025-renamed.zip"
    responses[archives.DAILY] = [
        b'<a href="old.zip">2024</a>',
        b'<a href="2025-renamed.zip">2025</a>',
    ]
    responses[url] = _zip(
        {
            "2025batting.csv": f"gid,id,team,stattype,b_h\n{_GAME},{_PLAYER},LAN,value,2\n",
            "2025fielding.csv": f"gid,id,team,stattype,d_pos,d_seq\n{_GAME},{_PLAYER},LAN,value,1,1\n",
        }
    )
    first = rs.batting_logs(season=2025)
    assert rs.fielding_logs(season=2025, force_collect=True)["d_pos"].item() == 1
    assert first.select("b_h").collect().item() == 2
    assert fetched == [archives.DAILY, archives.DAILY, url]


def test_invalid_filters_do_not_fetch_sources(sources):
    _, fetched, _ = sources
    with pytest.raises(ValueError, match="Supply"):
        rs.plays()
    with pytest.raises(ValueError, match="must match"):
        rs.plays(season=2024, game_id=_GAME)
    with pytest.raises(TypeError, match="season"):
        rs.schedules(season=True)
    with pytest.raises(ValueError, match="bulk"):
        rs.team_logs(team_id="LAN", stattype="official")
    assert fetched == []


def test_missing_season_refresh_and_broken_listing(sources):
    responses, fetched, _ = sources
    responses[archives.PLAYS] = b'<a href="2025.zip">2025</a>'
    responses[archives.DAILY] = b'<a href="daily2025.zip">2025</a>'
    with pytest.raises(ValueError, match="2026 is not published"):
        rs.plays(season=2026)
    assert fetched == [archives.PLAYS, archives.PLAYS, archives.DAILY, archives.DAILY]
    responses[archives.SCHEDULES] = b"<p>Temporary maintenance</p>"
    with pytest.raises(RuntimeError, match="No season"):
        rs.schedules(season=2026)


def test_player_plays_downloads_exact_career_seasons(sources):
    responses, fetched, _ = sources
    responses[archives.DAILY] = (
        b'<a href="registry.zip">allplayers.csv</a><a href="daily2025.zip">2025</a>'
    )
    registry = archives.ROOT + "downloads/registry.zip"
    responses[registry] = _zip(
        {
            "allplayers.csv": "id,team,season\n"
            f"{_PLAYER},ANA,2023\n{_PLAYER},LAN,2023\n{_PLAYER},LAN,2025\n"
            f"{_PLAYER},LAN,2026\n"
        }
    )
    responses[archives.PLAYS] = b"".join(
        f'<a href="{year}.zip">{year}</a>'.encode() for year in (2023, 2024, 2025)
    )
    header = "gid,pn,batter,pitcher,site,br1_pre,f2,po2,firstf\n"
    for year in (2023, 2025):
        game = f"LAN{year}03270"
        rows = (
            f"{game},1,other001,other002,LAX01,{_PLAYER},other003,0,0\n"
            f"{game},2,other001,other002,LAX01,,{_PLAYER},1,2\n"
            f"{game},3,other001,other002,LAX01,,{_PLAYER},0,0\n"
            f"{game},4,{_PLAYER},other002,LAX01,{_PLAYER},,0,0\n"
        )
        responses[archives.ROOT + f"downloads/{year}.zip"] = _zip(
            {f"{year}plays.csv": header + rows}
        )
    result = rs.plays(player_id=_PLAYER, force_collect=True)
    assert result["pn"].to_list() == [1, 2, 4, 1, 2, 4]
    assert fetched == [
        archives.DAILY,
        registry,
        archives.PLAYS,
        archives.PLAYS,
        archives.DAILY,
        archives.ROOT + "downloads/2023.zip",
        archives.ROOT + "downloads/2025.zip",
    ]
    assert rs.plays(player_id="other999", force_collect=True).is_empty()


def test_player_archive_without_pitching_rows(sources):
    responses, fetched, _ = sources
    url = archives.ROOT + f"downloads/players/{_PLAYER}.zip"
    responses[url] = _zip(
        {
            f"{_PLAYER}_b.csv": f"gid,id,team,stattype,b_h,eject\n{_GAME},{_PLAYER},LAN,value,2,y\n"
        }
    )
    pitching = rs.pitching_logs(player_id=_PLAYER, force_collect=True)
    assert pitching.is_empty()
    assert pitching.schema["p_ipouts"] == pl.Int64
    assert pitching.schema["date"] == pl.Date
    assert (
        rs.batting_logs(player_id=_PLAYER, season=2025, force_collect=True)[
            "eject"
        ].item()
        == "y"
    )
    assert fetched == [url]


@pytest.mark.parametrize("listing", [archives.PLAYS, archives.DAILY])
def test_player_plays_refreshes_catalogs_for_new_season(sources, listing):
    responses, fetched, _ = sources
    registry_link = b'<a href="registry.zip">allplayers.csv</a>'
    stale = b'<a href="old.zip">2025</a>'
    new = b'<a href="new.zip">2026</a>'
    responses[archives.DAILY] = registry_link + stale
    responses[archives.PLAYS] = stale
    prefix = registry_link if listing == archives.DAILY else b""
    responses[listing] = [prefix + stale, prefix + stale + new]
    archives.season_links(archives.PLAYS)
    archives.season_links(archives.DAILY)
    responses[archives.ROOT + "downloads/registry.zip"] = _zip(
        {"allplayers.csv": f"id,team,season\n{_PLAYER},LAN,2026\n"}
    )
    responses[archives.ROOT + "downloads/new.zip"] = _zip(
        {
            "2026plays.csv": f"gid,pn,batter,pitcher,site\nLAN202603270,1,{_PLAYER},other002,LAX01\n"
        }
    )
    assert rs.plays(player_id=_PLAYER).select("gid").collect().item() == "LAN202603270"
    assert fetched.count(listing) == 2


def test_passed_ball_matches_only_the_catcher(tmp_path):
    path = tmp_path / "plays.zip"
    path.write_bytes(
        _zip(
            {
                "2025plays.csv": "gid,pn,batter,pitcher,site,f2,f3,po2,a2,e2,pb\n"
                f"{_GAME},1,other001,other002,LAX01,{_PLAYER},other003,0,0,0,1\n"
                f"{_GAME},2,other001,other002,LAX01,other003,{_PLAYER},0,0,0,1\n"
            }
        )
    )
    assert (
        rs.plays(player_id=_PLAYER, season=2025, archive_path=path)
        .select("pn")
        .collect()
        .item()
        == 1
    )


@pytest.mark.parametrize("force_collect", [False, True])
def test_local_player_archive_without_pitching_rows(tmp_path, sources, force_collect):
    _, fetched, _ = sources
    path = tmp_path / "player.zip"
    path.write_bytes(
        _zip(
            {f"{_PLAYER}_b.csv": f"gid,id,team,stattype\n{_GAME},{_PLAYER},LAN,value\n"}
        )
    )
    result = rs.pitching_logs(
        player_id=_PLAYER, season=2025, archive_path=path, force_collect=force_collect
    )
    assert isinstance(result, pl.DataFrame if force_collect else pl.LazyFrame)
    pitching = result.collect() if isinstance(result, pl.LazyFrame) else result
    assert pitching.is_empty()
    assert pitching.schema["p_ipouts"] == pl.Int64
    assert fetched == []


def test_local_player_seasons_use_row_year_for_unprefixed_member(tmp_path):
    path = tmp_path / "players.zip"
    path.write_bytes(
        _zip(
            {
                "allplayers.csv": f"id,team,first_g\n{_PLAYER},ANA,20230401\n"
                f"{_PLAYER},LAN,20250327\n{_PLAYER},NYA,0\n"
            }
        )
    )
    result = rs.player_seasons(season=2025, archive_path=path, force_collect=True)
    assert result.select("season", "team").rows() == [(2025, "LAN")]

    path = tmp_path / "season.zip"
    path.write_bytes(
        _zip({"2025allplayers.csv": f"id,team,first_g\n{_PLAYER},LAN,0\n"})
    )
    assert (
        rs.player_seasons(season=2025, archive_path=path)
        .select("season")
        .collect()
        .item()
        == 2025
    )


@pytest.mark.parametrize("filters", [{"team_id": "BSN"}, {"park_id": "BOS05"}])
def test_team_and_park_plays_use_season_archives(filters, sources):
    responses, fetched, _ = sources
    bundle = archives.ROOT + "downloads/daily1897.zip"
    responses[archives.PLAYS] = b'<a href="1900.zip">1900</a>'
    responses[archives.DAILY] = b'<a href="daily1897.zip">1897</a>'
    responses[bundle] = _zip(
        {
            "1897plays.csv": "gid,pn,batter,pitcher,site,batteam,pitteam\n"
            "BSN189704220,1,other001,other002,BOS05,BSN,BAL\n"
        }
    )
    with pytest.raises(ValueError, match="supply season, game_id"):
        rs.plays(**filters)
    assert fetched == []

    game_id = "BSN189704220"
    assert rs.plays(season=1897, **filters).select("gid").collect().item() == game_id
    assert (
        rs.plays(game_id=game_id, **filters).select("gid").collect().item() == game_id
    )
    assert fetched[:5] == [
        archives.PLAYS,
        archives.PLAYS,
        archives.DAILY,
        bundle,
        archives.PLAYS,
    ]
    assert fetched.count(bundle) == 1


def test_local_season_archive_error_explains_required_filter(tmp_path, sources):
    _, fetched, _ = sources
    path = tmp_path / "season.zip"
    path.write_bytes(
        _zip(
            {
                "2025plays.csv": f"gid,pn,batter,pitcher,site\n{_GAME},1,{_PLAYER},other001,LOS03"
            }
        )
    )
    with pytest.raises(
        RuntimeError, match="For a daily season ZIP, supply season or game_id"
    ):
        rs.plays(park_id="LOS03", archive_path=path)
    assert (
        rs.plays(game_id=_GAME, park_id="LOS03", archive_path=path)
        .select("gid")
        .collect()
        .item()
        == _GAME
    )
    assert fetched == []


def test_local_detailed_archive_requires_no_network(tmp_path, sources):
    _, fetched, _ = sources
    path = tmp_path / "batting.zip"
    path.write_bytes(
        _zip(
            {
                "batting.csv": "gid,id,team,stattype,b_h\n"
                f"{_GAME},{_PLAYER},LAN,value,2\n"
                f"{_GAME},{_PLAYER},LAN,official,1\n"
            }
        )
    )
    kwargs = dict(season=2025, archive_path=path)
    baseline = rs.batting_logs(**kwargs, stattype="all")
    assert_frame_equal(
        baseline.collect(),
        rs.batting_logs(**kwargs, stattype="all", force_collect=True),
    )
    assert (
        rs.batting_logs(**kwargs, stattype="official").select("b_h").collect().item()
        == 1
    )
    assert rs.batting_logs(**kwargs, team_id="NYA").collect().is_empty()
    assert fetched == []


def test_budget_stops_extraction_without_breaking_earlier_scan(tmp_path, monkeypatch):
    monkeypatch.setenv(archives.LIMIT_VARIABLE, "512")
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    first.write_bytes(
        _zip(
            {"batting.csv": f"gid,id,team,stattype,b_h\n{_GAME},{_PLAYER},LAN,value,2"}
        )
    )
    second.write_bytes(_zip({"batting.csv": "x" * 1024}))
    query = rs.batting_logs(season=2025, archive_path=first)
    existing = set(archives._workspace().root.iterdir())
    with pytest.raises(RuntimeError, match="512 byte limit"):
        rs.batting_logs(season=2025, archive_path=second)
    assert set(archives._workspace().root.iterdir()) == existing
    assert query.select("b_h").collect().item() == 2
    assert second.exists()


def test_workspace_checks_streamed_bytes_and_does_not_publish_partial_file(
    monkeypatch, tmp_path
):
    monkeypatch.setenv(archives.LIMIT_VARIABLE, "10")
    ws = archives._workspace()
    path = ws.path(str(tmp_path), "test.zip")
    with pytest.raises(RuntimeError, match="limit exceeded"):
        ws.write(path, [b"1234", b"1234567"], None)
    assert list(ws.root.iterdir()) == []


def test_interrupted_archive_download_can_be_retried(monkeypatch):
    url = archives.ROOT + "downloads/retry.zip"
    payload = _zip({"table.csv": "id\nohtas001\n"})
    attempts = 0

    @contextmanager
    def response(_url):
        nonlocal attempts
        attempts += 1

        class Response:
            headers = {}

            def iter_content(self, _chunk_size):
                if attempts == 1:
                    yield payload[:10]
                    raise OSError("connection interrupted")
                yield payload

        yield Response()

    monkeypatch.setattr(archives, "_response", response)
    with pytest.raises(RuntimeError, match="connection interrupted"):
        archives.archive_members(url, ("table.csv",))
    assert list(archives._workspace().root.iterdir()) == []
    (path,) = archives.archive_members(url, ("table.csv",))
    assert path.read_text() == "id\nohtas001\n"


def test_bulk_warns_before_streaming_once(sources):
    responses, _, streamed = sources
    url = archives.ROOT + "downloads/bulk.zip"
    responses[archives.DAILY] = b'<a href="bulk.zip">teamstats.csv</a>'
    responses[url] = _zip(
        {"teamstats.csv": f"gid,team,stattype\n{_GAME},LAN,official\n"}
    )
    with pytest.warns(UserWarning, match=r"bulk download.*compressed bytes"):
        rs.team_logs(team_id="LAN", stattype="official", allow_bulk_download=True)
    rs.team_logs(team_id="LAN", stattype="official", allow_bulk_download=True)
    assert streamed == [url]


def test_game_log_preserves_positional_fields_and_filters_year(tmp_path):
    output = StringIO()
    row = dict.fromkeys(GAME_LOG_COLUMNS, "")
    row.update(
        date="20251024",
        number="A",
        visitor_team="LAN",
        home_team="TOR",
        visitor_line_score="000010000",
        home_score="2",
        completion="20251025,TOR02,0,0,9",
    )
    csv.DictWriter(output, fieldnames=GAME_LOG_COLUMNS).writerow(row)
    path = tmp_path / "world-series.zip"
    path.write_bytes(_zip({"glws.txt": output.getvalue()}))
    result = rs.game_logs(
        season=2025,
        game_type="world_series",
        team_id="LAN",
        archive_path=path,
        force_collect=True,
    )
    assert result.width == 161
    assert result["number"].item() == "A"
    assert result["visitor_line_score"].item() == "000010000"
    assert result["completion"].item() == "20251025,TOR02,0,0,9"


def test_schedule_versions_and_location(tmp_path):
    header = "Date,Num,Day,Visitor,League,Game,Home,League,Game,Day/Night,"
    path = tmp_path / "schedule.zip"
    path.write_bytes(
        _zip(
            {
                "2020sched-orig.csv": header
                + "Postponed,Makeup\n20200327,0,Fri,LAN,NL,1,SFN,NL,1,D,,\n",
                "2020schedule.csv": header + "Location,Postponed,Makeup\n"
                "20200723,2,Thu,LAN,NL,2,SFN,NL,2,N,LAX01,Rain,20200725;20200726\n",
            }
        )
    )
    result = rs.schedules(season=2020, archive_path=path, force_collect=True)
    assert result["schedule_version"].to_list() == ["original", "revised"]
    assert result["park_id"].to_list() == [None, "LAX01"]
    assert result["makeup"].to_list() == [None, "20200725;20200726"]
    assert result["number"].to_list() == ["0", "2"]


def test_invalid_schedule_encoding_preserves_source_error(tmp_path):
    path = tmp_path / "schedule.zip"
    path.write_bytes(_zip({"2025schedule.csv": b"Date,Num,\xff\n"}))
    with pytest.raises(RuntimeError, match="schedule header") as caught:
        rs.schedules(season=2025, archive_path=path)
    assert isinstance(caught.value.__cause__, UnicodeDecodeError)


@pytest.mark.live
def test_retrosheet_daily_logs_archive():
    logs = rs.batting_logs(season=1948, stattype="official", force_collect=True)
    assert not logs.is_empty()
    assert logs["stattype"].unique().to_list() == ["official"]
    assert logs["gid"].str.slice(3, 4).unique().to_list() == ["1948"]


@pytest.mark.live
def test_retrosheet_legacy_game_logs_archive():
    logs = rs.game_logs(season=2025, team_id="LAN", force_collect=True)
    assert logs.width == 161
    assert not logs.is_empty()
    assert logs["date"].dt.year().unique().to_list() == [2025]
    assert logs.select(
        ((pl.col("visitor_team") == "LAN") | (pl.col("home_team") == "LAN")).all()
    ).item()


@pytest.mark.live
def test_retrosheet_schedule_archive():
    schedules = rs.schedules(season=2020, force_collect=True)
    assert set(schedules["schedule_version"]) == {"original", "revised"}
    assert schedules["date"].dt.year().unique().to_list() == [2020]


@pytest.mark.live
def test_retrosheet_recent_schedule_includes_park():
    schedules = rs.schedules(season=2026, team_id="LAN", force_collect=True)
    assert not schedules.is_empty()
    assert schedules["park_id"].drop_nulls().len() > 0
    assert schedules["date"].dt.year().unique().to_list() == [2026]


@pytest.mark.live
def test_retrosheet_entity_archives():
    player = rs.batting_logs(player_id=_PLAYER, season=2025, force_collect=True)
    assert not player.is_empty()
    assert player["id"].unique().to_list() == [_PLAYER]
    assert "eject" in player.columns
    assert rs.pitching_logs(player_id="judga001", force_collect=True).is_empty()
    team = rs.player_seasons(season=1937, team_id="HOM", force_collect=True)
    assert team["team"].unique().to_list() == ["HOM"]
    assert team["season"].unique().to_list() == [1937]
    assert rs.game_info(park_id="TOK01", force_collect=True)[
        "site"
    ].unique().to_list() == ["TOK01"]
    assert rs.manager_logs(manager_id="weave801", force_collect=True)[
        "mgr"
    ].unique().to_list() == ["weave801"]
    umpire = rs.umpire_logs(umpire_id="millb901", force_collect=True)
    assert umpire["uid"].unique().to_list() == ["millb901"]
    assert umpire.schema["eject"] == pl.Int64


@pytest.mark.live
def test_retrosheet_parsed_plays():
    early = rs.plays(season=1900, force_collect=True)
    assert not early.is_empty()
    assert early.select("gid", "pn").unique().height == early.height
    recent = rs.plays(player_id=_PLAYER, season=2025, force_collect=True)
    assert not recent.is_empty()
    assert recent.select("gid", "pn").unique().height == recent.height
    historical = rs.plays(team_id="BSN", season=1897, force_collect=True)
    assert not historical.is_empty()
    assert historical["gid"].str.slice(3, 4).unique().to_list() == ["1897"]
    park = rs.plays(park_id="BOS05", season=1897, force_collect=True)
    assert park["site"].unique().to_list() == ["BOS05"]
    assert park["gid"].str.slice(3, 4).unique().to_list() == ["1897"]
