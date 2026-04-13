from __future__ import annotations

from core.experiments.scenarios import ScenarioDefinition

#from experiments.scenarios.s01_corridor_baseline import (
#    build as build_s01_corridor_baseline,
#)
#from experiments.scenarios.s02_corridor_static import build as build_s02_corridor_static
#from experiments.scenarios.s03_long_slow_zone_corridor import (
#    build as build_s03_long_slow_zone_corridor,
#)
#from experiments.scenarios.s04_short_slow_zone_corridor import (
#    build as build_s04_short_slow_zone_corridor,
#)
#from experiments.scenarios.s05_dynamic_obstacle_corridor import (
#    build as build_s05_dynamic_obstacle_corridor,
#)
#from experiments.scenarios.s06_dynamic_zone_then_block import (
#    build as build_s06_dynamic_zone_then_block,
#)
#from experiments.scenarios.s07_complex_dynamic_maze import (
#    build as build_s07_complex_dynamic_maze,
#)
#from experiments.scenarios.s08_update_storm_corridor import (
#    build as build_s08_update_storm_corridor,
#)
#from experiments.scenarios.s09_bridge_cutoff_offpath_noise import (
#    build as build_s09_bridge_cutoff_offpath_noise,
#)
from experiments.scenarios.sf1_s01_baseline_reference import (
    build as build_sf1_s01_baseline_reference,
)
from experiments.scenarios.sf1_s02_on_path_obstacle_middle_gate import (
    build as build_sf1_s02_on_path_obstacle_middle_gate,
)
from experiments.scenarios.sf1_s03_same_event_later_timing import (
    build as build_sf1_s03_same_event_later_timing,
)
from experiments.scenarios.sf2_s01_persistent_on_path_slow_zone import (
    build as build_sf2_s01_persistent_on_path_slow_zone,
)
from experiments.scenarios.sf2_s02_ttl_zone_same_position import (
    build as build_sf2_s02_ttl_zone_same_position,
)
from experiments.scenarios.sf2_s03_pulse_zone_same_position import (
    build as build_sf2_s03_pulse_zone_same_position,
)
from experiments.scenarios.sf3_s01_single_off_path_zone import (
    build as build_sf3_s01_single_off_path_zone,
)
from experiments.scenarios.sf3_s02_repeated_off_path_updates import (
    build as build_sf3_s02_repeated_off_path_updates,
)
from experiments.scenarios.sf3_s03_off_path_update_storm import (
    build as build_sf3_s03_off_path_update_storm,
)
from experiments.scenarios.sf4_s01_off_path_noise_then_on_path_obstacle import (
    build as build_sf4_s01_off_path_noise_then_on_path_obstacle,
)
from experiments.scenarios.sf4_s02_off_path_noise_then_on_path_slow_zone import (
    build as build_sf4_s02_off_path_noise_then_on_path_slow_zone,
)
from experiments.scenarios.sf4_s03_near_path_zone_then_central_blockade import (
    build as build_sf4_s03_near_path_zone_then_central_blockade,
)
from experiments.scenarios.sf5_s01_shortcut_opens import (
    build as build_sf5_s01_shortcut_opens,
)
from experiments.scenarios.sf5_s02_cost_disappears_on_alternative_route import (
    build as build_sf5_s02_cost_disappears_on_alternative_route,
)

SCENARIO_BUILDERS = (
    build_sf1_s01_baseline_reference,
    build_sf1_s02_on_path_obstacle_middle_gate,
    build_sf1_s03_same_event_later_timing,
    build_sf2_s01_persistent_on_path_slow_zone,
    build_sf2_s02_ttl_zone_same_position,
    build_sf2_s03_pulse_zone_same_position,
    build_sf3_s01_single_off_path_zone,
    build_sf3_s02_repeated_off_path_updates,
    build_sf3_s03_off_path_update_storm,
    build_sf4_s01_off_path_noise_then_on_path_obstacle,
    build_sf4_s02_off_path_noise_then_on_path_slow_zone,
    build_sf4_s03_near_path_zone_then_central_blockade,
    build_sf5_s01_shortcut_opens,
    build_sf5_s02_cost_disappears_on_alternative_route

    #build_s01_corridor_baseline,
    #build_s02_corridor_static,
    #build_s03_long_slow_zone_corridor,
    #build_s04_short_slow_zone_corridor,
    #build_s05_dynamic_obstacle_corridor,
    #build_s06_dynamic_zone_then_block,
    #build_s07_complex_dynamic_maze,
    #build_s08_update_storm_corridor,
    #build_s09_bridge_cutoff_offpath_noise
)


def required_scenarios() -> tuple[ScenarioDefinition, ...]:
    return tuple(builder() for builder in SCENARIO_BUILDERS)


def scenario_by_name(name: str) -> ScenarioDefinition:
    scenarios = {scenario.name: scenario for scenario in required_scenarios()}
    try:
        return scenarios[name]
    except KeyError as exc:
        raise ValueError(f"Unknown scenario: {name}") from exc
