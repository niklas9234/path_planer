from core.domain import Position
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="max_ticks_guard",
        policy_name="event_based",
        world_config=WorldConfig(width=5, height=5),
        start=Position(0, 0),
        goal=Position(4, 4),
        initial_obstacles=(),
        initial_zones=(),
        max_ticks=1,
        scheduled_events={},
        expectation=ScenarioExpectation(
            allowed_reasons=("max_ticks",),
        ),
    )
