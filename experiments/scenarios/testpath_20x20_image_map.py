from core.domain import AddObstacle, AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
    ZoneDefinition,
)


def build() -> ScenarioDefinition:
    return ScenarioDefinition(
        name="testpath_20x20_image_map",
        policy_name="event_based",
        world_config=WorldConfig(width=20, height=20),
        start=Position(3, 19),
        goal=Position(12, 0),
        initial_obstacles=(
            Position(3, 0),
            Position(7, 0),
            Position(13, 0),
            Position(7, 1),
            Position(7, 2),
            Position(13, 2),
            Position(17, 2),
            Position(7, 3),
            Position(19, 3),
            Position(3, 4),
            Position(4, 5),
            Position(19, 5),
            Position(5, 6),
            Position(14, 6),
            Position(6, 7),
            Position(10, 7),
            Position(13, 7),
            Position(6, 8),
            Position(11, 8),
            Position(0, 9),
            Position(1, 9),
            Position(2, 9),
            Position(7, 9),
            Position(3, 10),
            Position(8, 10),
            Position(4, 11),
            Position(15, 11),
            Position(16, 12),
            Position(17, 13),
            Position(7, 14),
            Position(13, 14),
            Position(19, 14),
            Position(4, 15),
            Position(8, 15),
            Position(14, 15),
            Position(5, 16),
            Position(14, 16),
            Position(6, 17),
            Position(14, 17),
            Position(12, 18),
            Position(13, 18),
            Position(12, 19),
        ),
        initial_zones=(
            ZoneDefinition(
                zone_type=ZoneType.SLOW,
                cells=(Position(3, 1), Position(3, 2), Position(3, 3)),
                extra_cost=3.0,
            ),
            ZoneDefinition(
                zone_type=ZoneType.SLOW, cells=(Position(7, 4),), extra_cost=3.0
            ),
            ZoneDefinition(
                zone_type=ZoneType.SLOW,
                cells=(Position(9, 5), Position(10, 6)),
                extra_cost=3.0,
            ),
            ZoneDefinition(
                zone_type=ZoneType.SLOW,
                cells=(
                    Position(15, 5),
                    Position(16, 5),
                    Position(17, 5),
                    Position(18, 5),
                ),
                extra_cost=3.0,
            ),
            ZoneDefinition(
                zone_type=ZoneType.SLOW,
                cells=(Position(14, 2), Position(15, 2), Position(16, 2)),
                extra_cost=3.0,
            ),
            ZoneDefinition(
                zone_type=ZoneType.SLOW,
                cells=(Position(3, 8), Position(4, 8), Position(5, 8)),
                extra_cost=3.0,
            ),
            ZoneDefinition(
                zone_type=ZoneType.SLOW,
                cells=(Position(10, 11), Position(11, 12), Position(12, 13)),
                extra_cost=3.0,
            ),
            ZoneDefinition(
                zone_type=ZoneType.SLOW,
                cells=(Position(10, 16), Position(11, 17)),
                extra_cost=3.0,
            ),
        ),
        max_ticks=400,
        scheduled_events={
            8: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=(Position(14, 1), Position(15, 1), Position(16, 1)),
                    duration_ticks=8,
                    extra_cost=5.0,
                ),
            ),
            9: (AddObstacle(position=Position(15, 2)),),
        },
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled", "max_ticks"),
            min_moves=0,
            min_replans=1,
        ),
    )
