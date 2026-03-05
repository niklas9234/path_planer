from core.domain import Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
  return ScenarioDefinition(
    name="baseline_empty_world_30",
    policy_name="event_based",
    world_config=WorldConfig(width=30, height=30),
    start=Position(2, 2),
    goal=Position(27, 27),
    initial_obstacles=(),
    initial_zones=(),
    max_ticks=400,
    scheduled_events={},
    expectation=ScenarioExpectation(
        allowed_reasons=("goal_reached",),
        min_moves=1,
    ),
)
