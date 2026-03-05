from core.domain import Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="s02_corridor_static",
        policy_name="event_based",
        world_config=WorldConfig(width=12, height=4),
        start=Position(0, 1),
        goal=Position(11, 1),
        initial_obstacles=(
            Position(4, 1),
            Position(5, 1),
            Position(6, 1),
            Position(7, 1),
        ),
        initial_zones=(),
        max_ticks=80,
        scheduled_events={},
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled", "max_ticks"),
            min_moves=1,
        ),
    )
