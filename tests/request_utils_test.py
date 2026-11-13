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
    with pytest.raises(RuntimeError, match="GET failed") as error:
        request_utils.get_csv("https://example.test/error")
    assert isinstance(error.value.__cause__, requests.HTTPError)
    assert all(kwargs["timeout"] == 30 for _, kwargs in calls)


@pytest.mark.parametrize(
    ("body", "function", "message"),
    [
        (b"<!doctype html><title>Just a moment</title>", request_utils.get_csv, "HTML"),
        (b"<html><body>Blocked</body></html>", request_utils.get_csv, "HTML"),
        (b"not json", request_utils.get_json, "JSON parsing failed"),
        (b"a,b\n1,2,3\n", request_utils.get_csv, "CSV parsing failed"),
    ],
)
def test_invalid_success_response_is_a_failure(monkeypatch, body, function, message):
    response = requests.Response()
    response.status_code = 200
    response._content = body
    monkeypatch.setattr(request_utils.requests, "get", lambda *args, **kwargs: response)
    with pytest.raises(RuntimeError, match=message):
        function("https://example.test/data")
