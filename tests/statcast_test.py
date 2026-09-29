import asyncio

import polars as pl
import pytest

import pybaseballstats.statcast as sc
from pybaseballstats import _statcast as sc_impl
from pybaseballstats._utils import statcast_utils
from pybaseballstats.enums import StatcastTeams


@pytest.mark.live
def test_pitch_by_pitch_data_errors():
    """Test error handling in pitch_by_pitch_data."""
    with pytest.raises(ValueError):
        sc.pitch_by_pitch_data(start_date=None, end_date="2023-07-01")
    with pytest.raises(ValueError):
        sc.pitch_by_pitch_data(start_date="2023-07-01", end_date=None)

    df = sc.pitch_by_pitch_data(start_date="2023-07-01", end_date="2023-07-02")
    assert df is not None
    assert isinstance(df, pl.LazyFrame)


def test_pitch_by_pitch_data_fails_gracefully_when_chunk_fails(monkeypatch):
    async def _mock_fetch_all_data(*args, **kwargs):
        raise RuntimeError(
            "Statcast download failed to retrieve all requested chunks after retries. "
            "1/2 chunk(s) failed. Data integrity policy prevented returning partial data."
        )

    monkeypatch.setattr(sc_impl, "_fetch_all_data", _mock_fetch_all_data)

    with pytest.raises(
        RuntimeError, match="Unable to complete Statcast pitch-by-pitch"
    ):
        sc.pitch_by_pitch_data(start_date="2023-07-01", end_date="2023-07-02")


def test_statcast_loader_unions_columns_and_keeps_chunk_order(tmp_path):
    first_chunk = tmp_path / "chunk-1.csv"
    second_chunk = tmp_path / "chunk-2.csv"
    first_chunk.write_text("a\n1\n", encoding="utf-8")
    second_chunk.write_text("a,b\n2,later\n", encoding="utf-8")

    result = pl.concat(
        statcast_utils._load_all_data([first_chunk, second_chunk], show_progress=False)
    ).collect()

    assert result.columns == ["a", "b"]
    assert result.get_column("a").to_list() == [1, 2]
    assert result.get_column("b").to_list() == [None, "later"]


@pytest.mark.asyncio
async def test_streamed_chunk_retries_invalid_csv(monkeypatch, tmp_path):
    bodies = [
        b"<html>server error</html>",
        b'game_date,pitcher\n"broken,123\n',
        b"game_date,pitcher\n2025-04-01,808967\n",
    ]

    class Response:
        status = 200

        def __init__(self, body):
            self.body = body
            self.content = self

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            pass

        async def iter_chunked(self, _size):
            yield self.body

    class Session:
        def get(self, _url):
            return Response(bodies.pop(0))

    async def no_sleep(_seconds):
        pass

    monkeypatch.setattr(statcast_utils.asyncio, "sleep", no_sleep)
    path = tmp_path / "chunk.csv"
    result = await statcast_utils._fetch_and_parse_chunk(
        Session(), "test", asyncio.Semaphore(1), max_retries=3, output_path=path
    )

    assert result.source_path == path
    assert not bodies
    assert path.read_bytes() == b"game_date,pitcher\n2025-04-01,808967\n"


@pytest.mark.asyncio
async def test_streamed_empty_chunk_keeps_schema(monkeypatch, tmp_path):
    class Response:
        status = 200
        content = None

        def __init__(self, body):
            self.body = body
            self.content = self

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            pass

        async def iter_chunked(self, _size):
            yield self.body

    class Session:
        def __init__(self, body):
            self.body = body

        def get(self, _url):
            return Response(self.body)

    empty_path = tmp_path / "empty.csv"
    empty = await statcast_utils._fetch_and_parse_chunk(
        Session(b"game_date,pitcher\n"),
        "empty",
        asyncio.Semaphore(1),
        output_path=empty_path,
    )
    assert empty.source_path == empty_path
    assert empty_path.exists()

    valid_path = tmp_path / "valid.csv"
    valid = await statcast_utils._fetch_and_parse_chunk(
        Session(b"game_date,pitcher\n2025-04-01,808967\n"),
        "valid",
        asyncio.Semaphore(1),
        output_path=valid_path,
    )

    async def fake_fetch(_session, url, _semaphore, output_path=None):
        return empty if url == "empty" else valid

    monkeypatch.setattr(statcast_utils, "_fetch_and_parse_chunk", fake_fetch)
    sources = await statcast_utils._fetch_all_data(
        ["empty", "valid"], 2, output_dir=tmp_path, show_progress=False
    )
    assert sources == [empty_path, valid_path]
    frame = statcast_utils._load_all_data(sources, show_progress=False)[0].collect()
    assert frame.schema["pitcher"] == pl.Int64
    assert frame["pitcher"].to_list() == [808967]


@pytest.mark.asyncio
@pytest.mark.parametrize("streamed", [False, True])
async def test_malformed_chunk_fails_with_parse_cause(tmp_path, streamed):
    class Response:
        status = 200

        def __init__(self):
            self.content = self

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            pass

        async def read(self):
            return b"game_date,pitcher\n2025-04-01,808967,extra\n"

        async def iter_chunked(self, _size):
            yield await self.read()

    class Session:
        def get(self, _url):
            return Response()

    path = tmp_path / "malformed.csv" if streamed else None
    result = await statcast_utils._fetch_and_parse_chunk(
        Session(), "malformed", asyncio.Semaphore(1), max_retries=1, output_path=path
    )
    assert result.dataframe is None and result.source_path is None
    assert isinstance(result.cause, pl.exceptions.PolarsError)
    if path is not None:
        assert not path.exists()


def test_statcast_lazy_source_lives_after_return(monkeypatch):
    paths = []

    async def fake_fetch(_urls, _days, **kwargs):
        path = kwargs["output_dir"] / "chunk.csv"
        path.write_text("game_date,pitcher\n2025-04-01,808967\n")
        paths.append(path)
        return [path]

    monkeypatch.setattr(sc_impl, "_fetch_all_data", fake_fetch)
    frame = sc.pitch_by_pitch_data("2025-04-01", "2025-04-01", show_progress=False)
    assert isinstance(frame, pl.LazyFrame)
    assert paths[0].exists()
    assert frame.collect()["pitcher"].to_list() == [808967]
    assert frame.filter(pl.col("pitcher") == 808967).collect().height == 1


def test_statcast_failed_call_cleans_temporary_files(monkeypatch):
    paths = []

    async def fake_fetch(_urls, _days, **kwargs):
        path = kwargs["output_dir"] / "chunk.csv"
        path.write_text("game_date\n2025-04-01\n")
        paths.append(path)
        raise RuntimeError("failed chunk")

    monkeypatch.setattr(sc_impl, "_fetch_all_data", fake_fetch)
    with pytest.raises(RuntimeError, match="Unable to complete Statcast"):
        sc.pitch_by_pitch_data("2025-04-01", "2025-04-01", show_progress=False)
    assert not paths[0].exists()


def test_eager_collection_wraps_polars_error(monkeypatch):
    async def fake_fetch(_urls, _days, **kwargs):
        return [pl.DataFrame({"game_date": ["2025-04-01"], "pitcher": ["bad"]})]

    monkeypatch.setattr(sc_impl, "_fetch_all_data", fake_fetch)
    monkeypatch.setattr(
        sc_impl,
        "_load_all_data",
        lambda *_args, **_kwargs: [
            pl.DataFrame({"pitcher": ["bad"]})
            .lazy()
            .select(pl.col("pitcher").cast(pl.Int64))
        ],
    )
    with pytest.raises(RuntimeError, match="pitch_by_pitch_data") as caught:
        sc.pitch_by_pitch_data(
            "2025-04-01", "2025-04-01", force_collect=True, show_progress=False
        )
    assert isinstance(caught.value.__cause__, pl.exceptions.PolarsError)


@pytest.mark.parametrize("force_collect", [False, True])
def test_all_empty_success_keeps_schema(monkeypatch, force_collect):
    async def fake_fetch(_urls, _days, **kwargs):
        return [pl.DataFrame(schema={"game_date": pl.String, "pitcher": pl.Int64})]

    monkeypatch.setattr(sc_impl, "_fetch_all_data", fake_fetch)
    result = sc.pitch_by_pitch_data(
        "2025-04-01", "2025-04-01", force_collect=force_collect, show_progress=False
    )
    assert isinstance(result, pl.DataFrame if force_collect else pl.LazyFrame)
    frame = result if force_collect else result.collect()
    assert frame.is_empty()
    assert frame.schema == {"game_date": pl.String, "pitcher": pl.Int64}


@pytest.mark.asyncio
async def test_statcast_download_keeps_request_order_with_progress(monkeypatch):
    async def fetch_in_reverse_completion_order(
        session, url, semaphore, max_retries=3, output_path=None
    ):
        await asyncio.sleep(0.02 if url == "first" else 0)
        return statcast_utils.ChunkFetchResult(
            url=url,
            dataframe=pl.DataFrame({"chunk": [url]}),
        )

    monkeypatch.setattr(
        statcast_utils, "_fetch_and_parse_chunk", fetch_in_reverse_completion_order
    )

    result = await statcast_utils._fetch_all_data(
        ["first", "second"], 2, concurrency=2, show_progress=True
    )

    assert [
        frame.get_column("chunk").item()
        for frame in result
        if isinstance(frame, pl.DataFrame)
    ] == ["first", "second"]


@pytest.mark.parametrize("show_progress", [False, True])
def test_statcast_loader_unions_in_memory_columns(show_progress):
    responses = [
        pl.DataFrame({"value": [1], "other": [3]}),
        pl.DataFrame({"other": [4]}),
    ]

    frame = statcast_utils._load_all_data(responses, show_progress=show_progress)[
        0
    ].collect()
    assert frame.columns == ["value", "other"]
    assert frame["value"].to_list() == [1, None]
    assert frame["other"].to_list() == [3, 4]


@pytest.mark.live
def test_pitch_by_pitch_data_general():
    """Test general functionality of pitch_by_pitch_data."""
    df = sc.pitch_by_pitch_data(
        start_date="2023-07-01", end_date="2023-07-03", force_collect=True
    )
    assert df is not None
    assert isinstance(df, pl.DataFrame)
    assert df.shape[0] == 12227
    assert df.shape[1] == 119
    assert df.select(pl.col("game_date").min()).item() == "2023-07-01"
    assert df.select(pl.col("game_date").max()).item() == "2023-07-03"
    assert df.select(pl.col("game_pk").n_unique()).item() == 41
    assert df.select(pl.col("player_name").n_unique()).item() == 296


@pytest.mark.live
def test_pitch_by_pitch_data_team_none_returns_all():
    """Ensure no filtering is applied when team is None."""
    df = sc.pitch_by_pitch_data(
        start_date="2023-07-03", end_date="2023-07-03", team=None, force_collect=True
    )
    assert df is not None
    assert isinstance(df, pl.DataFrame)
    assert df.select(pl.col("home_team").n_unique()).item() > 1
    assert df.select(pl.col("away_team").n_unique()).item() > 1


@pytest.mark.live
def test_pitch_by_pitch_data_team_filtering():
    """Test team filtering of pitch_by_pitch_data."""
    df = sc.pitch_by_pitch_data(
        start_date="2023-07-01",
        end_date="2023-07-03",
        team=StatcastTeams.DODGERS,
        force_collect=True,
    )
    assert df is not None
    assert isinstance(df, pl.DataFrame)
    assert df.shape[1] == 119
    assert df.select(pl.col("game_date").min()).item() == "2023-07-01"
    assert df.select(pl.col("game_date").max()).item() == "2023-07-03"

    dodgers_games = (pl.col("home_team") == "LAD") | (pl.col("away_team") == "LAD")
    assert df.filter(
        ~dodgers_games
    ).is_empty()  # Filters out non Dodger rows and there should be none
    assert df.shape[0] > 0


def test_pitch_by_pitch_data_invalid_team():
    """Tests for AttributeError exception to be raised when you try to access a nonexistent enum member"""
    with pytest.raises(AttributeError):
        sc.pitch_by_pitch_data(
            start_date="2023-07-01",
            end_date="2023-07-03",
            team=StatcastTeams.METZ,
        )
