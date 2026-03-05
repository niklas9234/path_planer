from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from core.domain import DomainEvent, Position, ZoneType
from core.experiments.execution import execute_scenario
from core.planning import Planner, plan
from core.simulation import RunReason, RunResult


@dataclass(frozen=True, slots=True)
class ScenarioExpectation:
    allowed_reasons: tuple[RunReason, ...]
    min_moves: int = 0
    max_moves: int | None = None
    min_replans: int = 0


@dataclass(frozen=True, slots=True)
class ScenarioDefinition:
    name: str
    world_config: WorldConfig
    start: Position
    goal: Position
    initial_obstacles: tuple[Position, ...]
    initial_zones: tuple[ZoneDefinition, ...]
    max_ticks: int
    scheduled_events: dict[int, tuple[DomainEvent, ...]]
    expectation: ScenarioExpectation
    policy_name: str = "event_based"
    policy_params: dict[str, object] = field(default_factory=dict)
    replan_mode: Literal["dynamic_event", "static_once"] | None = None

    def __post_init__(self) -> None:
        """Backwards compatible policy migration.

        `replan_mode` is deprecated and only used as a fallback when `policy_name`
        is not set. If both are provided and conflict, `policy_name` wins.
        """

        if self.replan_mode is None:
            return

        mapped_policy = _policy_name_from_replan_mode(self.replan_mode)
        if self.policy_name:
            return
        object.__setattr__(self, "policy_name", mapped_policy)


def _policy_name_from_replan_mode(
    replan_mode: Literal["dynamic_event", "static_once"],
) -> str:
    if replan_mode == "static_once":
        return "static_once"
    return "event_based"


@dataclass(frozen=True, slots=True)
class WorldConfig:
    width: int
    height: int
    base_cost: float = 1.0
    cell_size_m: float = 1.0


@dataclass(frozen=True, slots=True)
class ZoneDefinition:
    zone_type: ZoneType
    cells: tuple[Position, ...]
    duration_ticks: int | None = None
    extra_cost: float = 0.0


def run_scenario(scenario: ScenarioDefinition, planner: Planner = plan) -> RunResult:
    result, _ = execute_scenario(scenario, planner, max_ticks=scenario.max_ticks)
    return result


def required_scenarios() -> tuple[ScenarioDefinition, ...]:
    """Compatibility shim.

    Scenario content is defined outside the core package under
    `experiments/scenarios/` in the repository root.
    """

    from experiments.scenarios.registry import (
        required_scenarios as root_required_scenarios,
    )

    return root_required_scenarios()


__all__ = [
    "ScenarioDefinition",
    "ScenarioExpectation",
    "WorldConfig",
    "ZoneDefinition",
    "required_scenarios",
    "run_scenario",
]
