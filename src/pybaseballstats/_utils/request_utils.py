"""Fetch and parse data from endpoints that use plain HTTP GET requests."""

import io
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

import polars as pl
import requests

P = ParamSpec("P")
T = TypeVar("T")


def source_schema_errors(function: Callable[P, T]) -> Callable[P, T]:
    """Add operation context to source CSV schema failures."""
    function_name = getattr(function, "__name__", type(function).__name__)

    @wraps(function)
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return function(*args, **kwargs)
        except pl.exceptions.PolarsError as exc:
            raise RuntimeError(
                f"{function_name}: invalid Baseball Savant source columns"
            ) from exc
        except RuntimeError as exc:
            if str(exc).startswith(f"{function_name}:"):
                raise
            raise RuntimeError(f"{function_name}: {exc}") from exc

    return wrapped


def _get(
    url: str, *, params: dict[str, str | list[str]] | None = None
) -> requests.Response:
    kwargs: dict[str, Any] = {"timeout": 30}
    if params is not None:
        kwargs["params"] = params
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"GET failed for {url}") from exc
    return response


def get_csv(url: str, **read_csv_kwargs: Any) -> pl.DataFrame:
    text = _get(url).text
    if text.lstrip().lower().startswith(("<!doctype html", "<html")):
        raise RuntimeError(f"CSV endpoint returned HTML for {url}")
    try:
        return pl.read_csv(io.StringIO(text), **read_csv_kwargs)
    except (pl.exceptions.PolarsError, ValueError) as exc:
        raise RuntimeError(f"CSV parsing failed for {url}") from exc


def get_json(url: str) -> Any:
    try:
        return _get(url).json()
    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError(f"JSON parsing failed for {url}") from exc


def get_text(url: str, *, params: dict[str, str | list[str]] | None = None) -> str:
    return _get(url, params=params).text


def get_bytes(url: str) -> bytes:
    return _get(url).content
