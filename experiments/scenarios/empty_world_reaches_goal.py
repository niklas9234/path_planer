from core.domain import Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="empty_world_reaches_goal",
        policy_name="event_based",
        world_config=WorldConfig(width=5, height=5),
        start=Position(0, 0),
        goal=Position(4, 4),
        initial_obstacles=(),
        initial_zones=(),
        max_ticks=20,
        scheduled_events={},
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached",),
            min_moves=1,
        ),
    )
