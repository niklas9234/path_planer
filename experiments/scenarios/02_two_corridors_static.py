from core.domain import Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
  return ScenarioDefinition(
    name="two_corridors_static",
    policy_name="event_based",
    world_config=WorldConfig(width=30, height=30),
    start=Position(2, 15),
    goal=Position(27, 15),
    initial_obstacles=tuple(
        Position(15, y) for y in range(30) if y not in (8, 22)
    ),
    initial_zones=(),
    max_ticks=400,
    scheduled_events={},
    expectation=ScenarioExpectation(
        allowed_reasons=("goal_reached",),
        min_moves=1,
    ),
)
