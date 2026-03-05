from __future__ import annotations

from core.experiments.scenarios import ScenarioDefinition

from experiments.scenarios.s01_corridor_baseline import (
    build as build_s01_corridor_baseline,
)
from experiments.scenarios.s02_corridor_static import build as build_s02_corridor_static
from experiments.scenarios.s03_long_slow_zone_corridor import (
    build as build_s03_long_slow_zone_corridor,
)
from experiments.scenarios.s04_short_slow_zone_corridor import (
    build as build_s04_short_slow_zone_corridor,
)
from experiments.scenarios.s05_dynamic_obstacle_corridor import (
    build as build_s05_dynamic_obstacle_corridor,
)
from experiments.scenarios.s06_dynamic_zone_then_block import (
    build as build_s06_dynamic_zone_then_block,
)
from experiments.scenarios.s07_complex_dynamic_maze import (
    build as build_s07_complex_dynamic_maze,
)
from experiments.scenarios.s08_update_storm_corridor import (
    build as build_s08_update_storm_corridor,
)

SCENARIO_BUILDERS = (
    build_s01_corridor_baseline,
    build_s02_corridor_static,
    build_s03_long_slow_zone_corridor,
    build_s04_short_slow_zone_corridor,
    build_s05_dynamic_obstacle_corridor,
    build_s06_dynamic_zone_then_block,
    build_s07_complex_dynamic_maze,
    build_s08_update_storm_corridor
)


def required_scenarios() -> tuple[ScenarioDefinition, ...]:
    return tuple(builder() for builder in SCENARIO_BUILDERS)


def scenario_by_name(name: str) -> ScenarioDefinition:
    scenarios = {scenario.name: scenario for scenario in required_scenarios()}
    try:
        return scenarios[name]
    except KeyError as exc:
        raise ValueError(f"Unknown scenario: {name}") from exc
