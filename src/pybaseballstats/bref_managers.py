"""Public bref managers data interface."""

from ._bref_managers import managers_basic_data as managers_basic_data
from ._bref_managers import managers_tendencies_data as managers_tendencies_data

__all__ = [
    "managers_basic_data",
    "managers_tendencies_data",
]


def __dir__() -> list[str]:
    return __all__
