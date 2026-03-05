from core.domain import Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
  return ScenarioDefinition(
    name="dynamic_obstacle_corridor",
    policy_name="event_based",
    world_config=WorldConfig(width=30, height=30),
    start=Position(2, 15),
    goal=Position(27, 15),
    initial_obstacles=tuple(
        Position(15, y) for y in range(30) if y not in (8, 22)
    ),
    initial_zones=(),
    max_ticks=400,
    scheduled_events={
        20: (
            AddObstacle(position=Position(15, 8)),
        ),
    },
    expectation=ScenarioExpectation(
        allowed_reasons=("goal_reached", "stalled"),
        min_replans=1,
    ),
)