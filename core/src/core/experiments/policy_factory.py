from __future__ import annotations

from collections.abc import Callable
from typing import Any

from core.simulation import (
    EventBasedReplanPolicy,
    PathAffectedReplanPolicy,
    PeriodicReplanPolicy,
    ReplanPolicy,
    StaticOnceReplanPolicy,
)


def _validate_param_keys(policy_name: str, params: dict[str, Any], allowed_keys: set[str]) -> None:
    unknown_keys = sorted(set(params) - allowed_keys)
    if unknown_keys:
        allowed = ", ".join(sorted(allowed_keys)) or "<none>"
        unknown = ", ".join(unknown_keys)
        raise ValueError(
            f"Invalid parameter(s) for policy '{policy_name}': {unknown}. "
            f"Allowed parameter(s): {allowed}."
        )


def _make_static_once(params: dict[str, Any]) -> ReplanPolicy:
    _validate_param_keys("static_once", params, set())
    return StaticOnceReplanPolicy()


def _make_event_based(params: dict[str, Any]) -> ReplanPolicy:
    _validate_param_keys("event_based", params, set())
    return EventBasedReplanPolicy()


def _make_periodic(params: dict[str, Any]) -> ReplanPolicy:
    _validate_param_keys("periodic", params, {"interval"})
    interval = params.get("interval", 1)
    try:
        interval_ticks = int(interval)
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid parameter for policy 'periodic': interval must be an integer.") from exc
    try:
        return PeriodicReplanPolicy(interval_ticks=interval_ticks)
    except ValueError as exc:
        raise ValueError(f"Invalid parameter for policy 'periodic': {exc}") from exc


def _make_path_affected(params: dict[str, Any]) -> ReplanPolicy:
    _validate_param_keys("path_affected", params, {"cost_delta_threshold"})
    threshold = params.get("cost_delta_threshold", 0.0)
    try:
        cost_delta_threshold = float(threshold)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Invalid parameter for policy 'path_affected': cost_delta_threshold must be numeric."
        ) from exc
    return PathAffectedReplanPolicy(cost_delta_threshold=cost_delta_threshold)


_POLICY_REGISTRY: dict[str, Callable[[dict[str, Any]], ReplanPolicy]] = {
    "static_once": _make_static_once,
    "event_based": _make_event_based,
    "periodic": _make_periodic,
    "path_affected": _make_path_affected,
}


def make_policy(policy_name: str, params: dict[str, Any]) -> ReplanPolicy:
    try:
        builder = _POLICY_REGISTRY[policy_name]
    except KeyError as exc:
        allowed = ", ".join(sorted(_POLICY_REGISTRY))
        raise ValueError(
            f"Unknown policy '{policy_name}'. Allowed policies: {allowed}."
        ) from exc
    return builder(params)
