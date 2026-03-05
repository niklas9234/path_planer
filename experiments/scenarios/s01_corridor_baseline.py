from core.domain import Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="s01_corridor_baseline",
        policy_name="event_based",
        world_config=WorldConfig(width=12, height=3),
        start=Position(0, 1),
        goal=Position(11, 1),
        initial_obstacles=(),
        initial_zones=(),
        max_ticks=60,
        scheduled_events={},
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled", "max_ticks"),
            min_moves=1,
        ),
    )
