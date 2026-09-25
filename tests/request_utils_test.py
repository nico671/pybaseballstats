import polars as pl
import pytest
import requests

from pybaseballstats._utils import request_utils


def test_response_helpers_check_status_and_set_timeout(monkeypatch):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        response = requests.Response()
        response.status_code = 503 if url.endswith("error") else 200
        response._content = b'{"rows": [1]}' if url.endswith("json") else b"R\n3\n"
        return response

    monkeypatch.setattr(request_utils.requests, "get", fake_get)

    assert request_utils.get_csv("https://example.test/csv").equals(
        pl.DataFrame({"R": [3]})
    )
    assert request_utils.get_json("https://example.test/json") == {"rows": [1]}
    assert request_utils.get_text("https://example.test/text") == "R\n3\n"
    assert request_utils.get_bytes("https://example.test/bytes") == b"R\n3\n"
    with pytest.raises(requests.HTTPError):
        request_utils.get_csv("https://example.test/error")
    assert all(kwargs["timeout"] == 30 for _, kwargs in calls)
