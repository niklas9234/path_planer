from core.domain import Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="blocked_goal_stalls",
        policy_name="event_based",
        world_config=WorldConfig(width=3, height=3),
        start=Position(0, 0),
        goal=Position(2, 2),
        initial_obstacles=(
            Position(1, 1),
            Position(1, 0),
            Position(0, 1),
        ),
        initial_zones=(),
        max_ticks=10,
        scheduled_events={},
        expectation=ScenarioExpectation(
            allowed_reasons=("stalled",),
            min_moves=0,
            max_moves=0,
        ),
    )
