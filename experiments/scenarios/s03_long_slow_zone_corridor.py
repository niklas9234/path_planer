from core.domain import Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
    ZoneDefinition,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="03_long_slow_zone_corridor",
        policy_name="event_based",
        world_config=WorldConfig(width=12, height=3),
        start=Position(0, 1),
        goal=Position(11, 1),
        initial_obstacles=(),
        initial_zones=(
            ZoneDefinition(
                zone_type=ZoneType.SLOW,
                cells=tuple(Position(x, 1) for x in range(3, 9)),
                extra_cost=10.0,
            ),
        ),
        max_ticks=60,
        scheduled_events={},
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled", "max_ticks"),
            min_moves=1,
        ),
    )
