from core.domain import AddObstacle, Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="replan_after_obstacle",
        policy_name="event_based",
        world_config=WorldConfig(width=5, height=3),
        start=Position(0, 0),
        goal=Position(4, 0),
        initial_obstacles=(),
        initial_zones=(),
        max_ticks=20,
        scheduled_events={1: (AddObstacle(position=Position(2, 0)),)},
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled"),
            min_replans=1,
        ),
    )
