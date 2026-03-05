from core.domain import AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="temporary_slow_zone_expires",
        policy_name="event_based",
        world_config=WorldConfig(width=6, height=3),
        start=Position(0, 1),
        goal=Position(5, 1),
        initial_obstacles=(),
        initial_zones=(),
        max_ticks=20,
        scheduled_events={
            0: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=(Position(1, 1), Position(2, 1)),
                    duration_ticks=2,
                    extra_cost=3.0,
                ),
            ),
        },
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached",),
            min_replans=1,
        ),
    )
