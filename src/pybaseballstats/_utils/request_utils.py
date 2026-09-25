"""Fetch and parse data from endpoints that use plain HTTP GET requests."""

import io
from typing import Any

import polars as pl
import requests


def _get(
    url: str, *, params: dict[str, str | list[str]] | None = None
) -> requests.Response:
    kwargs: dict[str, Any] = {"timeout": 30}
    if params is not None:
        kwargs["params"] = params
    response = requests.get(url, **kwargs)
    response.raise_for_status()
    return response


def get_csv(url: str, **read_csv_kwargs: Any) -> pl.DataFrame:
    return pl.read_csv(io.StringIO(_get(url).text), **read_csv_kwargs)


def get_json(url: str) -> Any:
    return _get(url).json()


def get_text(url: str, *, params: dict[str, str | list[str]] | None = None) -> str:
    return _get(url, params=params).text


def get_bytes(url: str) -> bytes:
    return _get(url).content
