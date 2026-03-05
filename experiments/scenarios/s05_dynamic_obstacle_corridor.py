from core.domain import AddObstacle, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
    ZoneDefinition,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="05_dynamic_obstacle_corridor",
        policy_name="event_based",
        world_config=WorldConfig(width=12, height=3),
        start=Position(0, 1),
        goal=Position(11, 1),
        initial_obstacles=(),
        initial_zones=(
            ZoneDefinition(
                zone_type=ZoneType.SLOW,
                cells=(Position(4, 0), Position(5, 0), Position(6, 0)),
                extra_cost=3.0,
            ),
        ),
        max_ticks=80,
        scheduled_events={
            3: (AddObstacle(position=Position(6, 1)),),
        },
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled", "max_ticks"),
            min_replans=1,
        ),
    )
