from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any


def _freeze_mapping(values: Mapping[str, Any] | None) -> Mapping[str, Any]:
    frozen = dict(values or {})
    return MappingProxyType(frozen)


def _stable_run_id(*, scenario_name: str, planner_name: str, planner_params: Mapping[str, Any], world_params: Mapping[str, Any]) -> str:
    payload = {
        "planner_name": planner_name,
        "planner_params": dict(planner_params),
        "scenario_name": scenario_name,
        "world_params": dict(world_params),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


@dataclass(frozen=True, slots=True)
class RunContext:
    run_id: str
    scenario_name: str
    planner_name: str
    planner_params: Mapping[str, Any]
    world_params: Mapping[str, Any]
    started_at: datetime
    core_version: str

    @classmethod
    def create(
        cls,
        *,
        scenario_name: str,
        planner_name: str,
        planner_params: Mapping[str, Any] | None,
        world_params: Mapping[str, Any] | None,
        core_version: str,
        started_at: datetime | None = None,
    ) -> RunContext:
        frozen_planner_params = _freeze_mapping(planner_params)
        frozen_world_params = _freeze_mapping(world_params)
        return cls(
            run_id=_stable_run_id(
                scenario_name=scenario_name,
                planner_name=planner_name,
                planner_params=frozen_planner_params,
                world_params=frozen_world_params,
            ),
            scenario_name=scenario_name,
            planner_name=planner_name,
            planner_params=frozen_planner_params,
            world_params=frozen_world_params,
            started_at=started_at or datetime.now(timezone.utc),
            core_version=core_version,
        )
