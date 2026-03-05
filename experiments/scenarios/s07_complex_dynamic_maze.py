from __future__ import annotations

from core.domain import AddObstacle, AddZone, Position, ZoneType
from core.experiments.scenarios import (
    ScenarioDefinition,
    ScenarioExpectation,
    WorldConfig,
)


def _wall_with_doors(x: int, height: int, doors_y: tuple[int, ...]) -> tuple[Position, ...]:
    """Vertical wall at x with openings at specified y positions."""
    return tuple(Position(x, y) for y in range(height) if y not in doors_y)


def _cluster_3x3(cx: int, cy: int) -> tuple[Position, ...]:
    """3x3 zone cluster centered around (cx, cy)."""
    return tuple(
        Position(x, y)
        for x in range(cx - 1, cx + 2)
        for y in range(cy - 1, cy + 2)
        if 0 <= x < 30 and 0 <= y < 30
    )


def build() -> ScenarioDefinition:
    width = 30
    height = 30

    # Three vertical walls that create multiple alternative routes (three "doors" each).
    wall1 = _wall_with_doors(8, height, doors_y=(5, 15, 25))
    wall2 = _wall_with_doors(15, height, doors_y=(7, 17, 27))
    wall3 = _wall_with_doors(22, height, doors_y=(4, 14, 24))

    initial_obstacles = wall1 + wall2 + wall3

    # Dynamic slow-zones target the door areas (high leverage spots),
    # ensuring they actually affect the chosen path.
    slow_zone_mid_doors = (
        _cluster_3x3(8, 15) +   # wall1 middle door
        _cluster_3x3(15, 17) +  # wall2 middle-ish door
        _cluster_3x3(22, 14)    # wall3 middle-ish door
    )

    slow_zone_top_doors = (
        _cluster_3x3(8, 5) +    # wall1 top door
        _cluster_3x3(15, 7) +   # wall2 top-ish door
        _cluster_3x3(22, 4)     # wall3 top door
    )

    slow_zone_bottom_doors = (
        _cluster_3x3(8, 25) +   # wall1 bottom door
        _cluster_3x3(15, 27) +  # wall2 bottom door
        _cluster_3x3(22, 24)    # wall3 bottom door
    )

    return ScenarioDefinition(
        name="s07_complex_dynamic_maze",
        policy_name="event_based",  # default; CLI/matrix overrides per policy
        world_config=WorldConfig(width=width, height=height),
        start=Position(2, 2),
        goal=Position(27, 27),
        initial_obstacles=initial_obstacles,
        initial_zones=(),
        max_ticks=800,
        scheduled_events={
            # Long-lasting "middle route becomes expensive"
            20: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=slow_zone_mid_doors,
                    duration_ticks=220,
                    extra_cost=10.0,
                ),
            ),

            # Medium "top route becomes expensive" (shorter TTL)
            90: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=slow_zone_top_doors,
                    duration_ticks=120,
                    extra_cost=10.0,
                ),
            ),

            # Short "bottom route becomes expensive"
            170: (
                AddZone(
                    zone_type=ZoneType.SLOW,
                    cells=slow_zone_bottom_doors,
                    duration_ticks=60,
                    extra_cost=10.0,
                ),
            ),

            # Hard obstacle: close a door late to force replanning for adaptive policies,
            # and to make static_once likely fail if it committed to this door.
            # This targets a critical chokepoint (wall2 top-ish door).
            260: (
                AddObstacle(position=Position(15, 7)),
            ),
        },
        expectation=ScenarioExpectation(
            allowed_reasons=("goal_reached", "stalled", "max_ticks"),
            min_replans=1,
        ),
    )