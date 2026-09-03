"""Static backend registry for reconstruction request compilers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Mapping

from historical_geo.backends.xtent_backend import compile_xtent_solver_input

BACKENDS: dict[str, Callable[[Mapping[str, Any]], dict[str, Any]]] = {
    "xtent": compile_xtent_solver_input,
}


def get_backend(name: str) -> Callable[[Mapping[str, Any]], dict[str, Any]]:
    try:
        return BACKENDS[name]
    except KeyError as error:
        raise ValueError(f"unsupported reconstruction backend: {name}") from error


__all__ = ["BACKENDS", "get_backend", "compile_xtent_solver_input"]
