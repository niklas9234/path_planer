from core.domain import Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
  return ScenarioDefinition(
    name="long_slow_zone_corridor",
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
            AddZone(
                zone_type=ZoneType.SLOW,
                cells=tuple(
                    Position(x, y)
                    for x in range(14, 17)
                    for y in range(6, 11)
                ),
                duration_ticks=200,
                extra_cost=10.0,
            ),
        ),
    },
    expectation=ScenarioExpectation(
        allowed_reasons=("goal_reached",),
        min_replans=1,
    ),
)
