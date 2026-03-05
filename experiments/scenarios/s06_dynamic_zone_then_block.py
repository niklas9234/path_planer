from core.domain import AddObstacle, AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="s06_dynamic_zone_then_block",
        policy_name="event_based",
        world_config=WorldConfig(width=12, height=4),
        start=Position(0, 1),
        goal=Position(11, 1),
        initial_obstacles=(),
        initial_zones=(),
        max_ticks=100,
        scheduled_events={
            2: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=(Position(4, 1), Position(5, 1), Position(6, 1)),
                    duration_ticks=6,
                    extra_cost=10.0,
                ),
            ),
            4: (AddObstacle(position=Position(7, 1)),),
        },
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled", "max_ticks"),
            min_replans=1,
        ),
    )
