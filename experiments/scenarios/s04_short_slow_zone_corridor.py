from core.domain import Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
    ZoneDefinition,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="s04_short_slow_zone_corridor",
        policy_name="event_based",
        world_config=WorldConfig(width=12, height=3),
        start=Position(0, 1),
        goal=Position(11, 1),
        initial_obstacles=(),
        initial_zones=(
            ZoneDefinition(
                zone_type=ZoneType.SLOW,
                cells=(Position(5, 1), Position(6, 1)),
                extra_cost=5.0,
            ),
        ),
        max_ticks=60,
        scheduled_events={},
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled", "max_ticks"),
            min_moves=1,
        ),
    )
