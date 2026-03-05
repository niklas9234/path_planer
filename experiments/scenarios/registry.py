from __future__ import annotations

from core.experiments.scenarios import ScenarioDefinition
from experiments.scenarios.blocked_goal_stalls import build as build_blocked_goal_stalls
from experiments.scenarios.empty_world_reaches_goal import (
    build as build_empty_world_reaches_goal,
)
from experiments.scenarios.max_ticks_guard import build as build_max_ticks_guard
from experiments.scenarios.replan_after_obstacle import (
    build as build_replan_after_obstacle,
)
from experiments.scenarios.temporary_slow_zone_expires import (
    build as build_temporary_slow_zone_expires,
)
from experiments.scenarios.testpath_20x20_image_map import (
    build as build_testpath_20x20_image_map,
)

SCENARIO_BUILDERS = (
    build_empty_world_reaches_goal,
    build_blocked_goal_stalls,
    build_replan_after_obstacle,
    build_temporary_slow_zone_expires,
    build_max_ticks_guard,
    build_testpath_20x20_image_map,
)


def required_scenarios() -> tuple[ScenarioDefinition, ...]:
    return tuple(builder() for builder in SCENARIO_BUILDERS)


def scenario_by_name(name: str) -> ScenarioDefinition:
    scenarios = {scenario.name: scenario for scenario in required_scenarios()}
    try:
        return scenarios[name]
    except KeyError as exc:
        raise ValueError(f"Unknown scenario: {name}") from exc
